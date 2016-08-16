# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test evaluation of pulses entries.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest
import numpy as np
from numpy.testing import assert_array_equal

from ecpy_pulses.pulses.pulse import Pulse
from ecpy_pulses.pulses.sequences.base_sequences import RootSequence
from ecpy_pulses.pulses.shapes.square_shape import SquareShape
from ecpy_pulses.testing.context import TestContext


@pytest.fixture
def pulse():
    return Pulse(root=RootSequence(context=TestContext()))


def test_eval_pulse1(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Stop mode, meaningful values.

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert pulse.eval_entries(root_vars, seq_locals, missing, errors)

    assert missing == set()
    assert errors == {}
    assert root_vars['0_start'] == 2.0
    assert root_vars['0_stop'] == 3.0
    assert root_vars['0_duration'] == 1.0
    assert seq_locals['0_start'] == 2.0
    assert seq_locals['0_stop'] == 3.0
    assert seq_locals['0_duration'] == 1.0
    assert pulse.start == 2.0
    assert pulse.stop == 3.0
    assert pulse.duration == 1.0
    assert_array_equal(pulse.waveform, np.ones(1))


def test_eval_pulse2(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Stop mode, meaningless start.

    """
    pulse.def_1 = '-1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 2.0, 'b': 10.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_start' in errors
    assert '0_start' not in root_vars
    assert '0_duration' not in root_vars
    assert '0_start' not in seq_locals
    assert '0_duration' not in seq_locals


def test_eval_pulse3(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Stop mode, meaningless stop (0).

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 0.0, 'b': 10.0, 'c': 0.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_stop' in errors
    assert '0_stop' not in root_vars
    assert '0_duration' not in root_vars
    assert '0_stop' not in seq_locals
    assert '0_duration' not in seq_locals


def test_eval_pulse4(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Stop mode, meaningless stop < start.

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 0.0, 'b': 10.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_stop' in errors
    assert '0_stop' not in root_vars
    assert '0_duration'not in root_vars
    assert '0_stop' not in seq_locals
    assert '0_duration' not in seq_locals


def test_eval_pulse5(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Duration mode, meaningful values.

    """
    pulse.def_mode = 'Start/Duration'
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert pulse.eval_entries(root_vars, seq_locals,
                              missing, errors)

    assert missing == set()
    assert errors == {}
    assert root_vars['0_start'] == 2.0
    assert root_vars['0_stop'] == 5.0
    assert root_vars['0_duration'] == 3.0
    assert seq_locals['0_start'] == 2.0
    assert seq_locals['0_stop'] == 5.0
    assert seq_locals['0_duration'] == 3.0
    assert pulse.start == 2.0
    assert pulse.stop == 5.0
    assert pulse.duration == 3.0
    assert_array_equal(pulse.waveform, np.ones(3))


def test_eval_pulse6(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Duration mode, meaningless start.

    """
    pulse.def_mode = 'Start/Duration'
    pulse.def_1 = '-1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 0.0, 'b': 10.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_start' in errors
    assert '0_start' not in root_vars
    assert '0_stop' not in root_vars
    assert '0_start' not in seq_locals
    assert '0_stop' not in seq_locals


def test_eval_pulse7(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Duration mode, meaningless duration.

    """
    pulse.def_mode = 'Start/Duration'
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 0.0, 'b': 10.0, 'c': 0.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_duration' in errors
    assert '0_duration' not in root_vars
    assert '0_stop' not in root_vars
    assert '0_duration' not in seq_locals
    assert '0_stop' not in seq_locals


def test_eval_pulse8(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Duration/Stop mode, meaningful values.

    """
    pulse.def_mode = 'Duration/Stop'
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert pulse.eval_entries(root_vars, seq_locals,
                              missing, errors)

    assert missing == set()
    assert errors == {}
    assert root_vars['0_start'] == 1.0
    assert root_vars['0_stop'] == 3.0
    assert root_vars['0_duration'] == 2.0
    assert seq_locals['0_start'] == 1.0
    assert seq_locals['0_stop'] == 3.0
    assert seq_locals['0_duration'] == 2.0
    assert pulse.start == 1.0
    assert pulse.stop == 3.0
    assert pulse.duration == 2.0
    assert_array_equal(pulse.waveform, np.ones(2))


def test_eval_pulse9(pulse):
    """Test evaluating the entries of a pulse Duration/Stop mode,
    meaningless duration.

    """
    pulse.def_mode = 'Duration/Stop'
    pulse.def_1 = '-1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 0.0, 'b': 10.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_duration' in errors
    assert '0_duration' not in root_vars
    assert '0_start' not in root_vars
    assert '0_duration' not in seq_locals
    assert '0_start' not in seq_locals


def test_eval_pulse10(pulse):
    """Test evaluating the entries of a pulse Duration/Stop mode,
    meaningless stop.

    """
    pulse.def_mode = 'Duration/Stop'
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 0.0, 'b': 10.0, 'c': 0.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_stop' in errors
    assert '0_stop' not in root_vars
    assert '0_start' not in root_vars
    assert '0_stop' not in seq_locals
    assert '0_start' not in seq_locals


def test_eval_pulse11(pulse):
    """Test evaluating the entries of a pulse Duration/Stop mode, duration
    larger than stop.

    """
    pulse.def_mode = 'Duration/Stop'
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 0.0, 'b': 10.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_stop' in errors
    assert '0_start' not in root_vars
    assert '0_start' not in seq_locals


def test_eval_pulse12(pulse):
    """Test evaluating the entries of a pulse when some vars are missing.
    Issue in def_1

    """
    pulse.def_1 = '1.0*2.0*{d}'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 2.0, 'b': 10.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set('d')
    assert '0_start' not in errors
    assert '0_start' not in root_vars
    assert '0_stop' in root_vars
    assert '0_start' not in seq_locals
    assert '0_stop', seq_locals


def test_eval_pulse13(pulse):
    """Test evaluating the entries of a pulse when some vars are missing.
    Issue in def_2

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 2.0, 'b': 10.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set('c')
    assert '0_stop' not in errors
    assert '0_stop' not in root_vars
    assert '0_start' in root_vars
    assert '0_stop' not in seq_locals
    assert '0_start' in seq_locals


def test_eval_pulse14(pulse):
    """Test evaluating the entries of a pulse when some entries are
    incorrect.
    Issue def_1

    """
    pulse.def_1 = '1.0*2.0*zeffer'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 2.0, 'b': 10.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_start' in errors
    assert '0_start' not in root_vars
    assert '0_stop' in root_vars
    assert '0_start' not in seq_locals
    assert '0_stop' in seq_locals


def test_eval_pulse15(pulse):
    """Test evaluating the entries of a pulse when some entries are
    incorrect.
    Issue in def_2

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c} + zeffer'

    root_vars = {'a': 2.0, 'b': 10.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert not pulse.eval_entries(root_vars, seq_locals,
                                  missing, errors)

    assert missing == set()
    assert '0_stop' in errors
    assert '0_stop' not in root_vars
    assert '0_start' in root_vars
    assert '0_stop' not in seq_locals
    assert '0_start' in seq_locals


def test_eval_pulse16(pulse):
    """Test evaluating the entries of an analogical pulse.

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    pulse.shape = SquareShape(amplitude='0.5')
    pulse.kind = 'Analogical'

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    assert pulse.eval_entries(root_vars, root_vars,
                              missing, errors)

    assert missing == set()
    assert errors == {}
    assert_array_equal(pulse.waveform, 0.5*np.ones(1))


def test_eval_pulse17(pulse):
    """Test evaluating the entries of an analogical pulse whose modulation
    evaluation fails.

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    pulse.shape = SquareShape(amplitude='0.5')
    pulse.kind = 'Analogical'

    pulse.modulation.frequency = '1.0**'
    pulse.modulation.phase = '1.0'
    pulse.modulation.activated = True

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    assert not pulse.eval_entries(root_vars, root_vars,
                                  missing, errors)

    assert missing == set()
    assert '0_mod_frequency' in errors


def test_eval_pulse18(pulse):
    """Test evaluating the entries of an analogical pulse whose shape
    evaluation fails.

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    pulse.shape = SquareShape(amplitude='0.5*')
    pulse.kind = 'Analogical'

    pulse.modulation.frequency = '1.0'
    pulse.modulation.phase = '1.0'
    pulse.modulation.activated = True

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    assert not pulse.eval_entries(root_vars, root_vars,
                                  missing, errors)

    assert missing == set()
    assert'0_shape_amplitude' in errors
