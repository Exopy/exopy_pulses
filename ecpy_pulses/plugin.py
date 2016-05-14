# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""
"""

from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


import os
import logging
import enaml
from traceback import format_exc
from importlib import import_module
from atom.api import (Dict, List, Unicode, Typed, ForwardTyped, Tuple)

from watchdog.observers import Observer
from inspect import cleandoc

from ecpy.utils.plugin_tools import (HasPreferencesPlugin, ExtensionsCollector,
                                     DeclaratorsCollector)
from ecpy.utils.watchdog import SystematicFileUpdater
from .pulse import Pulse
from .sequences.base_sequences import BaseSequence, RootSequence
from .filters.base_filters import ItemFilter
from .utils.sequences_io import load_sequence_prefs
with enaml.imports():
    from .pulse_view import PulseView
    from .sequences.views.abstract_sequence_view import AbstractSequenceView
    from .sequences.views.base_sequence_view import (BaseSequenceView,
                                                     RootSequenceView)

from .declarations import (Sequence, Sequences, SequenceConfig, 
                           SequenceConfigs, Contexts, Context, Shapes, Shape)
from .infos import SequenceInfos, PulseInfos
from .sequences.template_sequence import TemplateSequence
from .sequences.views.template_view import TemplateSequenceView



PACKAGE_PATH = os.path.dirname(__file__)

TEMPLATE_PATH = os.path.realpath(os.path.join(PACKAGE_PATH, 'templates'))

FILTERS_POINT = 'ecpy.pulses.filters'
SEQUENCES_POINT = 'ecpy.pulses.sequences'
CONFIGS_POINT = 'ecpy.pulses.configs'
CONTEXTS_POINT = 'ecpy.pulses.contexts'
SHAPES_POINT = 'ecpy.pulses.shapes'

MODULE_ANCHOR = 'ecpy_pulses'


def workspace_state():
    from .workspace.workspace import SequenceEditionSpaceState
    return SequenceEditionSpaceState


def workspace():
    from .workspace.workspace import SequenceEditionSpace
    return SequenceEditionSpace


class PulsesManagerPlugin(HasPreferencesPlugin):
    """Plugin responsible for managing pulses.
    """
    #: Folders containings templates which should be loaded.
    templates_folders = List(default=[TEMPLATE_PATH]).tag(pref=True)

    #: List of all known sequences and template-sequences.
    sequences = List(Unicode())

    #: List of all known contexts
    contexts = List(Unicode())

    #: List of all known shape.
    shapes = List(Unicode())

    #: List of all known filters:
    filters = List()

    #: Reference to the workspace or None if the workspace is not active.
    workspace = ForwardTyped(workspace)

    #: Reference to the workspace state.
    workspace_state = ForwardTyped(workspace_state)

    def start(self):
        """ Start the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        super(PulsesManagerPlugin, self).start()

        if not os.path.isdir(TEMPLATE_PATH):
            try:
                os.mkdir(TEMPLATE_PATH)
            except Exception:
                if TEMPLATE_PATH in self.templates_folders:
                    self.templates_folders.remove(TEMPLATE_PATH)
                core = self.workbench.get_plugin('enaml.workbench.core')
                msg = 'Failed to create template folder.'
                # Python 2 windows issue
                try:
                    msg += 'Traceback : %s' % format_exc()
                except UnicodeError:
                    msg += 'Failed to format error message.'
                core.invoke_command('ecpy.app.errors.signal',
                                    dict(kind='error',
                                         message=msg))

        #: Start the Declarators and Extensions collectors to collect
        #: all elements of the plugin that are declared through enaml
        #: declarations
        self._filters = ExtensionsCollector(workbench=self.workbench,
                                            point=FILTERS_POINT,
                                            ext_class=ItemFilter)
        self._filters.start()
        print("Collected Filters:")
        print(self._filters.contributions)

        self._configs = DeclaratorsCollector(workbench=self.workbench,
                                             point=CONFIGS_POINT,
                                             ext_class=(SequenceConfig,
                                                        SequenceConfigs))
        self._configs.start()

        self._sequences = DeclaratorsCollector(workbench=self.workbench,
                                               point=SEQUENCES_POINT,
                                               ext_class=(Sequences, Sequence))
        self._sequences.start()

        self._contexts = DeclaratorsCollector(workbench=self.workbench,
                                              point=CONTEXTS_POINT,
                                              ext_class=(Contexts, Context))
        self._contexts.start()

        self._shapes = DeclaratorsCollector(workbench=self.workbench,
                                            point=SHAPES_POINT,
                                            ext_class=(Shapes, Shape))
        self._shapes.start()

        self.contexts = list(self._contexts.contributions.keys())
        self.filters = list(self._filters.contributions.keys())
        self.shapes = list(self._shapes.contributions.keys())

        #: Last step: refresh template sequences from the template folder
        #: and start observing that folder so that we will refresh it again
        #: if a file will be added.
        self._refresh_template_sequences_data()

        #: Populate the Pulse Info Object
        self._pulse_info = PulseInfos()
        self._pulse_info.cls = Pulse
        self._pulse_info.view = PulseView

        self._bind_observers()

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        super(PulsesManagerPlugin, self).stop()
        self._unbind_observers()
        self._template_sequences_data.clear()

        #: Stop all Extension/DeclaratorCollectors
        self._filters.stop()
        self._configs.stop()
        self._sequences.stop()
        self._contexts.stop()
        self._shapes.stop()

    def get_sequences_infos(self, sequences, use_class_names=False):
        """ Give access to sequence infos.

        Parameters
        ----------
        sequences : list(str)
            The names of the requested sequences.
        use_class_names : bool, optional
            Should the search be performed using class names rather than
            sequence names.
        views : bool
            When false views are not returned alongside the class.

        Returns
        -------
        sequences : dict
            The required sequences infos as a dict. For Python sequences the
            entry will contain the class and the view ({name: (class, view)}).
            If use_class_names is True the class name will be used.
            For templates the entry will contain the path, the data as a
            ConfigObj object and the doc ({name : (path, data, doc)})

        missings : list
            List of the sequences which were not found.

        """

        answer = {}
        if not use_class_names:
            missing_py = set([name for name in sequences
                              if name not in
                              self._sequences.contributions.keys()])
            missing_temp = set([name for name in sequences
                                if name not in
                                self._template_sequences_data.keys()])
            missing = list(set.intersection(missing_py, missing_temp))

            answer.update({key: val for key, val in
                           self._sequences.contributions.items()
                           if key in sequences})

            # TODO Return InfoObject
            templ = {key: val for key, val in
                     self._template_sequences_data.items()
                     if key in sequences}

            for _, t_info in templ:
                prefs = load_sequence_prefs(t_info.metadata['path'])
                t_info.metadata.update(prefs)

            answer.update(templ)

        else:
            class_names = {val.cls.__name__: val
                           for val in self._sequences.contributions.values()}

            missing = [name for name in sequences
                       if name not in class_names]

            answer.update({key: val for key, val in class_names.items()
                           if key in sequences})

        return answer, missing

    def get_sequence_info(self, sequence, use_class_names=False):
        """Access a given sequence infos.

        Parameters
        ----------
        sequence : unicode
            Id of the sequence class for which to return the actual class.

        Returns
        -------
        infos : SequenceInfos or None
            Object containing all the infos about the requested sequence.
            This object should never be manipulated directly by user code.

        """
        sequences = [sequence]
        _answer, _missing = self.get_sequences_infos(sequences,
                                                     use_class_names)

        try:
            answer = _answer[sequence]
            missing = None
        except KeyError:
            answer = None
            missing = [sequence]
        return answer, missing

    def get_sequences(self, sequences, use_class_names=False):
        """Access a given sequence class.

        Parameters
        ----------
        sequence : unicode
            Id of the sequence class for which to return the actual class.

        view : bool, optional
            Whether or not to return the view assoicated with the sequence.

        Returns
        -------
        task_cls : type or None
            Class associated to the requested sequence or None if the sequence
            was not found.

        task_view : EnamlDefMeta or None, optional
            Associated view if requested.

        """
        _answer, _missing = self.get_sequences_infos(sequences,
                                                     use_class_names)
        answer = {key: (val.cls, val.view) for key, val in _answer}

        for key, val in _answer:
            answer = {key, val}

        return answer, _missing

    def get_sequence(self, sequence, use_class_names=False):
        """Access a given sequence class.

        Parameters
        ----------
        sequence : unicode
            Id of the sequence class for which to return the actual class.

        view : bool, optional
            Whether or not to return the view assoicated with the sequence.

        Returns
        -------
        task_cls : type or None
            Class associated to the requested sequence or None if the sequence
            was not found.

        task_view : EnamlDefMeta or None, optional
            Associated view if requested.

        """
        _answer, _missing = self.get_sequence_info(sequence, use_class_names)

        if _answer is None:
            return (None, None)

        return (_answer.cls, _answer.view)

    def get_items_infos(self, items, use_class_names=False):
        print("Get Item Infos: " + str(items))
        _answer, _missing = self.get_sequences_infos(items, use_class_names)

        additional_items = {}
        # additional_items = {key:_pulse_info for key in
        #                    _missing if _missing is "Pulse"}

        missing = []

        for el in _missing:
            if el == "Pulse":
                additional_items[el] = self._pulse_info
            elif el == "__template__":
                print("MISSING CASE")
            else:
                missing.append(el)

        _answer.update(additional_items)

        return _answer, missing

    def get_contexts_infos(self, contexts, use_class_names=False):
        """ Give access to context infos.

        Parameters
        ----------
        contexts : list(str)
            The names of the requested contexts.
        use_class_names : bool, optional
            Should the search be performed using class names rather than
            context names.

        Returns
        -------
        contexts : dict
            The required contexts infos as a dict {name: (class, view)}.
            If use_class_names is True the class name will be used.

        """
        if type(contexts) is not list:
            raise ValueError("plugin.py:get_contexts_infos" +
                             " - contexts should be a list")

        answer = {}

        if not use_class_names:
            missing = [name for name in contexts
                       if name not in self._contexts.contributions.keys()]
            answer.update({key: val for key, val in
                           self._contexts.contributions.items()
                           if key in contexts})

        else:
            class_names = {val.cls.__name__: val
                           for val in self._contexts.contributions.values()}
            missing = [name for name in contexts
                       if name not in class_names]

            answer.update({key: val for key, val in
                           class_names.items() if key in contexts})

        return answer, missing

    def get_context_info(self, context, use_class_names=False):
        """ Give access to context infos.

        Parameters
        ----------
        contexts : list(str)
            The names of the requested contexts.
        use_class_names : bool, optional
            Should the search be performed using class names rather than
            context names.

        Returns
        -------
        contexts : dict
            The required contexts infos as a dict {name: (class, view)}.
            If use_class_names is True the class name will be used.

        """
        contexts = [context]
        _answer, _missing = self.get_contexts_infos(contexts, use_class_names)

        try:
            answer = _answer[context]
            missing = None
        except KeyError:
            answer = None
            missing = context
        return answer, missing

    def get_shapes_infos(self, shapes, use_class_names=False):
        """ Give access to shape infos.

        Parameters
        ----------
        shapes : list(str)
            The names of the requested shapes.
        use_class_names : bool, optional
            Should the search be performed using class names rather than
            context names.
        views : bool
            When flase views are not returned alongside the class.

        Returns
        -------
        shapes : dict
            The required shapes infos as a dict {name: (class, view)}.
            If use_class_names is True the class name will be used.

        """
        answer = {}

        if not use_class_names:
            missing = [name for name in shapes
                       if name not in self._shapes.contributions.keys()]

            answer.update({key: val for key, val
                           in self._shapes.contributions.items()
                           if key in shapes})

        else:
            class_names = {val.cls.__name__: val
                           for val in self._shapes.contributions.values()}

            missing = [name for name in shapes
                       if name not in class_names]

            answer.update({key: val for key, val in class_names.items()
                           if key in shapes})

        return answer, missing

    def get_config(self, sequence_id):
        """ Access the proper config for a sequence.

        Parameters
        ----------
        sequence : str
            Name of the sequnce for which a config is required

        Returns
        -------
        config : tuple
            Tuple containing the config object requested, and its visualisation

        """
        templates = self._template_sequences_data
        if sequence_id in templates:
            config_infos = self._config.contributions['__template__']
            conf = config_infos.cls
            view = config_infos.view
            t_config, t_doc = load_sequence_prefs(templates[sequence_id])
            return conf(manager=self, config=t_config, doc=t_doc), view

        elif sequence_id in self._sequences.contributions:
            configs = self._configs.contributions
            # Look up the hierarchy of the selected sequence to get the
            # appropriate SequenceConfig
            sequence_class = self._sequences.contributions[sequence_id].cls
            for i_class in type.mro(sequence_class):
                if i_class in configs:
                    config = configs[i_class].cls
                    view = configs[i_class].view
                    return config(manager=self,
                                  sequence_class=sequence_class), view
        return None, None

    def filter_sequences(self, filter_name):
        """ Filter the known sequences using the specified filter.

        Parameters
        ----------
        filter_name : str
            Name of the filter to use

        Returns
        -------
        sequences : list(str) or None
            Sequences selected by the filter, or None if the filter does not
            exist.

        """

        s_filter = self._filters.contributions.get(filter_name)
        if s_filter:
            # Remove items that should not be shown in the list
            sequences = self._sequences.contributions.copy()
            template_sequences_data = self._template_sequences_data.copy() #TODO To contribution

            try:
                template_sequences_data.pop('Pulse')
                template_sequences_data.pop('RootSequence')
            except KeyError:
                pass
            print(sequences)
            print(template_sequences_data)
            return s_filter.filter_items(sequences,
                                         template_sequences_data)
        else:
            logger = logging.getLogger(__name__)
            logger.warn("Did not find the filter " + str(filter_name) +
                        " and returned zero elements.")
            return []


    def report(self):
        """ Give access to the failures which happened at startup.

        """
        return self._failed

    # --- Private API ---------------------------------------------------------

    #: Sequences implemented in Python
    _sequences = Typed(DeclaratorsCollector)

    #: Template sequences (store full path to .ini)
    _template_sequences_data = Dict(Unicode(), Unicode())

    #: Template sequences infos
    _template_sequences_infos = Dict(Unicode(), SequenceInfos)

    #: Info Object for Pulse
    _pulse_info = Typed(PulseInfos)

    #: Sequence contexts.
    _contexts = Typed(DeclaratorsCollector)

    #: Task config dict for python tasks (task_class: (config, view))
    _shapes = Typed(DeclaratorsCollector)

    #: Contributed task filters.
    _filters = Typed(ExtensionsCollector)

    #: Configuration object used to insert new sequences in existing ones.
    _configs = Typed(DeclaratorsCollector)

    # Dict holding the list of failures which happened during loading
    _failed = Dict()

    # Watchdog observer
    _observer = Typed(Observer, ())

    def _refresh_template_sequences_data(self):
        """ Refresh the known template sequences.

        """
        templates = {}
        for path in self.templates_folders:
            if os.path.isdir(path):
                filenames = sorted(f for f in os.listdir(path)
                                   if (os.path.isfile(os.path.join(path, f))
                                       and f.endswith('.ini')))
                for filename in filenames:
                    template_name = self._normalise_name(filename)
                    template_path = os.path.join(path, filename)
                    # Beware redundant names are overwrited
                    templates[template_name] = template_path
            else:
                logger = logging.getLogger(__name__)
                logger.warn('{} is not a valid directory'.format(path))

        self._template_sequences_data = templates
        aux = (list(self._sequences.contributions.keys()) +
               list(templates.keys()))

        self.sequences = aux


    def _refresh_template_sequences_infos(self):
        """ Refresh the known template sequence infos.

        """
        # TODO Should be more proper in case of update

        templates = self._template_sequences_data
        templates_infos = {}

        for template_name, template_path in templates:

            metadata = {'is_template': True, 'path': template_path}
            infos = SequenceInfos(metadata=metadata)
            infos.cls = TemplateSequence
            infos.view = TemplateSequenceView
            templates_infos[template_name] = infos

        self._template_sequences_infos = templates_infos





    def _update_filters(self, change):
        """ Place holder for a future filter discovery function

        """
        self.filters = list(change['value'].keys())

#    def _refresh_config(self):
#        """ Place holder for a future config discovery function
#
#        """
#        mapping = {}
#        for key, val in SEQUENCE_CONFIG.items():
#            mapping[key] = (val, CONFIG_MAP_VIEW[val])
#
#        self._configs = mapping

    def _explore_package(self, pack, pack_path, failed, exceptions):
        """ Explore a package.

        Parameters
        ----------
        pack : str
            The package name relative to the packages pulses.
            (ex : sequences)

        pack_path : unicode
            Path of the package to explore

        failed : dict
            A dict in which failed imports will be stored.

        exceptions: list
            Names of the modules which should not be loaded.

        Returns
        -------
        modules : list
            List of string indicating modules which can be imported

        v_modules : list
            List of string indicating enaml modules which can be imported

        """
        if not os.path.isdir(pack_path):
            log = logging.getLogger(__name__)
            mess = '{} is not a valid directory.({})'.format(pack,
                                                             pack_path)
            log.error(mess)
            failed[pack] = mess
            return [], []

        modules = sorted(pack + '.' + m[:-3] for m in os.listdir(pack_path)
                         if (os.path.isfile(os.path.join(pack_path, m)) and
                             m.endswith('.py')))

        try:
            modules.remove(pack + '.__init__')
        except ValueError:
            log = logging.getLogger(__name__)
            mess = cleandoc('''{} is not a valid Python package (miss
                __init__.py).'''.format(pack))
            log.error(mess)
            failed[pack] = mess
            return [], []

        # Remove modules which should not be imported
        for mod in modules[:]:
            if mod in exceptions:
                modules.remove(mod)

        # Look for enaml definitions
        v_path = os.path.join(pack_path, 'views')
        if not os.path.isdir(v_path):
            log = logging.getLogger(__name__)
            mess = '{}.views is not a valid directory.({})'.format(pack,
                                                                   v_path)
            log.error(mess)
            failed[pack] = mess
            return [], []

        v_modules = sorted(pack + '.views.' + m[:-6]
                           for m in os.listdir(v_path)
                           if (os.path.isfile(os.path.join(v_path, m)) and
                               m.endswith('.enaml')))

        if not os.path.isfile(os.path.join(pack_path, '__init__.py')):
            log = logging.getLogger(__name__)
            mess = cleandoc('''{} is not a valid Python package (miss
                __init__.py).'''.format(pack + '.views'))
            log.error(mess)
            failed[pack] = mess
            return [], []

        for mod in v_modules[:]:
            if mod in exceptions:
                v_modules.remove(mod)

        return modules, v_modules

    def _explore_modules(self, modules, founds, mod_var, failed):
        """ Explore a list of modules, looking for tasks.

        Parameters
        ----------
        modules : list
            The list of modules to explore

        found : dict
            A dict in which discovered objects will be stored.

        mod_var : str
            Name of the module variable to look for.

        failed : list
            A dict in which failed imports will be stored.

        """
        for mod in modules:
            try:
                m = import_module('.' + mod, MODULE_ANCHOR)
            except Exception as e:
                log = logging.getLogger(__name__)
                mess = 'Failed to import {} : {}'.format(mod, e)
                log.error(mess)
                failed[mod] = mess
                continue

            if hasattr(m, mod_var):
                var = getattr(m, mod_var)
                if isinstance(var, list):
                    founds.update({self._normalise_name(found.__name__): found
                                  for found in var})
                else:
                    founds.update(var)

    def _explore_views(self, modules, views, mod_var, failed):
        """ Explore a list of modules, looking for views.

        Parameters
        ----------
        modules : list
            The list of modules to explore

        views : dict
            A dict in which discovered views will be stored.

        mod_var : str
            Name of the module variable to look for.

        failed : list
            A list in which failed imports will be stored.

        """
        for mod in modules:
            try:
                with enaml.imports():
                    m = import_module('.' + mod, MODULE_ANCHOR)
            except Exception as e:
                log = logging.getLogger(__name__)
                mess = 'Failed to import {} : {}'.format(mod, e)
                log.error(mess)
                failed[mod] = mess
                continue

            if hasattr(m, mod_var):
                views.update(getattr(m, mod_var))

    def _bind_observers(self):
        """ Setup the observers for the plugin.

        """

        for folder in self.templates_folders:
            handler = SystematicFileUpdater(self._refresh_template_sequences_data)
            self._observer.schedule(handler, folder, recursive=True)

        self._observer.start()

        self.observe('templates_folders', self._update_templates)
        self._filters.observe('contributions', self._update_filters)

    def _unbind_observers(self):
        """ Remove the observers for the plugin.

        """
        self.unobserve('templates_folders', self._update_templates)
        self._filters.unobserve('contributions', self._update_filters)
        self._observer.unschedule_all()
        self._observer.stop()
        self._observer.join()

    def _update_templates(self, change):
        """ Observer ensuring that we observe the right template folders.

        """
        self._observer.unschedule_all()

        for folder in self.templates_folders:
            handler = SystematicFileUpdater(self._refresh_template_tasks)
            self._observer.schedule(handler, folder, recursive=True)

    @staticmethod
    def _normalise_name(name):
        """Normalize names by replacing '_' by spaces, removing the extension,
        and adding spaces between 'aA' sequences.

        """
        if name.endswith('.ini'):
            name = name[:-4] + '\0'
        elif name.endswith('Shape'):
            name = name[:-5] + '\0'
        else:
            name += '\0'
        aux = ''
        for i, char in enumerate(name):
            if char == '_':
                aux += ' '
                continue

            if char != '\0':
                if char.isupper() and i != 0:
                    if name[i-1].islower():
                        if name[i+1].islower():
                            aux += ' ' + char.lower()
                        else:
                            aux += ' ' + char
                    else:
                        if name[i+1].islower():
                            aux += ' ' + char.lower()
                        else:
                            aux += char
                else:
                    if i == 0:
                        aux += char.upper()
                    else:
                        aux += char
        return aux
