# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""The version information for this release of Ecpy.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest

from ecpy_pulses.pulses.pulse import Pulse
from ecpy_pulses.pulses.base_sequences import RootSequence, Sequence
from ecpy_pulses.pulses.sequences.conditional_sequence\
     import ConditionalSequence

from .context import TestContext


def test_conditional_sequence_compilation1(root):
    """Test compiling a conditional sequence whose condition evaluates to
    False.


    """
    root.external_vars = {'a': 1.5, 'include': True}

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = Sequence(items=[pulse3])
    sequence1 = ConditionalSequence(items=[pulse2, sequence2, pulse4],
                                    condition='{include}')

    root.items = [pulse1, sequence1, pulse5]

    res, pulses = root.compile_sequence(False)
    assert_true(res)
    assert len(pulses), 5)
    assert_is(pulses[0], pulse1)
    assert pulses[0].start, 1.0)
    assert pulses[0].stop, 2.0)
    assert pulses[0].duration, 1.0)
    assert_is(pulses[1], pulse2)
    assert pulses[1].start, 2.5)
    assert pulses[1].stop, 3.0)
    assert pulses[1].duration, 0.5)
    assert_is(pulses[2], pulse3)
    assert pulses[2].start, 3.5)
    assert pulses[2].stop, 10.0)
    assert pulses[2].duration, 6.5)
    assert_is(pulses[3], pulse4)
    assert pulses[3].start, 2.0)
    assert pulses[3].stop, 2.5)
    assert pulses[3].duration, 0.5)
    assert_is(pulses[4], pulse5)
    assert pulses[4].start, 3.0)
    assert pulses[4].stop, 3.5)
    assert pulses[4].duration, 0.5)

def test_conditional_sequence_compilation2(root):
    # Test compiling a conditional sequence whose condition evaluates to
    # True.
    root.external_vars = {'a': 1.5, 'include': False}

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = Sequence(items=[pulse3])
    sequence1 = ConditionalSequence(items=[pulse2, sequence2, pulse4],
                                    condition='{include}')

    root.items = [pulse1, sequence1, pulse5]

    res, pulses = root.compile_sequence(False)
    assert_true(res)
    assert len(pulses), 2)
    assert_is(pulses[0], pulse1)
    assert pulses[0].start, 1.0)
    assert pulses[0].stop, 2.0)
    assert pulses[0].duration, 1.0)
    assert_is(pulses[1], pulse5)
    assert pulses[1].start, 3.0)
    assert pulses[1].stop, 3.5)
    assert pulses[1].duration, 0.5)

def test_conditional_sequence_compilation3(root):
    # Test compiling a conditional sequence with a wrong condition.
    root.external_vars = {'a': 1.5, 'include': False}

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = Sequence(items=[pulse3])
    sequence1 = ConditionalSequence(items=[pulse2, sequence2, pulse4],
                                    condition='{include}*/')

    root.items = [pulse1, sequence1, pulse5]

    res, (missings, errors) = root.compile_sequence(False)
    assert_false(res)
    assert_in('2_condition', errors)
