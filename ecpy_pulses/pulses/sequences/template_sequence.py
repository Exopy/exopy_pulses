# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Sequence use to insert another premade sequence.

"""
# TODO this is unfinished and requires a update to ecpy to support declaring
# multiple build dependencies

from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from copy import deepcopy
from ast import literal_eval

from atom.api import (Dict, ForwardTyped, Unicode, List)

from ecpy.utils.atom_util import update_members_from_preferences
from ecpy.utils.traceback import format_exc

from ..pulse import Pulse
from ..utils.entry_eval import eval_entry
from .base_sequences import AbstractSequence, BaseSequence


def context():
    from ..contexts.template_context import TemplateContext
    return TemplateContext


# TODO need a custom dep_id to also collect the config of the template
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

    #: Ids of the global linkable vars. Those are for example the start, stop
    #: and duration of most items.
    global_vars = List()

    def evaluate_sequence(self, root_vars, sequence_locals, missings, errors):
        """Evaluate the entries of the items making the context.

        """
        # Check the channel mapping makes sense.
        if not self.context.prepare_compilation(errors):
            return False

        # Definition evaluation.
        self.eval_entries(root_vars, sequence_locals, missings, errors)

        prefix = '{}_'.format(self.index)
        # Template vars evaluation.
        for name, formula in self.template_vars.items():
            if name not in self._evaluated_vars:
                try:
                    val = eval_entry(formula, sequence_locals, missings)
                    self._evaluated_vars[name] = val
                except Exception:
                    errors[prefix + name] = format_exc()

        # Local vars computation.
        for name, formula in self.local_vars.items():
            if name not in self._evaluated_vars:
                try:
                    val = eval_entry(formula, sequence_locals, missings)
                    self._evaluated_vars[name] = val
                except Exception:
                    errors[prefix + name] = format_exc()

        local_namespace = self._evaluated_vars.copy()
        local_namespace['sequence_end'] = self.duration

        res = self._evaluate_items(local_namespace, local_namespace,
                                   missings, errors)

        if res:
            overtime = []
            self._update_times(self.items, errors, overtime)

            if overtime:
                msg = ('The stop time of the following items {} is larger '
                       'than the stop time of the sequence {}')
                ind = [p.index for p in overtime]
                errors[self.name + '-stop'] = msg.format(ind, self.index)

        if errors:
            return False

        return True

    def simplify_sequence(self):
        """Inline the sequences not supported by the context.

        """
        supported = self.root.context.supported_sequences

        seq = []
        for item in self.items:
            if not item.enabled:
                continue
            if isinstance(item, Pulse) or type(item) in supported:
                seq.append(item)
            else:
                seq.extend(item.simplify_sequence())

        return seq

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
        # TOOD this is not correct as the template config is never retrieved

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
        context_id = dep['ecpy.pulses.context'][context_id_name]
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

    def _update_times(self, items, errors, overtime):
        """Offset all the timing of the items and check it still make sense.

        Parameters
        ----------
        items : list
            List of items whose end time should be checked.

        errors : dict
            Dict in which to report errors.

        overtime : list
            List of items which do not respect the time constraint.

        """
        t_start = self.start
        c_mapping = self.context.channel_mapping
        for i in items:
            if isinstance(i, Pulse):
                i.start += t_start
                i.stop += t_start
                try:
                    i.channel = c_mapping[i.channel]
                except KeyError as e:
                    errors[self.name + '-channels'] = \
                        'Channel mapping is corrupted : {}'.format(e)
                if i.stop > self.stop:
                    overtime.append(i)
            else:
                self._update_times(i.items, errors, overtime)
                if i.duration and i.stop > self.stop:
                    overtime.append(i)

    def _post_setattr_context(self, old, new):
        """ Make sure the context has a ref to the sequence.

        """
        if new:
            new.template_sequence = self
