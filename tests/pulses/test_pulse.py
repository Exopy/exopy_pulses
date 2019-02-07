# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test evaluation of pulses entries.

"""
import pytest
import numpy as np
from numpy.testing import assert_array_equal

from exopy_pulses.pulses.pulse import Pulse
from exopy_pulses.pulses.sequences.base_sequences import RootSequence
from exopy_pulses.pulses.shapes.square_shape import SquareShape
from exopy_pulses.testing.context import DummyContext


@pytest.fixture
def pulse():
    return Pulse(root=RootSequence(context=DummyContext()))


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


def test_eval_pulse1bis(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Stop mode, zero duration.

    """
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '2.0'

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert pulse.eval_entries(root_vars, seq_locals, missing, errors)

    assert missing == set()
    assert errors == {}
    assert root_vars['0_start'] == 2.0
    assert root_vars['0_stop'] == 2.0
    assert root_vars['0_duration'] == 0.0
    assert seq_locals['0_start'] == 2.0
    assert seq_locals['0_stop'] == 2.0
    assert seq_locals['0_duration'] == 0.0
    assert pulse.start == 2.0
    assert pulse.stop == 2.0
    assert pulse.duration == 0.0
    assert_array_equal(pulse.waveform, np.ones(0))


def test_eval_pulse_validation_fail(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Stop mode, meaningless start.

    """
    pulse.root.context.rectify_time = False
    pulse.def_1 = '1.0*2.1'
    pulse.def_2 = '5.1*{a}/{b} + {c}'

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


def test_eval_pulse5bis(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Start/Duration mode, 0 duration.

    """
    pulse.def_mode = 'Start/Duration'
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '0'

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert pulse.eval_entries(root_vars, seq_locals,
                              missing, errors)

    assert missing == set()
    assert errors == {}
    assert root_vars['0_start'] == 2.0
    assert root_vars['0_stop'] == 2.0
    assert root_vars['0_duration'] == 0.0
    assert seq_locals['0_start'] == 2.0
    assert seq_locals['0_stop'] == 2.0
    assert seq_locals['0_duration'] == 0.0
    assert pulse.start == 2.0
    assert pulse.stop == 2.0
    assert pulse.duration == 0
    assert_array_equal(pulse.waveform, np.ones(0))


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

    root_vars = {'a': -1.0, 'b': 10.0, 'c': 0.0}
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


def test_eval_pulse8bis(pulse):
    """Test evaluating the entries of a pulse when everything is ok.
    Duration/Stop mode, zero duration.

    """
    pulse.def_mode = 'Duration/Stop'
    pulse.def_1 = '0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    seq_locals = root_vars.copy()
    assert pulse.eval_entries(root_vars, seq_locals,
                              missing, errors)

    assert missing == set()
    assert errors == {}
    assert root_vars['0_start'] == 3.0
    assert root_vars['0_stop'] == 3.0
    assert root_vars['0_duration'] == 0.0
    assert seq_locals['0_start'] == 3.0
    assert seq_locals['0_stop'] == 3.0
    assert seq_locals['0_duration'] == 0.0
    assert pulse.start == 3.0
    assert pulse.stop == 3.0
    assert pulse.duration == 0.0
    assert_array_equal(pulse.waveform, np.ones(0))


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
    pulse.index = 2
    pulse.def_1 = '1.0*2.0'
    pulse.def_2 = '5.0*{a}/{b} + {c}'

    pulse.shape = SquareShape(amplitude='0.5')
    pulse.kind = 'Analogical'

    pulse.modulation.frequency = '0.0'
    pulse.modulation.phase = '0.0'
    pulse.modulation.kind = 'cos'
    pulse.modulation.activated = True

    root_vars = {'a': 2.0, 'b': 5.0, 'c': 1.0}
    missing = set()
    errors = {}

    assert pulse.eval_entries(root_vars, root_vars,
                              missing, errors)

    assert missing == set()
    assert errors == {}
    assert_array_equal(pulse.waveform, 0.5*np.ones(1))
    assert pulse.shape.index == 2

    pulse.clean_cached_values()
    assert not pulse.modulation._cache
    assert not pulse.shape._cache


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
    assert '0_modulation_frequency' in errors


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


def test_traversing_pulse(pulse):
    """Test traversing a pulse.

    """
    assert list(pulse.traverse()) == [pulse]

    pulse.kind = 'Analogical'
    assert list(pulse.traverse()) == [pulse, pulse.modulation]

    pulse.shape = SquareShape()
    assert list(pulse.traverse()) == [pulse, pulse.modulation, pulse.shape]


def test_pulse_view(exopy_qtbot, workbench, pulse, dialog_sleep):
    """Test the view of the Pulse class.

    """
    import enaml
    from exopy.testing.util import show_widget
    with enaml.imports():
        from exopy_pulses.pulses.sequences.views.base_sequences_views\
            import RootSequenceView

    pulse.kind = 'Analogical'
    root = pulse.root
    root.add_child_item(0, pulse)
    core = workbench.get_plugin('enaml.workbench.core')
    root_view = RootSequenceView(item=root, core=core)
    pulse_view = root_view.view_for(pulse)
    show_widget(exopy_qtbot, root_view)
    exopy_qtbot.wait(dialog_sleep)

    # Test swithcing between logical and analogical
    widgets_num = len(pulse_view.widgets())
    pulse.kind = 'Logical'

    def assert_widgets():
        assert widgets_num - 1 == len(pulse_view.widgets())
    exopy_qtbot.wait_until(assert_widgets)
    exopy_qtbot.wait(dialog_sleep)

    pulse.kind = 'Analogical'

    def assert_widgets():
        assert widgets_num == len(pulse_view.widgets())
    exopy_qtbot.wait_until(assert_widgets)
    exopy_qtbot.wait(dialog_sleep)

    # Test selecting a shape
    shape_select = pulse_view.widgets()[-1].widgets()[-1]
    shape_select.selected = 'exopy_pulses.SquareShape'

    def assert_widgets():
        assert widgets_num + 1 == len(pulse_view.widgets())
    exopy_qtbot.wait_until(assert_widgets)
    exopy_qtbot.wait(dialog_sleep)

    shape_select.selected = ''

    def assert_widgets():
        assert widgets_num == len(pulse_view.widgets())
    exopy_qtbot.wait_until(assert_widgets)
    exopy_qtbot.wait(dialog_sleep)

    # Test adding a modulation
    mod_check = pulse_view.widgets()[-1].widgets()[0]
    mod_check.checked = True

    def assert_widgets():
        assert widgets_num + 1 == len(pulse_view.widgets())
    exopy_qtbot.wait_until(assert_widgets)
    exopy_qtbot.wait(dialog_sleep)
    mod_check.checked = False

    def assert_widgets():
        assert widgets_num == len(pulse_view.widgets())
    exopy_qtbot.wait_until(assert_widgets)
    exopy_qtbot.wait(dialog_sleep)


def test_pulse_view2(exopy_qtbot, workbench, pulse):
    """Test showing a pulse logical at the start.

    """
    import enaml
    from exopy.testing.util import show_and_close_widget
    with enaml.imports():
        from exopy_pulses.pulses.sequences.views.base_sequences_views\
            import RootSequenceView

    pulse.kind = 'Logical'
    root = pulse.root
    root.add_child_item(0, pulse)
    core = workbench.get_plugin('enaml.workbench.core')
    root_view = RootSequenceView(item=root, core=core)
    show_and_close_widget(exopy_qtbot, root_view)


def test_pulse_view3(exopy_qtbot, workbench, pulse):
    """Test showing a pulse with a shape at the start at the start.

    """
    import enaml
    from exopy.testing.util import show_and_close_widget
    with enaml.imports():
        from exopy_pulses.pulses.sequences.views.base_sequences_views\
            import RootSequenceView

    pulse.kind = 'Analogical'
    pulse.shape = SquareShape()
    root = pulse.root
    root.add_child_item(0, pulse)
    core = workbench.get_plugin('enaml.workbench.core')
    root_view = RootSequenceView(item=root, core=core)
    show_and_close_widget(exopy_qtbot, root_view)
