# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
from atom.api import Unicode, set_default

from .base_sequences import BaseSequence
from ..utils.entry_eval import eval_entry


class ConditionalSequence(BaseSequence):
    """ Sequence whose child items will be included only if a condition is met.

    """
    condition = Unicode().tag(pref=True)

    linkable_vars = set_default(['condition'])

    def compile_sequence(self, root_vars, sequence_locals, missings, errors):
        """ Compile the sequence in a flat list of pulses.

        The list of pulse will be not empty only if the condition specified
        for the sequence is met.

        Parameters
        ----------
        root_vars : dict
            Dictionary of global variables for the all items. This will
            tipically contains the i_start/stop/duration and the root vars.
            This dict must be updated with global new values but for
            evaluation sequence_locals must be used.

        sequence_locals : dict
            Dictionary of variables whose scope is limited to this sequence
            parent. This dict must be updated with global new values and
            must be used to perform evaluation (It always contains all the
            names defined in root_vars).

        missings : set
            Set of unfound local variables.

        errors : dict
            Dict of the errors which happened when performing the evaluation.

        Returns
        -------
        flag : bool
            Boolean indicating whether or not the evaluation succeeded.

        pulses : list
            List of pulses in which all the string entries have been evaluated.

        """
        cond = None
        try:
            cond = bool(eval_entry(self.condition,
                                   sequence_locals, missings))
        except Exception as e:
            errors['{}_'.format(self.index) + 'condition'] = repr(e)

        if cond is None:
            return False, []

        local = '{}_'.format(self.index) + 'condition'
        sequence_locals[local] = cond

        if cond:
            return super(ConditionalSequence,
                         self).compile_sequence(root_vars, sequence_locals,
                                                missings, errors)

        else:
            return True, []