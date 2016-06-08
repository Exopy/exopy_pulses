# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


from atom.api import (Dict, ForwardTyped, Unicode)
from inspect import cleandoc
from copy import deepcopy
from ast import literal_eval

from ecpy.utils.atom_util import update_members_from_preferences

from ..utils.entry_eval import eval_entry
from .base_sequences import AbstractSequence, BaseSequence


def context():
    from ..contexts.template_context import TemplateContext
    return TemplateContext


class TemplateSequence(AbstractSequence):
    """ Sequence used to represent a template in a Sequence.

    """
    #: Id of the template on which this sequence relies.
    template_id = Unicode().tag(pref=True)

    #: Dict of variables defined in the template scope.
    template_vars = Dict().tag(pref=True)

    #: Documentation of the template as provided by the user.
    docs = Unicode()

    #: Special context providing channel mapping.
    context = ForwardTyped(context).tag(pref=True)

    def compile_sequence(self, root_vars, sequence_locals, missings, errors):
        """

        """
        # Check the channel mapping makes sense.
        if not self.context.prepare_compilation(errors):
            return False, []

        # Definition evaluation.
        self.eval_entries(root_vars, sequence_locals, missings, errors)

        prefix = '{}_'.format(self.index)
        # Template vars evaluation.
        for name, formula in self.template_vars.items():
            if name not in self._evaluated_vars:
                try:
                    val = eval_entry(formula, sequence_locals, missings)
                    self._evaluated_vars[name] = val
                except Exception as e:
                    errors[prefix + name] = repr(e)

        # Local vars computation.
        for name, formula in self.local_vars.items():
            if name not in self._evaluated_vars:
                try:
                    val = eval_entry(formula, sequence_locals, missings)
                    self._evaluated_vars[name] = val
                except Exception as e:
                    errors[prefix + name] = repr(e)

        local_namespace = self._evaluated_vars.copy()
        local_namespace['sequence_end'] = self.duration

        res, pulses = self._compile_items(local_namespace, local_namespace,
                                          missings, errors)

        if res:
            t_start = self.start
            c_mapping = self.context.channel_mapping
            try:
                for pulse in pulses:
                    pulse.start += t_start
                    pulse.stop += t_start
                    pulse.channel = c_mapping[pulse.channel]
            except KeyError as e:
                errors[self.name + '-channels'] = \
                    'Channel mapping is corrupted : {}'.format(e)
                return False, []

            # Check if stop time of pulses are compatible with sequence
            # duration.
            stop_err = [pulse for pulse in pulses
                        if pulse.stop > self.stop]

            if stop_err:
                mess = cleandoc('''The stop time of the following items {}
                    is larger than the stop time of the sequence {}''')
                mess = mess.replace('\n', ' ')
                ind = [p.index for p in stop_err]
                errors[self.name + '-stop'] = mess.format(ind, self.index)

            if errors:
                return False, []

            return True, pulses

        else:
            return False, []

    @classmethod
    def build_from_config(cls, config, dependencies):
        """ Create a new instance using the provided infos for initialisation.

        Overridden here to allow context creation.

        Parameters
        ----------
        config : dict(str)
            Dictionary holding the new values to give to the members in string
            format, or dictionnary like for instance with prefs.

        dependencies : dict
            Dictionary holding the necessary classes needed when rebuilding.

        Returns
        -------
        sequence : TemplateSequence
            Newly created and initiliazed sequence.

        """
        # First get the underlying template from the dependencies and merge
        # config into it as it has more recent infos about the context and
        # the vars.
        dep = dependencies

        # Don't want to alter the dependencies dict in case somebody else use
        # the same template.
        t_config = deepcopy(config)

        # Make sure the template_vars stored in the config match the one
        # declared in the template.
        t_vars = literal_eval(config.pop('template_vars'))
        declared_t_vars = literal_eval(t_config['template_vars'])
        for var in declared_t_vars:
            declared_t_vars[var] = t_vars.get(var, '')
        t_config['template_vars'] = repr(declared_t_vars)

        t_config.merge(config)
        config = t_config

        context_config = config['context']
        context_id_name = context_config.pop('context_id')
        context_id = dep['ecpy.pulses.contexts'][context_id_name]
        context = context_id()
        update_members_from_preferences(context, context_config)

        seq = super(TemplateSequence, cls).build_from_config(t_config,
                                                             dependencies)
        seq.docs = config['template_doc']
        seq.context = context

        # Do the indexing of the children once and for all.
        i = 1
        for item in seq.items:
            item.index = i
            item.root = seq
            if isinstance(item, BaseSequence):
                item._recompute_indexes()
                i = item._last_index + 1
            else:
                i += 1

        return seq

    # --- Private API ---------------------------------------------------------

    def _post_setattr_context(self, change):
        """ Make sure the context has a ref to the sequence.

        """
        c = change['value']
        if c:
            c.template_sequence = self
