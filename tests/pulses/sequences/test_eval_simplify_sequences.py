# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test evaluating and simplifying base sequences

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from collections import OrderedDict

import pytest

from ecpy_pulses.pulses.pulse import Pulse
from ecpy_pulses.pulses.shapes.square_shape import SquareShape
from ecpy_pulses.pulses.sequences.base_sequences\
    import RootSequence, BaseSequence

from ecpy_pulses.testing.context import TestContext


@pytest.fixture
def root():
    root = RootSequence()
    context = TestContext(sampling=0.5)
    root.context = context
    return root


def add_children(seq, children):
    """Add a sequence of item to a BaseSequence.

    """
    for i, c in enumerate(children):
        seq.add_child_item(i, c)


def test_sequence_compilation1(root):
    """Test compiling a flat sequence.

    """
    root.external_vars = OrderedDict({'a': 1.5})
    root.local_vars = OrderedDict({'b': '2*{a}'})

    pulse1 = Pulse(def_1='1.0', def_2='{a}', kind='Analogical',
                   shape=SquareShape(amplitude='0.5',
                                     _cache={'amplitude': 1.0}))
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10 + {b}')
    add_children(root, (pulse1, pulse2, pulse3))

    res, missings, errors = root.evaluate_sequence()
    print(errors)
    pulses = root.items
    assert res
    assert len(pulses) == 3
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 1.5
    assert pulses[0].duration == 0.5
    assert pulses[0].shape._cache['amplitude'] == 0.5
    assert pulses[1].start == 2.5
    assert pulses[1].stop == 3.0
    assert pulses[1].duration == 0.5
    assert pulses[2].start == 3.5
    assert pulses[2].stop == 13.0
    assert pulses[2].duration == 9.5


def test_sequence_compilation1bis(root):
    """Compiles two times a sequence while changing a parameter to make
    sure the cache is cleaned in between

    Also validate that the context cache is cleaned

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='4.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10')
    add_children(root, (pulse1, pulse2, pulse3))

    res, _, _ = root.evaluate_sequence()
    pulses = root.items
    context = root.context
    assert not context._cache
    context._cache = {'a': 1}
    assert res
    assert len(pulses) == 3
    assert pulses[0].stop == 1.5

    root.external_vars = OrderedDict({'a': 2.})
    res = root.evaluate_sequence()
    pulses = root.items
    context = root.context
    assert not context._cache
    assert res
    assert len(pulses) == 3
    assert pulses[0].stop == 2.


def test_sequence_compilation2(root):
    """Test compiling a flat sequence of fixed duration.

    """
    root.external_vars = OrderedDict({'a': 1.5})
    root.time_constrained = True
    root.sequence_duration = '10.0'

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='{sequence_end}')
    add_children(root, (pulse1, pulse2, pulse3))

    res, missings, errors = root.evaluate_sequence()
    print(errors)
    pulses = root.items
    assert res
    assert len(pulses) == 3
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 1.5
    assert pulses[0].duration == 0.5
    assert pulses[1].start == 2.5
    assert pulses[1].stop == 3.0
    assert pulses[1].duration == 0.5
    assert pulses[2].start == 3.5
    assert pulses[2].stop == 10.0
    assert pulses[2].duration == 6.5


def test_sequence_compilation2bis(root):
    """Test compiling a flat sequence of fixed duration but with a pulse
    stopping too late.

    """
    root.external_vars = OrderedDict({'a': 1.5})
    root.time_constrained = True
    root.sequence_duration = '10.0'

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='{sequence_end} + 1')
    add_children(root, (pulse1, pulse2, pulse3))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert 'root-stop' in errors


def test_sequence_compilation3(root):
    """Test compiling a flat sequence in two passes.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{2_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10')
    add_children(root, (pulse1, pulse2, pulse3))

    res, _, _ = root.evaluate_sequence()
    pulses = root.items
    assert res
    assert len(pulses) == 3
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 1.5
    assert pulses[0].duration == 0.5
    assert pulses[1].start == 2.5
    assert pulses[1].stop == 3.0
    assert pulses[1].duration == 0.5
    assert pulses[2].start == 3.5
    assert pulses[2].stop == 10.0
    assert pulses[2].duration == 6.5


def test_sequence_compilation4(root):
    """Test compiling a flat sequence with circular references.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{2_start} - 1.0')
    pulse2 = Pulse(def_1='{1_stop} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10')
    add_children(root, (pulse1, pulse2, pulse3))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert len(missings) == 2
    assert '1_stop' in missings
    assert '2_start' in missings
    assert len(errors) == 0


def test_sequence_compilation5(root):
    """Test compiling a flat sequence with evaluation errors.
    missing global

    """
    root.time_constrained = True
    root.sequence_duration = '10.0'

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='{sequence_end}')
    add_children(root, (pulse1, pulse2, pulse3))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert len(missings) == 1
    assert 'a' in missings
    assert len(errors) == 0


def test_sequence_compilation6(root):
    """Test compiling a flat sequence with evaluation errors.
    wrong string value

    """
    root.external_vars = OrderedDict({'a': 1.5})
    root.time_constrained = True
    root.sequence_duration = '*10.0*'

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} +* 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10.0')
    add_children(root, (pulse1, pulse2, pulse3))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert not missings
    assert len(errors) == 2
    assert '2_start' in errors
    assert 'root_seq_duration' in errors


def test_sequence_compilation6bis(root):
    """Test compiling a flat sequence with evaluation errors.
    local vars of root

    """
    root.time_constrained = True
    root.sequence_duration = '10.0'
    root.external_vars = OrderedDict({'a': 1.5})
    root.local_vars = OrderedDict({'b': '2*{a}+', 'c': '{dummy}'})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='{sequence_end}')
    add_children(root, (pulse1, pulse2, pulse3))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert 'dummy' in missings
    assert 'root_b' in errors


def test_sequence_compilation6ter(root):
    """Test compiling a flat sequence with evaluation errors.
    wrong string value

    """
    root.external_vars = OrderedDict({'a': 1.5})
    root.time_constrained = True
    root.sequence_duration = '10.0*{dummy}'

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} +* 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10.0')
    add_children(root, (pulse1, pulse2, pulse3))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert 'dummy' in missings
    assert len(errors) == 1
    assert '2_start' in errors


def test_sequence_compilation7(root):
    """Test compiling a nested sequence with a disabled item

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse3bis = Pulse(def_1='{3_stop} + 0.5', def_2='10.0', enabled=False)
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence()
    add_children(sequence2, (pulse3, pulse3bis))
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    pulses = root.simplify_sequence()
    assert res
    assert len(pulses) == 5
    assert pulses[0] is pulse1
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 1.5
    assert pulses[0].duration == 0.5
    assert pulses[1] is pulse2
    assert pulses[1].start == 2.5
    assert pulses[1].stop == 3.0
    assert pulses[1].duration == 0.5
    assert pulses[2] is pulse3
    assert pulses[2].start == 3.5
    assert pulses[2].stop == 10.0
    assert pulses[2].duration == 6.5
    assert pulses[3] is pulse4
    assert pulses[3].start == 2.0
    assert pulses[3].stop == 2.5
    assert pulses[3].duration == 0.5
    assert pulses[4] is pulse5
    assert pulses[4].start == 3.0
    assert pulses[4].stop == 3.5
    assert pulses[4].duration == 0.5


def test_sequence_compilation8(root):
    """Test compiling a nested sequence in two passes on the external
    sequence.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence()
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    pulses = root.simplify_sequence()
    assert res
    assert len(pulses) == 5
    assert pulses[0] is pulse1
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 2.0
    assert pulses[0].duration == 1.0
    assert pulses[1] is pulse2
    assert pulses[1].start == 2.5
    assert pulses[1].stop == 3.0
    assert pulses[1].duration == 0.5
    assert pulses[2] is pulse3
    assert pulses[2].start == 3.5
    assert pulses[2].stop == 10.0
    assert pulses[2].duration == 6.5
    assert pulses[3] is pulse4
    assert pulses[3].start == 2.0
    assert pulses[3].stop == 2.5
    assert pulses[3].duration == 0.5
    assert pulses[4] is pulse5
    assert pulses[4].start == 3.0
    assert pulses[4].stop == 3.5
    assert pulses[4].duration == 0.5


def test_sequence_compilation9(root):
    """Test compiling a nested sequence in multi passes.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='{6_start} + 1.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence()
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    pulses = root.simplify_sequence()
    assert res
    assert len(pulses) == 5
    assert pulses[0] is pulse1
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 2.0
    assert pulses[0].duration == 1.0
    assert pulses[1] is pulse2
    assert pulses[1].start == 2.5
    assert pulses[1].stop == 3.0
    assert pulses[1].duration == 0.5
    assert pulses[2] is pulse3
    assert pulses[2].start == 3.5
    assert pulses[2].stop == 10.0
    assert pulses[2].duration == 6.5
    assert pulses[3] is pulse4
    assert pulses[3].start == 2.0
    assert pulses[3].stop == 2.5
    assert pulses[3].duration == 0.5
    assert pulses[4] is pulse5
    assert pulses[4].start == 3.0
    assert pulses[4].stop == 3.5
    assert pulses[4].duration == 0.5


def test_sequence_compilation10(root):
    """Test compiling a nested sequence with circular reference in the deep
    one.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='{6_start} + 1.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='{1_stop}', def_2='0.5',
                   def_mode='Start/Duration')

    sequence2 = BaseSequence()
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert len(missings) == 2
    assert '7_start' in missings
    assert '1_stop' in missings
    assert not errors


def test_sequence_compilation11(root):
    """Test compiling a nested sequence with circular reference in the deep
    one.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='{6_start} + 1.0')
    pulse3 = Pulse(def_1='{3_stop} + *0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence()
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert len(errors) == 1
    assert '5_start' in errors


def test_sequence_compilation12(root):
    """Test compiling a nested sequence using local vars.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='{b}')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence(local_vars=OrderedDict({'b': '2**2'}))
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    print(missings, errors)
    pulses = root.simplify_sequence()
    assert res
    assert len(pulses) == 5
    assert pulses[0] is pulse1
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 1.5
    assert pulses[0].duration == 0.5
    assert pulses[1] is pulse2
    assert pulses[1].start == 2.5
    assert pulses[1].stop == 3.0
    assert pulses[1].duration == 0.5
    assert pulses[2] is pulse3
    assert pulses[2].start == 3.5
    assert pulses[2].stop == 4
    assert pulses[2].duration == 0.5
    assert pulses[3] is pulse4
    assert pulses[3].start == 2.0
    assert pulses[3].stop == 2.5
    assert pulses[3].duration == 0.5
    assert pulses[4] is pulse5
    assert pulses[4].start == 3.0
    assert pulses[4].stop == 3.5
    assert pulses[4].duration == 0.5


def test_sequence_compilation13(root):
    """Test compiling a nested sequence with wrong local vars definitions.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='{b}')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence(local_vars=OrderedDict({'b': '2**',
                                                     'c': '{dummy}'}))
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert len(missings) == 2
    assert 'b' in missings
    assert 'dummy' in missings
    assert '4_b' in errors


def test_sequence_compilation14(root):
    """Test the locality of local vars.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='{b}')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='{b}', def_mode='Start/Duration')

    sequence2 = BaseSequence(local_vars=OrderedDict({'b': '2**2'}))
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert len(missings) == 1
    assert 'b' in missings
    assert not errors


# No test of the evaluation errors on the defs as this is handled
# at the Item level and tested in the test of the Pulses.

def test_sequence_compilation15(root):
    """Test compiling a nested sequence with internal fixed length.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{4_start} + 0.5',
                   def_2='{4_start}+{4_duration}-0.5')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence(time_constrained=True,
                             def_1='{3_stop} + 0.5', def_2='6')
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    pulses = root.simplify_sequence()
    assert res
    assert len(pulses) == 5
    assert pulses[0] is pulse1
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 1.5
    assert pulses[0].duration == 0.5
    assert pulses[1] is pulse2
    assert pulses[1].start == 2.5
    assert pulses[1].stop == 3.0
    assert pulses[1].duration == 0.5
    assert pulses[2] is pulse3
    assert pulses[2].start == 4
    assert pulses[2].stop == 5.5
    assert pulses[2].duration == 1.5
    assert pulses[3] is pulse4
    assert pulses[3].start == 2.0
    assert pulses[3].stop == 2.5
    assert pulses[3].duration == 0.5
    assert pulses[4] is pulse5
    assert pulses[4].start == 3.0
    assert pulses[4].stop == 3.5
    assert pulses[4].duration == 0.5


def test_sequence_compilation16(root):
    """Test compiling a nested sequence with internal fixed length but
    incoherent pulse start.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{4_start} - 0.5',
                   def_2='{4_start}+{4_duration}-0.5')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence(time_constrained=True,
                             def_1='{3_stop} + 0.5', def_2='6',
                             name='test')
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert 'test-start' in errors


def test_sequence_compilation17(root):
    """Test compiling a nested sequence with internal fixed length but
    incoherent pulse stop.

    """
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{4_start} + 0.5',
                   def_2='{4_start}+{4_duration}+0.5')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence(time_constrained=True,
                             def_1='{3_stop} + 0.5', def_2='6',
                             name='test')
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))

    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert not missings
    assert 'test-stop' in errors


def test_sequence_compilation18(root):
    """Test compiling a nested fixed duration sequence.

    """
    root.external_vars = OrderedDict({'a': 1.5})
    root.time_constrained = True
    root.sequence_duration = '100'

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{4_start} + 0.5',
                   def_2='{4_start}+{4_duration}-0.5')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence(time_constrained=True,
                             def_1='{3_stop} + 0.5', def_2='6',
                             name='test')
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    add_children(sequence1, (pulse2, sequence2, pulse4))
    add_children(root, (pulse1, sequence1, pulse5))

    res, missings, errors = root.evaluate_sequence()
    print(errors)
    assert res

    root.sequence_duration = '1'
    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert 'root-stop' in errors
