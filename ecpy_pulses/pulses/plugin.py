# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Plugin centralizing the collection and management pulse sequences related
objects : sequences, shapes, configs, contexts

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import os
import logging
import enaml

from watchdog.observers import Observer
from atom.api import (Dict, List, Unicode, Typed, ForwardTyped)
from ecpy.utils.plugin_tools import (HasPreferencesPlugin, ExtensionsCollector,
                                     DeclaratorsCollector)
from ecpy.utils.watchdog import SystematicFileUpdater

from .pulse import Pulse
from .filters import SequenceFilter
from .utils.sequences_io import load_sequence_prefs
from .declarations import (Sequence, Sequences, SequenceConfig,
                           SequenceConfigs, Contexts, Context, Shapes, Shape)
from .shapes.modulation import Modulation
from .infos import SequenceInfos, PulseInfos
from .sequences.template_sequence import TemplateSequence

with enaml.imports():
    from .pulse_view import PulseView
    from .sequences.views.template_view import TemplateSequenceView


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
    templates_folders = List()  # .tag(pref=True)  # TODO harcoded currently

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
        core = self.workbench.get_plugin('enaml.workbench.core')
        core.invoke_command('ecpy.app.errors.enter_error_gathering')

        state = core.invoke_command('ecpy.app.states.get',
                                    {'state_id': 'ecpy.app.directory'})

        p_dir = os.path.join(state.app_directory, 'pulses')
        # Create pulses subfolder if it does not exist.
        if not os.path.isdir(p_dir):
            os.mkdir(p_dir)

        temp_dir = os.path.join(p_dir, 'templates')
        # Create templates subfolder if it does not exist.
        if not os.path.isdir(temp_dir):
            os.mkdir(temp_dir)

        self.templates_folders = [temp_dir]

        # Start the Declarators and Extensions collectors to collect
        # all elements of the plugin that are declared through enaml
        # declarations
        self._filters = ExtensionsCollector(workbench=self.workbench,
                                            point=FILTERS_POINT,
                                            ext_class=SequenceFilter)

        self._configs = DeclaratorsCollector(workbench=self.workbench,
                                             point=CONFIGS_POINT,
                                             ext_class=(SequenceConfig,
                                                        SequenceConfigs))

        self._sequences = DeclaratorsCollector(workbench=self.workbench,
                                               point=SEQUENCES_POINT,
                                               ext_class=(Sequences, Sequence))

        self._contexts = DeclaratorsCollector(workbench=self.workbench,
                                              point=CONTEXTS_POINT,
                                              ext_class=(Contexts, Context))

        self._shapes = DeclaratorsCollector(workbench=self.workbench,
                                            point=SHAPES_POINT,
                                            ext_class=(Shapes, Shape))

        # Bind the observers before starting the collectors so that they will
        # update the lists of known seq, configs, filters, contexts...
        self._bind_observers()

        self._sequences.start()
        self._configs.start()
        self._filters.start()
        self._contexts.start()
        self._shapes.start()

        # Populate the Pulse Info Object
        self._pulse_infos = PulseInfos()
        self._pulse_infos.cls = Pulse
        self._pulse_infos.view = PulseView

        core.invoke_command('ecpy.app.errors.exit_error_gathering')

    def stop(self):
        """ Stop the plugin life-cycle.

        This method is called by the framework at the appropriate time.
        It should never be called by user code.

        """
        super(PulsesManagerPlugin, self).stop()
        self._unbind_observers()
        self._template_sequences_data.clear()
        self._template_sequences_infos.clear()

        # Stop all Extension/DeclaratorCollectors
        self._filters.stop()
        self._configs.stop()
        self._sequences.stop()
        self._contexts.stop()
        self._shapes.stop()

    def get_item_infos(self, item_id):
        """Give access to an item infos.

        NB : an item can be a sequence or a pulse.

        Parameters
        ----------
        item_id : unicode
            The id of the requested item.

        Returns
        -------
        item_infos : ItemInfos or None
            The required item infos or None if it was not found.

        """
        if item_id == "ecpy_pulses.Pulse":
            return self._pulse_infos
        if item_id in self._sequences.contributions:
            return self._sequences.contributions[item_id]
        elif item_id in self._template_sequences_infos:
            t_info = self._template_sequences_infos[item_id]
            if not t_info.metadata['loaded']:
                config, doc = load_sequence_prefs(t_info.metadata['path'])
                t_info.metadata['template_config'] = config
                t_info.metadata['template_doc'] = doc
                t_info.metadata['loaded'] = True
            return t_info
        elif item_id == "ecpy_pulses.__template__":
            infos = SequenceInfos()
            infos.cls = TemplateSequence
            infos.view = TemplateSequenceView
            return infos
        else:
            return None

    def get_item(self, item_id, view=False):
        """Access a given item class.

        Parameters
        ----------
        item_id : unicode
            Id of the item for which to return the actual class.

        view : bool, optional
            Whether or not to return the view assoicated with the item.

        Returns
        -------
        item_cls : type or None
            Class associated to the requested item or None if the item was not
            found.

        item_view : EnamlDefMeta or None, optional
            Associated view if requested.

        """
        infos = self.get_item_infos(item_id)
        if not infos:
            return None if not view else (None, None)
        else:
            return infos.cls if not view else (infos.cls, infos.view)

    def get_items(self, item_ids):
        """Access the classes associated to a set of items.

        Parameters
        ----------
        item_ids : list(unicode)
            Ids of the item for which to return the actual class.

        Returns
        -------
        items_cls : dict
            Dictionary mapping the requested items to the actual classes.

        missing : list
            List of items that were not found.

        """
        items_cls = {}
        missing = []
        for t in item_ids:
            res = self.get_item(t)
            if res:
                items_cls[t] = res
            else:
                missing.append(t)

        return items_cls, missing

    def get_context_infos(self, context_id):
        """Give access to a context infos.

        Parameters
        ----------
        context_id : unicode
            Id of the requested context.

        Returns
        -------
        context_infos : ContextInfos or None
            Infos for the requested context or None if the context was not
            found.

        """
        return self._contexts.contributions.get(context_id)

    def get_context(self, context_id, view=False):
        """Access the class associated with a context.

        Parameters
        ----------
        context_id : unicode
            Id of the context for which to return the class

        view : bool, optional
            Whether or not to return the view associated with context.

        Returns
        -------
        context_cls : type or None
            Class associated to the requested context or None if the context
            was not found.

        item_view : EnamlDefMeta or None, optional
            Associated view if requested.

        """
        infos = self.get_context_infos(context_id)
        if not infos:
            return None if not view else (None, None)
        else:
            return infos.cls if not view else (infos.cls, infos.view)

    def get_shape_infos(self, shape_id):
        """ Give access to a shape infos.

        Parameters
        ----------
        shape : unicode
            Id of the requested shapes.
        view : bool
            When false, the view is not returned alongside the class.

        Returns
        -------
        shape_infos : ShapeInfos or None
            The required shape infos or None if the shape was not found.

        """
        return self._shapes.contributions.get(shape_id)

    def get_shape(self, shape_id, view=False):
        """Access the class associated with a shape.

        Parameters
        ----------
        shape_id : unicode
            Id of the shape for which to return the class

        view : bool, optional
            Whether or not to return the view associated with context.

        Returns
        -------
        context_cls : type or None
            Class associated to the requested shape or None if the shape
            was not found.

        item_view : EnamlDefMeta or None, optional
            Associated view if requested.

        """
        infos = self.get_shape_infos(shape_id)
        if not infos:
            return None if not view else (None, None)
        else:
            return infos.cls if not view else (infos.cls, infos.view)

    # TODO for future easiness of extension
    # Note that the pulse view should be updated too
    def get_modulation_infos(self, modulation_id):
        """
        """
        raise NotImplementedError()

    def get_modulation(self, modulation_id, view=False):
        """Get the modulation class.

        """
        if modulation_id == 'ecpy_pulses.Modulation':
            return Modulation
        else:
            None

    def get_config(self, sequence_id):
        """ Access the proper config for a sequence.

        Parameters
        ----------
        sequence_id : str
            Id of the sequence for which a config is required

        Returns
        -------
        config : tuple
            Tuple containing the config object requested, and its visualisation

        Notes
        -----
        It is the responsability of the user to properly set the root attribute
        of the returned config object.

        """
        templates = self._template_sequences_data
        if sequence_id in templates:
            config_infos = self._configs.contributions['__template__']
            conf_cls = config_infos.cls
            conf_view = config_infos.view
            t_config, t_doc = load_sequence_prefs(templates[sequence_id])
            conf = conf_cls(manager=self,
                            template_config=t_config,
                            template_doc=t_doc,
                            root=self.workspace.state.sequence)
            view = conf_view(model=conf)
            return conf, view

        elif sequence_id in self._sequences.contributions:
            configs = self._configs.contributions
            # Look up the hierarchy of the selected sequence to get the
            # appropriate SequenceConfig
            sequence_class = self._sequences.contributions[sequence_id].cls
            for i_class in type.mro(sequence_class):
                if i_class in configs:
                    conf_cls = configs[i_class].cls
                    conf_view = configs[i_class].view
                    conf = conf_cls(manager=self,
                                    sequence_class=sequence_class)
                    view = conf_view(model=conf)
                    return conf, view

        return None, None

    def list_sequences(self, filter_name='All'):
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
            template_sequences_data = self._template_sequences_data.copy()

            try:
                sequences.pop('ecpy_pulses.RootSequence')
            except KeyError:  # pragma: no cover
                pass
            return s_filter.filter_sequences(sequences,
                                             template_sequences_data)
        else:
            logger = logging.getLogger(__name__)
            logger.warn("Did not find the filter " + str(filter_name) +
                        " and returned zero elements.")
            return []

    # --- Private API ---------------------------------------------------------

    #: Sequences implemented in Python
    _sequences = Typed(DeclaratorsCollector)

    #: Template sequences (store full path to .ini)
    _template_sequences_data = Dict(Unicode(), Unicode())

    #: Template sequences infos
    _template_sequences_infos = Dict(Unicode(), SequenceInfos)

    #: Info Object for Pulse
    _pulse_infos = Typed(PulseInfos)

    #: Sequence contexts.
    _contexts = Typed(DeclaratorsCollector)

    #: Task config dict for python tasks (task_class: (config, view))
    _shapes = Typed(DeclaratorsCollector)

    #: Contributed task filters.
    _filters = Typed(ExtensionsCollector)

    #: Configuration object used to insert new sequences in existing ones.
    _configs = Typed(DeclaratorsCollector)

    # Watchdog observer
    _observer = Typed(Observer, ())

    def _refresh_known_template_sequences(self):
        """Refresh the known template sequences.

        """
        templates = {}
        for path in self.templates_folders:
            if os.path.isdir(path):
                filenames = [f for f in os.listdir(path)
                             if (os.path.isfile(os.path.join(path, f)) and
                                 f.endswith('.temp_pulse.ini'))]
                filenames.sort()
                for filename in filenames:
                    template_name = filename[:-len('.temp_pulse.ini')]
                    template_path = os.path.join(path, filename)

                    # Beware redundant names are overwrited
                    templates[template_name] = template_path
            else:
                logger = logging.getLogger(__name__)
                logger.warn('{} is not a valid directory'.format(path))

        self._template_sequences_data = templates
        aux = (list(self._sequences.contributions) +
               list(templates))

        self.sequences = aux
        self._refresh_template_sequences_infos()

    def _refresh_template_sequences_infos(self):
        """ Refresh the known template sequence infos.

        """
        # TODO Should be more proper in case of update

        templates = self._template_sequences_data
        templates_infos = {}

        for template_name, template_path in templates.items():

            metadata = {'is_template': True, 'path': template_path,
                        'loaded': False}
            infos = SequenceInfos(metadata=metadata)
            infos.cls = TemplateSequence
            infos.view = TemplateSequenceView
            templates_infos[template_name] = infos

        self._template_sequences_infos = templates_infos

    def _update_filters(self, change):
        """ Update the list of known filters.

        """
        self.filters = list(self._filters.contributions.keys())

    def _update_known_contexts(self, change):
        """ Update the list of known contexts.

        """
        self.contexts = list(self._contexts.contributions.keys())

    def _update_known_sequences(self, change):
        """ Update the list of known sequences.

        """
        self.sequences = list(self._sequences.contributions.keys())

        #: Always refresh the list of known templates after refreshing
        #: sequences, as we could have just added a template.
        self._refresh_known_template_sequences()

    def _update_known_shapes(self, change):
        """ Update the list of known shapes.

        """
        self.shapes = list(self._shapes.contributions.keys())

    def _bind_observers(self):
        """ Setup the observers for the plugin.

        """
        for folder in self.templates_folders:
            handler = SystematicFileUpdater(
                self._refresh_known_template_sequences)
            self._observer.schedule(handler, folder, recursive=True)

        self._observer.start()

        self._contexts.observe('contributions', self._update_known_contexts)
        self._shapes.observe('contributions', self._update_known_shapes)
        self._sequences.observe('contributions', self._update_known_sequences)
        self._filters.observe('contributions', self._update_filters)

        self.observe('templates_folders', self._update_templates)

    def _unbind_observers(self):
        """ Remove the observers for the plugin.

        """
        self.unobserve('templates_folders', self._update_templates)
        self._filters.unobserve('contributions', self._update_filters)
        self._observer.unschedule_all()
        self._observer.stop()
        self._observer.join()

    def _update_templates(self, change):
        """Observer ensuring that we observe the right template folders.

        """
        self._observer.unschedule_all()

        for folder in self.templates_folders:
            if not os.path.isdir(folder):
                continue
            handler = SystematicFileUpdater(
                self._refresh_known_template_sequences)
            self._observer.schedule(handler, folder, recursive=True)

        self._refresh_known_template_sequences()
