# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Sequence allowing conditional inclusion of its items.

"""
from atom.api import Str, Bool, set_default

from .base_sequences import BaseSequence
from ..utils.validators import Feval


class ConditionalSequence(BaseSequence):
    """Sequence whose child items will be included only if a condition is met.

    """
    #: Condition to be evaluated. If this evaluates to true then sub-items will
    #: be executed
    condition = Str().tag(pref=True, feval=Feval(store_global=True))

    #: Name of the variable which can be referenced in other items.
    #: Those should not contain the index of the item.
    linkable_vars = set_default(['condition'])

    def evaluate_sequence(self, root_vars, sequence_locals, missings, errors):
        """ Evaluate the sequence vars and compile the list of pulses.

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

        """
        res = self.eval_entries(root_vars, sequence_locals, missings, errors)

        # If the condition is False the sequence will do nothing so consider
        # it a success.
        if 'condition' in self._cache and not self._cache['condition']:
            return True

        if not res:
            return False

        if self._cache['condition']:
            return super(ConditionalSequence,
                         self).evaluate_sequence(root_vars, sequence_locals,
                                                 missings, errors)

    def simplify_sequence(self):
        """Inline the sequences not supported by the context.

        """
        if self._cache['condition']:
            return super(ConditionalSequence, self).simplify_sequence()
        else:
            return []

    # =========================================================================
    # --- Private API ---------------------------------------------------------
    # =========================================================================

    #: Cached value of the computed condition.
    _condition = Bool()
