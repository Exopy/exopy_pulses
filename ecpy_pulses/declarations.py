# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Enaml objects used to declare sequences in a plugin manifest.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


from future.utils import python_2_unicode_compatible
from traceback import format_exc
from inspect import cleandoc

from atom.api import Unicode, Dict, Property
from enaml.core.api import d_, d_func

from ecpy.utils.declarator import (Declarator, GroupDeclarator, import_and_get)
from .infos import (SequenceInfos, ConfigInfos, ContextInfos, ShapeInfos)


class Sequences(GroupDeclarator):
    """ GroupDeclarator for Sequences.

    Sequences will be stored according to the group of their parent.

    """
    pass


@python_2_unicode_compatible
class Sequence(Declarator):
    """Declarator used to contribute a Sequence

    """
    #: path of the sequence object. Paths should be dot separed and the class
    #: name preceded by ':'.
    #: The path to any parent GroupDeclarator will be prepended to it.
    sequence = d_(Unicode())

    #: Path to the view object associated to the sequence.
    #: The path of any parent GroupDeclarator will be prepended.
    view = d_(Unicode())

    #: Metadata associated to the sequence.
    metadata = d_(Dict())

    #: Id of the sequence computed from the top-level package and the sequence
    #: name
    id = Property(cached=True)

    def register(self, collector, traceback):
        """Collect sequence and view and add infos to the DeclaratorCollector
        contributions member.

        The group declared by a parent if any is taken into account. All
        Interface children are also registered.

        """
        # Build the sequence id by assembling the package name and the class
        # name.
        sequence_id = self.id

        # If the sequence only specifies a name update the matching infos.
        if ':' not in self.sequence:
            if self.sequence not in collector.contributions:
                collector._delayed.append(self)
                return

            infos = collector.contributions[sequence_id]
            # TODO Check or Update something?

        # Determine the path of sequence and view
        path = self.get_path()
        try:
            s_path, sequence = (path + '.' + self.sequence
                                if path else self.sequence).split(':')
            v_path, view = (path + '.' + self.view
                            if path else self.view).split(':')
        except ValueError:
            msg = 'Incorrect %s (%s), path must be of the form a.b.c:Class'
            err_id = s_path.split('.', 1)[0] + '.' + sequence
            msg = msg % ('view', self.view)

            traceback[err_id] = msg
            return

        # Check that the sequence does not already exist.
        if sequence_id in collector.contributions or sequence_id in traceback:
            i = 1
            while True:
                err_id = '%s_duplicate%d' % (sequence_id, i)
                if err_id not in traceback:
                    break

            msg = 'Duplicate definition of {}, found in {}'
            traceback[err_id] = msg.format(sequence, s_path)
            return

        infos = SequenceInfos(metadata=self.metadata)

        # Get the sequence class.
        s_cls = import_and_get(s_path, sequence, traceback, sequence_id)
        if s_cls is None:
            return

        try:
            infos.cls = s_cls
        except TypeError:
            msg = '{} should be a subclass of AbstractSequence. \n{}'
            traceback[sequence_id] = msg.format(s_cls, format_exc())
            return

        # Get the sequence view.
        s_view = import_and_get(v_path, view, traceback, sequence_id)
        if s_view is None:
            return

        try:
            infos.view = s_view
        except TypeError:
            msg = '{} should be a subclass of AbstractSequenceView,.\n{}'
            traceback[sequence_id] = msg.format(s_view, format_exc())
            return

        # Add group and add to collector
        infos.metadata['group'] = self.get_group()
        collector.contributions[sequence_id] = infos

        # Register children.
        for i in self.children:
            i.register(collector, traceback)

        self.is_registered = True

    def unregister(self, collector):
        """Remove contributed infos from the collector.

        """
        if self.is_registered:
            # Unregister children.
            for i in self.children:
                i.unregister(collector)

            # If we were just extending the sequence, clean instruments.
            if ':' not in self.sequence:
                if self.sequence in collector.contributions:
                    infos = collector.contributions[self.sequence]
                return

            # Remove infos.
            try:
                # Unparent remaining interfaces
                infos = collector.contributions[self.id]
                for i in infos.interfaces.values():
                    i.parent = None

                del collector.contributions[self.id]
            except KeyError:
                pass

            self.is_registered = False

    def __str__(self):
        """Nice string representation giving attributes values.

        """
        msg = cleandoc('''{} with:
                       sequence: {}, view : {} and metadata: {} declaring :
                       {}''')
        return msg.format(type(self).__name__, self.sequence, self.view,
                          self.metadata,
                          '\n'.join(' - {}'.format(c) for c in self.children))

    def _get_id(self):
        """Create the unique identifier of the sequence using the top level
        package and the class name.

        """
        if ':' in self.sequence:
            path = self.get_path()
            s_path, sequence = (path + '.' + self.sequence
                                if path else self.sequence).split(':')

            # Build the sequence id by assembling the package name and the
            # class name
            return s_path.split('.', 1)[0] + '.' + sequence

        else:
            return self.sequence


class SequenceConfigs(GroupDeclarator):
    """GroupDeclarator for sequences configs.

    """
    pass


@python_2_unicode_compatible
class SequenceConfig(Declarator):
    """Declarator used to contribute a Sequence configurator

    """

    #: path of the config object. Paths should be dot separed and the class
    #: name preceded by ':'.
    #: The path to any parent GroupDeclarator will be prepended to it.
    config = d_(Unicode())

    #: Path to the view object associated to the sequence.
    #: The path of any parent GroupDeclarator will be prepended.
    view = d_(Unicode())

    #: Id of the sequence computed from the top-level package and the sequence
    #: name
    id = Property(cached=True)

    @d_func
    def get_sequence_class(self):
        """Return the base sequence class this config is used for.

        """
        raise NotImplementedError()

    def register(self, collector, traceback):
        """Collect config and view and add infos to the DeclaratorCollector
        contributions member under the supported task name.

        """
        # Determine the path of sequence and view
        path = self.get_path()
        try:
            c_path, config = (path + '.' + self.config
                              if path else self.config).split(':')
            v_path, view = (path + '.' + self.view
                            if path else self.view).split(':')
        except ValueError:
            msg = 'Incorrect %s (%s), path must be of the form a.b.c:Class'
            err_id = c_path.split('.', 1)[0] + '.' + config
            msg = msg % ('view', self.view)

            traceback[err_id] = msg
            return

        try:
            s_cls = self.get_sequence_class()
        except Exception:
            msg = 'Failed to get supported sequence : %s'
            traceback[self.id] = msg % format_exc()
            return

        # Check that the configurer does not already exist.
        if self.id in traceback:
            i = 1
            while True:
                err_id = '%s_duplicate%d' % (config, i)
                if err_id not in traceback:
                    break

            msg = 'Duplicate definition of {}, found in {}'
            traceback[err_id] = msg.format(s_cls, c_path)
            return

        if s_cls in collector.contributions:
            msg = 'Duplicate definition for {}, found in {}'
            traceback[self.id] = msg.format(s_cls, c_path)
            return

        infos = ConfigInfos()

        # Get the config class.
        c_cls = import_and_get(c_path, config, traceback, self.id)
        if c_cls is None:
            return

        try:
            infos.cls = c_cls
        except TypeError:
            msg = '{} should a subclass of AbstractConfig.\n{}'
            traceback[self.id] = msg.format(c_cls, format_exc())
            return

        # Get the config view.
        view = import_and_get(v_path, view, traceback, self.id)
        if view is None:
            return

        try:
            infos.view = view
        except TypeError:
            msg = '{} should a subclass of AbstractConfigView.\n{}'
            traceback[self.id] = msg.format(c_cls, format_exc())
            return

        collector.contributions[s_cls] = infos

        self.is_registered = True

    def unregister(self, collector):
        """Remove contributed infos from the collector.

        """
        if self.is_registered:
            try:
                del collector.contributions[self.get_sequence_class()]
            except KeyError:
                pass

            self.is_registered = False

    def __str__(self):
        """Nice string representation giving attributes values.

        """
        msg = cleandoc('''{} with:
                       config: {}, view : {}''')
        return msg.format(type(self).__name__, self.config, self.view)

    def _get_id(self):
        """Create the unique identifier of the config using the top level
        package and the class name.

        """
        if ':' in self.config:
            path = self.get_path()
            c_path, config = (path + '.' + self.config
                              if path else self.config).split(':')

            # Build the task id by assembling the package name and the class
            # name
            return c_path.split('.', 1)[0] + '.' + config

        else:
            return self.config


class Contexts(GroupDeclarator):
    """ GroupDeclarator for Contexts.

    Contexts will be stored according to the group of their parent.

    """
    pass


@python_2_unicode_compatible
class Context(Declarator):
    """Declarator used to contribute a Context

    """

    #: path of the context object. Paths should be dot separed and the class
    #: name preceded by ':'.
    #: The path to any parent GroupDeclarator will be prepended to it.
    context = d_(Unicode())

    #: Path to the view object associated to the context.
    #: The path of any parent GroupDeclarator will be prepended.
    view = d_(Unicode())

    #: Metadata associated to the context.
    metadata = d_(Dict())

    #: Id of the context computed from the top-level package and the context
    #: name
    id = Property(cached=True)

    def register(self, collector, traceback):
        """Collect context and view and add infos to the DeclaratorCollector
        contributions member.

        The group declared by a parent if any is taken into account. All
        Interface children are also registered.

        """
        # Build the context id by assembling the package name and the class
        # name.
        context_id = self.id

        # If the context only specifies a name update the matching infos.
        if ':' not in self.context:
            if self.context not in collector.contributions:
                collector._delayed.append(self)
                return

            infos = collector.contributions[context_id]
            # TODO Check or Update something?

        # Determine the path of context and view
        path = self.get_path()
        try:
            c_path, context = (path + '.' + self.context
                               if path else self.context).split(':')
            v_path, view = (path + '.' + self.view
                            if path else self.view).split(':')
        except ValueError:
            msg = 'Incorrect %s (%s), path must be of the form a.b.c:Class'
            err_id = c_path.split('.', 1)[0] + '.' + context
            msg = msg % ('view', self.view)

            traceback[err_id] = msg
            return

        # Check that the context does not already exist.
        if context_id in collector.contributions or context_id in traceback:
            i = 1
            while True:
                err_id = '%s_duplicate%d' % (context_id, i)
                if err_id not in traceback:
                    break

            msg = 'Duplicate definition of {}, found in {}'
            traceback[err_id] = msg.format(context, c_path)
            return

        infos = ContextInfos(metadata=self.metadata)

        # Get the sequence class.
        c_cls = import_and_get(c_path, context, traceback, context_id)
        if c_cls is None:
            return

        try:
            infos.cls = c_cls
        except TypeError:
            msg = '{} should be a subclass of BaseContext. \n{}'
            traceback[context_id] = msg.format(c_cls, format_exc())
            return

        # Get the context view.
        c_view = import_and_get(v_path, view, traceback, context_id)
        if c_view is None:
            return

        try:
            infos.view = c_view
        except TypeError:
            msg = '{} should be a subclass of BaseContextView,.\n{}'
            traceback[context_id] = msg.format(c_view, format_exc())
            return

        # Add group and add to collector
        infos.metadata['group'] = self.get_group()
        collector.contributions[context_id] = infos

        # Register children.
        for i in self.children:
            i.register(collector, traceback)

        self.is_registered = True

    def unregister(self, collector):
        """Remove contributed infos from the collector.

        """
        if self.is_registered:
            # Unregister children.
            for i in self.children:
                i.unregister(collector)

            # If we were just extending the context, clean instruments.
            if ':' not in self.context:
                if self.context in collector.contributions:
                    infos = collector.contributions[self.context]
                return

            # Remove infos.
            try:
                # Unparent remaining interfaces
                infos = collector.contributions[self.id]
                for i in infos.interfaces.values():
                    i.parent = None

                del collector.contributions[self.id]
            except KeyError:
                pass

            self.is_registered = False

    def __str__(self):
        """Nice string representation giving attributes values.

        """
        msg = cleandoc('''{} with:
                       context: {}, view : {} and metadata: {} declaring :
                       {}''')
        return msg.format(type(self).__name__, self.context, self.view,
                          self.metadata,
                          '\n'.join(' - {}'.format(c) for c in self.children))

    def _get_id(self):
        """Create the unique identifier of the context using the top level
        package and the class name.

        """
        if ':' in self.context:
            path = self.get_path()
            c_path, context = (path + '.' + self.context
                               if path else self.context).split(':')

            # Build the context id by assembling the package name and the
            # class name
            return c_path.split('.', 1)[0] + '.' + context

        else:
            return self.context


class Shapes(GroupDeclarator):
    """ GroupDeclarator for a group of Shapes.

    Shapes will be stored according to the group of their parent.

    """
    pass


@python_2_unicode_compatible
class Shape(Declarator):
    """Declarator used to contribute a Shape

    """

    #: path of the shape object. Paths should be dot separed and the class
    #: name preceded by ':'.
    #: The path to any parent GroupDeclarator will be prepended to it.
    shape = d_(Unicode())

    #: Path to the view object associated to the shape.
    #: The path of any parent GroupDeclarator will be prepended.
    view = d_(Unicode())

    #: Metadata associated to the shape.
    metadata = d_(Dict())

    #: Id of the shape computed from the top-level package and the shape
    #: name
    id = Property(cached=True)

    def register(self, collector, traceback):
        """Collect shape and view and add infos to the DeclaratorCollector
        contributions member.

        The group declared by a parent if any is taken into account. All
        Interface children are also registered.

        """
        # Build the shape id by assembling the package name and the class
        # name.
        shape_id = self.id

        # If the shape only specifies a name update the matching infos.
        if ':' not in self.shape:
            if self.shape not in collector.contributions:
                collector._delayed.append(self)
                return

            infos = collector.contributions[shape_id]
            # TODO Check or Update something?

        # Determine the path of shape and view
        path = self.get_path()
        try:
            s_path, shape = (path + '.' + self.shape
                             if path else self.shape).split(':')
            v_path, view = (path + '.' + self.view
                            if path else self.view).split(':')
        except ValueError:
            msg = 'Incorrect %s (%s), path must be of the form a.b.c:Class'
            err_id = s_path.split('.', 1)[0] + '.' + shape
            msg = msg % ('view', self.view)

            traceback[err_id] = msg
            return

        # Check that the shape does not already exist.
        if shape_id in collector.contributions or shape_id in traceback:
            i = 1
            while True:
                err_id = '%s_duplicate%d' % (shape_id, i)
                if err_id not in traceback:
                    break

            msg = 'Duplicate definition of {}, found in {}'
            traceback[err_id] = msg.format(shape, s_path)
            return

        infos = ShapeInfos(metadata=self.metadata)

        # Get the sequence class.
        s_cls = import_and_get(s_path, shape, traceback, shape_id)
        if s_cls is None:
            return

        try:
            infos.cls = s_cls
        except TypeError:
            msg = '{} should be a subclass of AbstractShape. \n{}'
            traceback[shape_id] = msg.format(s_cls, format_exc())
            return

        # Get the shape view.
        s_view = import_and_get(v_path, view, traceback, shape_id)
        if s_view is None:
            return

        try:
            infos.view = s_view
        except TypeError:
            msg = '{} should be a subclass of AbstractShapeView,.\n{}'
            traceback[shape_id] = msg.format(s_view, format_exc())
            return

        # Add group and add to collector
        infos.metadata['group'] = self.get_group()
        collector.contributions[shape_id] = infos

        # Register children.
        for i in self.children:
            i.register(collector, traceback)

        self.is_registered = True

    def unregister(self, collector):
        """Remove contributed infos from the collector.

        """
        if self.is_registered:
            # Unregister children.
            for i in self.children:
                i.unregister(collector)

            # If we were just extending the shape, clean instruments.
            if ':' not in self.shape:
                if self.shape in collector.contributions:
                    infos = collector.contributions[self.shape]
                return

            # Remove infos.
            try:
                # Unparent remaining interfaces
                infos = collector.contributions[self.id]
                for i in infos.interfaces.values():
                    i.parent = None

                del collector.contributions[self.id]
            except KeyError:
                pass

            self.is_registered = False

    def __str__(self):
        """Nice string representation giving attributes values.

        """
        msg = cleandoc('''{} with:
                       shape: {}, view : {} and metadata: {} declaring :
                       {}''')
        return msg.format(type(self).__name__, self.shape, self.view,
                          self.metadata,
                          '\n'.join(' - {}'.format(c) for c in self.children))

    def _get_id(self):
        """Create the unique identifier of the sequence using the top level
        package and the class name.

        """
        if ':' in self.shape:
            path = self.get_path()
            s_path, shape = (path + '.' + self.shape
                             if path else self.shape).split(':')

            # Build the shape id by assembling the package name and the
            # class name
            return s_path.split('.', 1)[0] + '.' + shape

        else:
            return self.shape
