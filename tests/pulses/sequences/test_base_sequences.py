# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test for the handling of indexing b sequences.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from collections import OrderedDict

from exopy_pulses.pulses.pulse import Pulse
from exopy_pulses.pulses.sequences.base_sequences\
    import RootSequence, BaseSequence
from exopy_pulses.pulses.shapes.square_shape import SquareShape
from exopy_pulses.testing.context import TestContext


def add_children(seq, children):
    """Add a sequence of item to a BaseSequence.

    """
    for i, c in enumerate(children):
        seq.add_child_item(i, c)


def test_sequence_time_constaints_observation():
    """Test observation of time constraint by the root.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context
    sequence = BaseSequence()
    root.add_child_item(0, sequence)

    assert root.global_vars == []

    sequence.time_constrained = True

    assert (sorted(root.global_vars) ==
            sorted(['1_start', '1_stop', '1_duration']))

    sequence.time_constrained = False

    assert root.global_vars == []

    root.time_constrained = True
    assert root.linkable_vars


def test_root_handling():
    """Test updating of item when a sequence get/lose the root.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context
    sequence1 = BaseSequence()
    sequence2 = BaseSequence()
    pulse = Pulse()

    sequence2.add_child_item(0, pulse)
    sequence1.add_child_item(0, sequence2)
    root.add_child_item(0, sequence1)

    assert pulse.root is root and sequence2.root is root
    assert sequence2.has_observers('_last_index')

    root.remove_child_item(0)
    assert pulse.root is None and sequence2.root is None
    assert not sequence2.has_observers('_last_index')


def test_get_accessible_vars():
    """Test getting the accessible vars of a sequence.

    """
    root = RootSequence(external_vars=OrderedDict({'a': 1}),
                        local_vars=OrderedDict({'a2': '5'}),
                        time_constrained=True)
    context = TestContext()
    root.context = context
    sequence1 = BaseSequence(local_vars=OrderedDict({'b': '1'}))
    sequence2 = BaseSequence(local_vars=OrderedDict({'c': '2'}))
    pulse = Pulse()

    sequence2.add_child_item(0, pulse)
    sequence1.add_child_item(0, sequence2)
    root.add_child_item(0, sequence1)

    variables = ['sequence_end', 'a', 'a2', '3_start', '3_stop',
                 '3_duration', 'b', 'c']
    lv = sequence2.get_accessible_vars()
    for v in variables:
        assert v in lv

    variables.pop()
    lv = sequence1.get_accessible_vars()
    for v in variables:
        assert v in lv

    variables.pop()
    lv = root.get_accessible_vars()
    for v in variables:
        assert v in lv


def test_update_preferences():
    """Test that update preferences does update the items too.

    """
    sequence = BaseSequence()
    sequence.add_child_item(0, Pulse())
    sequence.update_members_from_preferences({'time_constrained': 'True',
                                              'item_0': {'def_1': '10'}})
    assert sequence.time_constrained
    assert sequence.items[0].def_1 == '10'


def test_sequence_indexing1():
    """Test adding, moving, deleting pulse in a sequence.

    """
    root = RootSequence()
    root.time_constrained = True
    root.sequence_duration = '1.0'
    context = TestContext()
    root.context = context

    pulse1 = Pulse()
    pulse2 = Pulse()
    pulse3 = Pulse()

    root.add_child_item(0, pulse1)
    assert pulse1.index == 1
    assert pulse1.root is root
    assert (sorted(root.get_accessible_vars()) ==
            (sorted(['sequence_end', '1_start', '1_stop', '1_duration'])))

    root.add_child_item(1, pulse2)
    assert pulse1.index == 1
    assert pulse2.index == 2
    assert pulse2.root is root
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['sequence_end', '1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration']))

    root.move_child_item(0, 1)
    assert pulse1.index == 2
    assert pulse2.index == 1
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['sequence_end', '1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration']))

    root.move_child_item(0, 1)

    root.add_child_item(2, pulse3)
    assert pulse1.index == 1
    assert pulse2.index == 2
    assert pulse3.index == 3
    assert pulse3.root is root
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['sequence_end', '1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration',
                    '3_start', '3_stop', '3_duration']))

    root.time_constrained = False
    root.remove_child_item(1)
    assert pulse1.index == 1
    assert pulse2.index == 0
    assert pulse3.index == 2
    assert pulse2.root is None
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration']))

    root.add_child_item(1, pulse2)
    assert pulse1.index == 1
    assert pulse2.index == 2
    assert pulse3.index == 3
    assert pulse2.root is root
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '2_start', '2_stop', '2_duration',
                    '3_start', '3_stop', '3_duration']))


def test_sequence_indexing2():
    """Test adding, moving, deleting a sequence in a sequence.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context

    pulse1 = Pulse()
    pulse2 = Pulse()
    pulse3 = Pulse()
    pulse4 = Pulse()

    sequence1 = BaseSequence()
    sequence2 = BaseSequence()

    root.add_child_item(0, pulse1)
    root.add_child_item(1, sequence1)
    root.add_child_item(2, pulse2)

    assert sequence1.parent is root
    assert sequence1.root is root

    sequence1.add_child_item(0, sequence2)

    assert sequence2.parent is sequence1
    assert sequence2.root is root
    assert pulse1.index == 1
    assert pulse2.index == 4
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '4_start', '4_stop', '4_duration']))

    pulse1.index = 200
    sequence2.add_child_item(0, pulse3)

    assert pulse3.parent is sequence2
    assert pulse3.root is root
    assert pulse2.index == 5
    assert pulse3.index == 4
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '4_start', '4_stop', '4_duration',
                    '5_start', '5_stop', '5_duration']))

    # Check that only the pulse below the modified sequence are updated.
    assert pulse1.index == 200
    pulse1.index = 0

    sequence1.add_child_item(0, pulse4)

    assert pulse4.index == 3
    assert sequence2.index == 4
    assert pulse3.index == 5
    assert pulse2.index == 6
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '3_start', '3_stop', '3_duration',
                    '5_start', '5_stop', '5_duration',
                    '6_start', '6_stop', '6_duration']))

    sequence1.remove_child_item(1)

    assert sequence2.parent is None
    assert sequence2.index == 0
    assert pulse2.index == 4
    assert (sorted(root.get_accessible_vars()) ==
            sorted(['1_start', '1_stop', '1_duration',
                    '3_start', '3_stop', '3_duration',
                    '4_start', '4_stop', '4_duration']))

    sequence1.index = 200
    root2 = RootSequence()
    sequence2.root = root2
    while True:
        sequence2.remove_child_item(0)
        if not sequence2.items:
            break

    # Check the observer was properly removed
    assert sequence1.index == 200


def test_traverse_sequence():
    """Test traversing a pulse sequence.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10',
                   kind='Analogical', shape=SquareShape())
    pulse4 = Pulse(def_1='{2_stop} + 0.5', def_2='10',
                   kind='Analogical', shape=SquareShape())
    seq = BaseSequence()
    add_children(root, [pulse1, pulse2, pulse3, seq])
    add_children(seq, [pulse4])

    items = root.traverse()
    assert len(list(items)) == 11

    assert list(root.traverse(0)) == [root, pulse1, pulse2, pulse3, seq,
                                      context]


def test_build_from_config():
    """Test building a pulse sequence.

    """
    root = RootSequence()
    context = TestContext()
    root.context = context
    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10',
                   kind='Analogical', shape=SquareShape())
    pulse4 = Pulse(def_1='{2_stop} + 0.5', def_2='10',
                   kind='Analogical', shape=SquareShape())
    seq = BaseSequence()
    add_children(root, [pulse1, pulse2, pulse3, seq])
    add_children(seq, [pulse4])

    pref = root.preferences_from_members()
    dependecies = {'exopy.pulses.item':
                   {'exopy_pulses.BaseSequence': BaseSequence,
                    'exopy_pulses.Pulse': Pulse},
                   'exopy.pulses.shape':
                   {'exopy_pulses.SquareShape': SquareShape},
                   'exopy.pulses.context':
                   {'exopy_pulses.TestContext': TestContext}}

    aux = RootSequence.build_from_config(pref, dependecies)
    assert aux.external_vars == {'a': 1.5}
    assert len(aux.items) == 4
    assert isinstance(aux.context, TestContext)

    pulse1 = aux.items[0]
    assert pulse1.parent
    assert pulse1.def_1 == '1.0'
    assert pulse1.def_2 == '{a}'

    pulse2 = aux.items[1]
    assert pulse2.parent
    assert pulse2.def_1 == '{a} + 1.0'
    assert pulse2.def_2 == '3.0'

    pulse3 = aux.items[2]
    assert pulse3.parent
    assert pulse3.def_1 == '{2_stop} + 0.5'
    assert pulse3.def_2 == '10'
    assert pulse3.kind == 'Analogical'
    assert isinstance(pulse3.shape, SquareShape)

    seq = aux.items[3]
    assert seq.parent
    assert len(seq.items) == 1
