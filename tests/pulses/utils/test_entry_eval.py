# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test automatic evaluation and formatting tools

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from math import exp, pi as Pi
import cmath as cm
                        
import numpy as np
from atom.api import Unicode

from ecpy_pulses.pulses.utils.entry_eval import HasEvaluableFields
from ecpy_pulses.pulses.utils.validators import Feval, SkipEmpty


FORMULA = 'Pi*np.array(cm.sqrt(exp(2*{feval2}))).real'

class EvalFmtTest(HasEvaluableFields):
    """Test class for HasEvaluableFields.

    """
    fmt1 = Unicode('+{fmt1}').tag(fmt=True)

    fmt2 = Unicode('+{fmt2}').tag(fmt=False)

    feval1 = Unicode('2*{feval1}').tag(feval=Feval(store_global=True))

    feval2 = Unicode(FORMULA).tag(feval=Feval(types=(int, float)))

    feval3 = Unicode('').tag(feval=SkipEmpty(types=int))

    def format_error_id(self, member):
        return member

    def format_global_vars_id(self, member):
        return member


def test_automatic_evaluation():
    """Test automatically evaluating fmt and feval tagged fields.

    """
    obj = EvalFmtTest()
    glob = {}
    loc = dict(fmt1='r', fmt2='t', feval1=1, feval2=2)
    missings = set()
    errors = {}

    assert obj.eval_entries(glob, loc, missings, errors)
    assert 'fmt1' in glob and 'feval1' in glob
    assert 'fmt2' not in glob and 'feval2' not in glob
    assert glob['fmt1'] == '+r' and glob['feval1'] == 2
    
    formula_val = eval(FORMULA.format(**loc))
    for k, v in dict(fmt1='+r', fmt2='+t', feval1=2,
                     feval2=formula_val).items():
        assert obj._cache[k] == v
        if k in glob:
            assert loc[k] == v
    assert not missings
    assert not errors

    loc['feval1'] = 2

    obj.feval3 = '1'
    assert obj.eval_entries(glob, loc, missings, errors)
    assert obj._cache['feval3'] == 1
    assert obj._cache['feval1'] == 2  # Would be 4 it had been re-evaluated

    obj.clean_cached_values()

    assert not obj._cache


def test_handling_format_missing():
    """Test handling a missing field in formatting.

    """
    obj = EvalFmtTest()
    glob = {}
    loc = dict(fmt1='r', feval1=1, feval2=2)
    missings = set()
    errors = {}

    assert not obj.eval_entries(glob, loc, missings, errors)
    assert 'fmt2' in missings


def test_handling_format_error():
    """Test handling an error in formatting.

    """
    obj = EvalFmtTest(fmt2='{')
    glob = {}
    loc = dict(fmt1='r', fmt2='t', feval1=1, feval2=2)
    missings = set()
    errors = {}

    assert not obj.eval_entries(glob, loc, missings, errors)
    assert 'fmt2' in errors


def test_handling_feval_missing():
    """Test handling a missing field in f-evaluating.

    """
    obj = EvalFmtTest()
    glob = {}
    loc = dict(fmt1='r', fmt2='t', feval1=1)
    missings = set()
    errors = {}

    assert not obj.eval_entries(glob, loc, missings, errors)
    assert 'feval2' in missings


def test_handling_feval_error():
    """Test handling an error in f-evaluating.

    """
    obj = EvalFmtTest(feval2='+*{feval2}')
    glob = {}
    loc = dict(fmt1='r', fmt2='t', feval1=1, feval2=2)
    missings = set()
    errors = {}

    assert not obj.eval_entries(glob, loc, missings, errors)
    assert 'feval2' in errors


def test_handling_feval_type_error():
    """Test handling an incorrect type for a f-evaluated field.

    """
    obj = EvalFmtTest(feval2='[{feval2}]')
    glob = {}
    loc = dict(fmt1='r', fmt2='t', feval1=1, feval2=2)
    missings = set()
    errors = {}

    assert not obj.eval_entries(glob, loc, missings, errors)
    assert 'feval2' in errors
