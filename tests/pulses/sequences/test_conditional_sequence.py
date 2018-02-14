# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the conditional sequence evaluation and simplification.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from collections import OrderedDict

from exopy_pulses.pulses.pulse import Pulse
from exopy_pulses.pulses.sequences.base_sequences import BaseSequence
from exopy_pulses.pulses.sequences.conditional_sequence\
     import ConditionalSequence

from .test_eval_simplify_sequences import root, add_children


def test_conditional_sequence_compilation1(root):
    """Test compiling a conditional sequence whose condition evaluates to
    True.

    """
    root.external_vars = OrderedDict({'a': 1.5, 'include': True})

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence()
    sequence2.add_child_item(0, pulse3)
    sequence1 = ConditionalSequence(condition='{include}')
    add_children(sequence1, [pulse2, sequence2, pulse4])

    add_children(root, [pulse1, sequence1, pulse5])

    res, missings, errors = root.evaluate_sequence()
    print(missings, errors)
    assert res
    pulses = root.simplify_sequence()
    assert res
    assert len(pulses) == 5
    assert pulses[0] is pulse1
    assert pulses[0].start == 1.0
    assert pulses[0].stop == 2.0
    assert pulses[0].duration == 1.0
    assert pulses[1] is pulse2
    assert pulses[1].start, 2.5
    assert pulses[1].stop, 3.0
    assert pulses[1].duration, 0.5
    assert pulses[2] is pulse3
    assert pulses[2].start, 3.5
    assert pulses[2].stop, 10.0
    assert pulses[2].duration, 6.5
    assert pulses[3] is pulse4
    assert pulses[3].start, 2.0
    assert pulses[3].stop, 2.5
    assert pulses[3].duration, 0.5
    assert pulses[4] is pulse5
    assert pulses[4].start, 3.0
    assert pulses[4].stop, 3.5
    assert pulses[4].duration, 0.5


def test_conditional_sequence_compilation2(root):
    """Test compiling a conditional sequence whose condition evaluates to
    False.

    """
    root.external_vars = OrderedDict({'a': 1.5, 'include': False})

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence()
    sequence2.add_child_item(0, pulse3)
    sequence1 = ConditionalSequence(condition='{include}')
    add_children(sequence1, [pulse2, sequence2, pulse4])

    add_children(root, [pulse1, sequence1, pulse5])

    res, missings, errors = root.evaluate_sequence()
    assert res
    pulses = root.simplify_sequence()
    assert len(pulses), 2
    assert pulses[0] is pulse1
    assert pulses[0].start, 1.0
    assert pulses[0].stop, 2.0
    assert pulses[0].duration, 1.0
    assert pulses[1] is pulse5
    assert pulses[1].start, 3.0
    assert pulses[1].stop, 3.5
    assert pulses[1].duration, 0.5


def test_conditional_sequence_compilation3(root):
    """Test compiling a conditional sequence with a wrong condition.

    """
    root.external_vars = OrderedDict({'a': 1.5, 'include': False})

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='3.0', def_2='0.5', def_mode='Start/Duration')

    sequence2 = BaseSequence()
    sequence2.add_child_item(0, pulse3)
    sequence1 = ConditionalSequence(condition='{include}*/')
    add_children(sequence1, [pulse2, sequence2, pulse4])

    add_children(root, [pulse1, sequence1, pulse5])

    res, missings, errors = root.evaluate_sequence()
    assert not res
    assert '2_condition' in errors


def test_conditional_sequence_view(windows, workbench, root,
                                   process_and_sleep):
    """Test the view of the Pulse class.

    """
    import enaml
    from exopy.testing.util import show_and_close_widget
    with enaml.imports():
        from exopy_pulses.pulses.sequences.views.base_sequences_views\
            import RootSequenceView

    core = workbench.get_plugin('enaml.workbench.core')
    root.add_child_item(0, ConditionalSequence())
    show_and_close_widget(RootSequenceView(item=root, core=core))
