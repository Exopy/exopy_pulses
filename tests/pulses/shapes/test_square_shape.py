# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test for the square shape.

The view is tested as part of the pulse.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest
import numpy as np
from numpy.testing import assert_array_equal

from ecpy_pulses.pulses.shapes.square_shape import SquareShape


def test_eval_square_amplitude1():
    """Test evaluating the amplitude of a square shape.

    """
    shape = SquareShape(amplitude='1*{a}')
    root_vars = {'a': 1.0}
    missing = set()
    errors = {}

    assert shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert errors == {}
    assert_array_equal(shape.compute(np.ones(1), 'mus'), 1.0)


def test_eval_amplitude_too_large():
    """Test handling a too large amplitude.

    """
    shape = SquareShape(amplitude='2*{a}')
    root_vars = {'a': 1.0}
    missing = set()
    errors = {}

    assert not shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert '0_shape_amplitude' in errors


def test_eval_amplitude2():
    """Test evaluating the entries of an active modulation when some vars
    are missing.
    Issue on amplitude.

    """
    shape = SquareShape(amplitude='1*{b}')
    root_vars = {'a': 1.0}
    missing = set()
    errors = {}

    assert not shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set('b')


def test_eval_amplitude3():
    """Test evaluating the entries of an active modulation when some entries
    are incorrect.
    Issue on frequency.

    """
    shape = SquareShape(amplitude='1*{a}+-')
    root_vars = {'a': 1.0}
    missing = set()
    errors = {}

    assert not shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert '0_shape_amplitude' in errors


def test_global_id():
    """Test that formatting a global id does raise.

    """
    shape = SquareShape()
    with pytest.raises(RuntimeError):
        shape.format_global_vars_id('r')
