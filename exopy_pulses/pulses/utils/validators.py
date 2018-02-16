# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2016-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Validators for feval members.

"""
from atom.api import Atom, Value, Bool

from .entry_eval import eval_entry


class Feval(Atom):
    """Object hanlding the validation of feval tagged member.

    """
    #: Allowed types for the result of the evaluation of the member.
    types = Value()

    #: Should the value be stored in the global after being evaluated.
    store_global = Bool()

    def evaluate(self, obj, member, loc_vars):
        """Validate the feval formula.

        Parameters
        ----------
        obj : HasEvaluatedFields
            Obj storing the member tagged with the validator

        member : unicode
            Name of the member to evaluate.

        loc_vars : dict
            Local variables to use for evaluating the formula.

        Returns
        -------
        value : any
            Value of the evaluated formula

        should_store : bool
            Should the value be stored in the globals. By defaults this is
            the logical and of should_store and should_test

        """
        str_value = getattr(obj, member)
        val = eval_entry(str_value, loc_vars)

        return val, self.store_global

    def should_test(self, obj, member):
        """Should the value stored in the member actually be tested.

        """
        return True

    def validate(self, obj, value):
        """Validate that the value resulting from the evaluation makes sense.

        """
        if self.types:
            if not isinstance(value, self.types):
                msg = 'Expected value should of types {}, got {}.'
                return False, msg.format(self.types, type(value))

        return True, ''


class SkipEmpty(Feval):
    """Specialized validator skipping empty fields.

    """
    def should_test(self, obj, member):
        """Only test if a formula is provided.

        """
        return bool(getattr(obj, member))
