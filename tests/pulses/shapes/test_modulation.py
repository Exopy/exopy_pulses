# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test for the modulation.

The view is tested as part of the pulse view.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest
import numpy as np
from numpy.testing import assert_array_equal, assert_array_almost_equal

from exopy_pulses.pulses.shapes.modulation import Modulation


def test_eval_modulation1():
    """Test evaluating the entries of an inactive modulation.

    """
    modulation = Modulation()
    root_vars = {'a': 1.0}
    missing = set()
    errors = {}

    assert modulation.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert errors == {}
    assert_array_equal(modulation.compute(np.zeros(1), 'mus'), 1.0)


def test_eval_modulation2():
    """Test evaluating the entries of an active modulation.

    """
    modulation = Modulation(activated=True)
    modulation.frequency = '1.0*{a}'
    modulation.phase = '0.0'

    root_vars = {'a': 1.0}
    missing = set()
    errors = {}

    assert modulation.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert errors == {}
    assert_array_equal(modulation.compute(np.array([0, 0.25]), 'mus'),
                       np.array([0, 1]))


def test_eval_modulation2bis():
    """Test evaluating the entries of an active modulation.

    """
    modulation = Modulation(activated=True)
    modulation.frequency = '1.0*{a}'
    modulation.phase = '90.0'
    modulation.phase_unit = 'deg'
    modulation.kind = 'cos'

    root_vars = {'a': 1.0}
    missing = set()
    errors = {}

    assert modulation.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert errors == {}
    assert_array_almost_equal(modulation.compute(np.array([0, 0.25]), 'mus'),
                              np.array([0, -1]))


def test_eval_modulation3():
    """Test evaluating the entries of an active modulation when some vars
    are missing.
    Issue on frequency.

    """
    modulation = Modulation(activated=True)
    modulation.frequency = '1.0*{a}'
    modulation.phase = '0.0'

    root_vars = {}
    missing = set()
    errors = {}

    assert not modulation.eval_entries({}, root_vars, missing, errors)
    assert missing == set('a')


def test_eval_modulation4():
    """Test evaluating the entries of an active modulation when some vars
    are missing.
    Issue on phase.

    """
    modulation = Modulation(activated=True)
    modulation.frequency = '1.0'
    modulation.phase = '0.0*{a}'

    root_vars = {}
    missing = set()
    errors = {}

    assert not modulation.eval_entries({}, root_vars, missing, errors)
    assert missing == set('a')


def test_eval_modulation5():
    """Test evaluating the entries of an active modulation when some entries
    are incorrect.
    Issue on frequency.

    """
    modulation = Modulation(activated=True)
    modulation.frequency = '1.0*'
    modulation.phase = '0.0'

    root_vars = {}
    missing = set()
    errors = {}

    assert not modulation.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert '0_modulation_frequency' in errors


def test_eval_modulation6():
    """Test evaluating the entries of an active modulation when some entries
    are incorrect.
    Issue on phase.

    """
    modulation = Modulation(activated=True)
    modulation.frequency = '1.0'
    modulation.phase = '0.0*'

    root_vars = {}
    missing = set()
    errors = {}

    assert not modulation.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert '0_modulation_phase' in errors


def test_global_id():
    """Test that formatting a global id does raise.

    """
    shape = Modulation()
    with pytest.raises(RuntimeError):
        shape.format_global_vars_id('r')
