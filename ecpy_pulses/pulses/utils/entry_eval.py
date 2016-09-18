# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Base class and functions to evaluate fields relying on values found in other
objects of the sequence.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from inspect import cleandoc
from textwrap import fill
from traceback import format_exc

from atom.api import Dict
from ecpy.utils.atom_util import tagged_members, HasPrefAtom


EVALUATER_TOOLTIP = '\n'.join([
    fill(cleandoc("""In this field you can enter a text and
                  include fields which will be replaced by database
                  entries by using the delimiters '{' and '}' and
                  which will then be evaluated."""), 80),
    "Available math functions:",
    "- cos, sin, tan, acos, asin, atan, atan2",
    "- exp, log, log10, cosh, sinh, tanh, sqrt",
    "- complex math function are available under cm",
    "- numpy function are avilable under np",
    "- pi is available as Pi"])


class MissingLocalVars(Exception):
    """Raised if some variables are found missing from the locals.

    """
    def __init__(self, missings):
        self.missings = missings


def eval_entry(string, seq_locals):
    """Evaluate a formula found in pulse sequence using the provided variables

    """
    aux_strings = string.split('{')
    if len(aux_strings) > 1:
        elements = [el for aux in aux_strings
                    for el in aux.split('}')]

        missings = [el for el in elements[1::2] if el not in seq_locals]
        if missings:
            raise MissingLocalVars(missings)

        replacement_token = ['_a{}'.format(i)
                             for i in range(len(elements[1::2]))]
        replacement_values = {'_a{}'.format(i): seq_locals[key]
                              for i, key in enumerate(elements[1::2])}

        str_to_eval = ''.join(key + '{}' for key in elements[::2])
        str_to_eval = str_to_eval[:-2]

        expr = str_to_eval.format(*replacement_token)
    else:
        replacement_values = {}
        expr = string

    return eval(expr, globals(), replacement_values)


class HasEvaluableFields(HasPrefAtom):
    """Object handling the formatting or evaluation of formulas based on tags.

    Members should be tagged as fmt for formatting and feval for evaluation.
    In the first case the value can be False or True depending on whether the
    result should be stored as a global variables. In the second case, the
    value should be a Feval instance.

    Notes
    -----
    Feval should be imported from ecpy_pulses.pulses.api not
    from ecpy.tasks.api


    """

    def eval_entries(self, global_vars, local_vars, missings, errors):
        """Evaluate and format all tagged members.

        The result of the evaluation is written to the _cache dictionary.

        Parameters
        ----------
        global_vars : dict
            Dictionary of global variables. This will be update will the valid
            values whose tag specify they should be stored as global.

        local_vars : dict
            Dictionary of variables used for evaluation. This will be update
            will the valid values whose tag specify they should be stored as
            global.

        missings : set
            Set of unfound local variables.

        errors : dict
            Dict of the errors which happened when performing the evaluation.

        Returns
        -------
        flag : bool
            Boolean indicating whether or not the evaluation succeeded.

        """
        res = True
        cache = self._cache

        for member, store in tagged_members(self, 'fmt').items():
            if member in cache:
                continue
            fmt_str = getattr(self, member)
            try:
                fmt = fmt_str.format(**local_vars)
                self._cache[member] = fmt
                if store:
                    id_ = self.format_global_vars_id(member)
                    global_vars[id_] = fmt
                    local_vars[id_] = fmt
            # This can only occur if a {} field was found and an entry is
            # missing
            except KeyError:
                res = False
                aux_strings = fmt_str.split('{')
                elements = [el for aux in aux_strings
                            for el in aux.split('}')]
                absent = [el for el in elements[1::2]
                          if el not in local_vars]
                missings.update(absent)
            except Exception:
                res = False
                errors[self.format_error_id(member)] = format_exc()

        for member, m in tagged_members(self, 'feval').items():
            feval = m.metadata['feval']
            if member in cache:
                continue
            if not feval.should_test(self, member):
                continue
            try:
                val, store = feval.evaluate(self, member, local_vars)
                valid, msg = feval.validate(self, val)
                if not valid:
                    res = False
                    errors[self.format_error_id(member)] = msg
                else:
                    self._cache[member] = val
                    if store:
                        id_ = self.format_global_vars_id(member)
                        global_vars[id_] = val
                        local_vars[id_] = val
            except MissingLocalVars as e:
                res = False
                missings.update(e.missings)
            except Exception:
                res = False
                errors[self.format_error_id(member)] = format_exc()

        return res

    def clean_cached_values(self):
        """Clean all the cached values.

        """
        self._cache.clear()

    def format_global_vars_id(self, member):
        """Format the id under which to store a value in the global and local
        variables used for evaluation.

        """
        raise NotImplementedError()

    def format_error_id(self, member):
        """Format the name under which to log that an error occured when
        formatting/evaluating a formula.

        """
        raise NotImplementedError()

    # =========================================================================
    # --- Private API ---------------------------------------------------------
    # =========================================================================

    #: Dictionary in which the values computed by the eval_entries method are
    #: stored.
    _cache = Dict()
