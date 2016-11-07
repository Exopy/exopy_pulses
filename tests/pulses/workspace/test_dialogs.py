# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the workspace dialogs.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest
import enaml
from enaml.colors import parse_color

from ecpy_pulses.pulses.pulse import Pulse
from ecpy_pulses.pulses.sequences.base_sequences\
    import RootSequence, BaseSequence

from ecpy_pulses.testing.context import TestContext
with enaml.imports():
    from ecpy_pulses.pulses.workspace.dialogs import (CompileDialog,
                                                      _VarValidator)


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


def test_var_validator():
    """Test the variable validator.

    """
    v = _VarValidator()
    assert v.validate('1')
    assert not v.validate('1*')


def test_compiling_a_working_sequence(workspace, root, process_and_sleep,
                                      windows):
    """Test using the dialog to compile a working sequence.

    """
    workbench = workspace.workbench
    ui = workbench.get_plugin('enaml.workbench.ui')
    ui.show_window()
    process_and_sleep()

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

    workspace.state.sequence = root

    dial = CompileDialog(workspace=workspace)
    dial.show()
    process_and_sleep()
    comp_widget = dial.central_widget().widgets()[0]

    comp_widget.widgets()[-1].clicked = True
    process_and_sleep()

    assert comp_widget.elapsed_time
    assert not comp_widget.errors
    assert comp_widget.widgets()[-2].background == parse_color('green')


def test_compiling_a_sequence_not_compiling(workspace, process_and_sleep, root,
                                            windows):
    """Test compiling that cannot compile as the sequence does not evaluate.

    """
    workbench = workspace.workbench
    ui = workbench.get_plugin('enaml.workbench.ui')
    ui.show_window()
    process_and_sleep()

    root.external_vars = OrderedDict({'a': 1.5})

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a + {b} + 1.0', def_2='3.0')
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

    workspace.state.sequence = root

    dial = CompileDialog(workspace=workspace)
    dial.show()
    process_and_sleep()
    comp_widget = dial.central_widget().widgets()[0]

    comp_widget.widgets()[-1].clicked = True
    process_and_sleep()

    assert comp_widget.elapsed_time
    assert comp_widget.errors
    assert comp_widget.widgets()[-2].background == parse_color('red')


def test_compiling_a_sequence_not_compiling2(workspace, root, monkeypatch,
                                             process_and_sleep, windows):
    """Test compiling a sequence that can be evaluated but not compiled.

    """
    def __raise(*args, **kwargs):
        return False, {}, {'test': False}
    from ecpy_pulses.testing.context import TestContext
    monkeypatch.setattr(TestContext, 'compile_and_transfer_sequence',
                        __raise)
    workbench = workspace.workbench
    ui = workbench.get_plugin('enaml.workbench.ui')
    ui.show_window()
    process_and_sleep()

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

    workspace.state.sequence = root

    dial = CompileDialog(workspace=workspace)
    dial.show()
    process_and_sleep()
    comp_widget = dial.central_widget().widgets()[0]

    comp_widget.widgets()[-1].clicked = True
    process_and_sleep()

    assert comp_widget.elapsed_time
    assert comp_widget.errors
    assert comp_widget.widgets()[-2].background == parse_color('red')
