# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Definition of the template config.

Template config is used to gather required infomation to add a templateSequence
to the sequence beeing edited.

"""
from copy import deepcopy
from ast import literal_eval
from pprint import pformat

from atom.api import (Str, Value, Bool, Typed)
from exopy.utils.atom_util import update_members_from_preferences

from .base_config import AbstractConfig
from ..contexts.template_context import TemplateContext
from ..sequences.base_sequences import BaseSequence
from ..sequences.template_sequence import TemplateSequence
from ..pulse import Pulse


class TemplateConfig(AbstractConfig):
    """ Config used to insert a template into a sequence.

    The template can either be inserted as a TemplateSequence or merged.
    In the first case it will appear as a single item and the only inputs will
    be the declared template vars and the mapping between the true context of
    execution channels and the ones from the template context. The id of the
    template will be kept and the template will be re-used each time the
    sequence is rebuilt.
    In the second the template will be unraveled and inserted as many items,
    the user will be allowed to choose where the template vars should appear
    and to give a mapping between the contexts channels.

    """
    #: Name of the sequence used to make the sequence easier to read.
    template_name = Str()

    #: Docstring of the sequence.
    template_doc = Str()

    #: Configobj object describing the template.
    template_config = Value()

    #: Flag indicating whether the Template should be merged as a standard
    #: sequence or included as a TemplateSequence. In the first case all
    #: reference to the template is lost, in the second the template sequence
    #: rememeber its templates and use it when rebuilding itself.
    merge = Bool()

    #: When merging should the template vars be added as local_vars or
    #: external_vars in the root.
    t_vars_as_root = Bool()

    #: False template context used to determine the mapping between the
    #: template context channels and the ones from the root.
    #: Only used in merge mode.
    context = Typed(TemplateContext)

    def build_sequence(self):
        """ Build sequence using the selected template.

        """
        config = deepcopy(self.template_config)

        #: Here we set the item id of the "root" of the sequence (that needed
        #: to collect the right dependency). If we are NOT merging, then the
        #: template will be added as a TemplateSequence (and therefore we need
        #: a TemplateSequence as dependecy). If we ARE merging , then the root
        #: is a BaseSequence holding everything and we must collect it.
        if not self.merge:
            config['item_id'] = "exopy_pulses.__template__"
        else:
            config['item_id'] = "exopy_pulses.BaseSequence"

        #: Set the rest of the config variables that are needed.
        config['name'] = self.template_name
        config['template_id'] = '__template__'
        config['template_doc'] = self.template_doc

        #: Collect Dependencies
        core = self.manager.workbench.get_plugin('enaml.workbench.core')
        cmd = 'exopy.app.dependencies.analyse'
        cont = core.invoke_command(cmd, {'obj': config})
        if cont.errors:
            msg = 'Failed to analyse dependencies :\n%s'
            self.errors['dependencies'] = msg % pformat(cont.errors)
            return None

        cmd = 'exopy.app.dependencies.collect'
        cont = core.invoke_command(cmd, {'kind': 'build',
                                         'dependencies': cont.dependencies})
        if cont.errors:
            msg = 'Failed to collect dependencies :\n%s'
            self.errors['dependencies'] = msg % pformat(cont.errors)
            return None

        #: Shorthand
        build_dep = cont.dependencies

        if not self.merge:
            seq = TemplateSequence.build_from_config(config, build_dep)
            return seq

        else:
            t_vars = literal_eval(config.pop('template_vars'))
            if not self.t_vars_as_root:
                loc_vars = literal_eval(config['local_vars'])
                loc_vars.update(t_vars)
                config['local_vars'] = repr(loc_vars)
            else:
                self.root.external_vars.update(t_vars)

            # Don't want to alter the dependencies dict in case somebody else
            # use the same template.
            t_config = deepcopy(config)
            t_config.merge(config)
            config = t_config

            seq = BaseSequence.build_from_config(t_config, build_dep)

            self._apply_mapping(seq)

            return seq

    # --- Private API ---------------------------------------------------------

    def _post_setattr_template_name(self, old, new):
        """ Observer notifying that the configurer is ready to build.

        """
        self.ready = bool(new)

    def _apply_mapping(self, seq):
        """ Apply the user defined mapping of channels for the pulses.

        """
        c_mapping = self.context.channel_mapping
        for item in seq.items:
            if isinstance(item, Pulse):
                item.channel = c_mapping.get(item.channel, '')
            elif isinstance(item, TemplateSequence):
                mapping = item.context.channel_mapping
                for channel in mapping:
                    mapping[channel] = c_mapping.get(item.channel, '')
            elif isinstance(item, BaseSequence):
                self._apply_mapping(item)

    def _default_context(self):
        """ Initialize the context using the config.

        """
        config = self.template_config
        context = TemplateContext()

        update_members_from_preferences(context, config['context'])
        return context
