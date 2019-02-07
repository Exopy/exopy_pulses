# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test for the slope shape.

"""
import enaml
import numpy as np
from numpy.testing import assert_array_equal

from exopy_pulses.pulses.pulse import Pulse
from exopy_pulses.pulses.sequences.base_sequences import RootSequence
from exopy_pulses.testing.context import TestingContext
from exopy_pulses.pulses.shapes.slope_shape import SlopeShape


def test_eval_start_stop():
    """Test evaluating the slope shape in start/stop mode.

    """
    shape = SlopeShape(mode='Start/Stop', def1='0.5', def2='{a}')
    root_vars = {'a': -1.0}
    missing = set()
    errors = {}

    assert shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert errors == {}
    assert_array_equal(shape.compute(np.linspace(0, 1, 11), 'mus'),
                       np.linspace(0.5, -1.0, 11))


def test_eval_start_slope():
    """Test evaluating the slope shape in start/slope mode.

    """
    shape = SlopeShape(mode='Start/Slope', def1='{a}', def2='-0.5',
                       index=1)
    root_vars = {'a': 0, '1_duration': 1}
    missing = set()
    errors = {}

    assert shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert errors == {}
    assert_array_equal(shape.compute(np.ones(11), 'mus'),
                       np.linspace(0.0, -0.5, 11))


def test_eval_slope_stop():
    """Test evaluating the entries of an active modulation when some vars
    are missing.
    Issue on amplitude.

    """
    """Test evaluating the slope shape in start/slope mode.

    """
    shape = SlopeShape(mode='Slope/Stop', def1='{a}', def2='-1',
                       index=1)
    root_vars = {'a': -0.5, '1_duration': 1}
    missing = set()
    errors = {}

    assert shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert errors == {}
    assert_array_equal(shape.compute(np.ones(11), 'mus'),
                       np.linspace(-0.5, -1.0, 11))


def test_eval_issue_on_start():
    """Test handling a too large value for start.

    """
    shape = SlopeShape(mode='Start/Stop', def1='1.5', def2='{a}')
    root_vars = {'a': 1.0}
    missing = set()
    errors = {}

    assert not shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert '0_shape_start' in errors


def test_eval_issue_on_stop():
    """Test handling a too large value for stop.

    """
    shape = SlopeShape(mode='Start/Stop', def1='1.0', def2='{a}')
    root_vars = {'a': 1.5}
    missing = set()
    errors = {}

    assert not shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert '0_shape_stop' in errors


def test_eval_issue_on_slope_start():
    """Test handling an issue on slope in Start/Slope mode.

    """
    shape = SlopeShape(mode='Start/Slope', def1='{a}', def2='0.5',
                       index=1)
    root_vars = {'a': 0.5, '1_duration': 2}
    missing = set()
    errors = {}

    assert not shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert '1_shape_slope' in errors


def test_eval_issue_on_slope_stop():
    """Test handling an issue on slope in Slope/Stop mode.

    """
    shape = SlopeShape(mode='Slope/Stop', def1='{a}', def2='0.5',
                       index=1)
    root_vars = {'a': -0.5, '1_duration': 2}
    missing = set()
    errors = {}

    assert not shape.eval_entries({}, root_vars, missing, errors)
    assert missing == set()
    assert '1_shape_slope' in errors


def test_pulse_view(workbench, exopy_qtbot, dialog_sleep):
    """Test the view of the Pulse class.

    """
    from exopy.testing.util import show_widget
    with enaml.imports():
        from exopy_pulses.pulses.sequences.views.base_sequences_views\
            import RootSequenceView

    pulse = Pulse(root=RootSequence(context=TestingContext()))
    pulse.kind = 'Analogical'
    root = pulse.root
    root.add_child_item(0, pulse)
    core = workbench.get_plugin('enaml.workbench.core')
    root_view = RootSequenceView(item=root, core=core)
    pulse_view = root_view.view_for(pulse)
    show_widget(exopy_qtbot, root_view)
    exopy_qtbot.wait(dialog_sleep)

    # Test selecting a slope shape
    shape_select = pulse_view.widgets()[-1].widgets()[-1]
    shape_select.selected = 'exopy_pulses.SlopeShape'
    exopy_qtbot.wait(10 + dialog_sleep)

    shape_view = pulse_view.widgets()[-1]
    sv_widgets = shape_view.split_items()[0].split_widget().widgets()

    for mode in ('Start/Stop', 'Start/Slope', 'Slope/Stop'):
        sv_widgets[1].selected = mode

        def assert_mode():
            assert sv_widgets[2].text == mode.split('/')[0]
            assert sv_widgets[4].text == mode.split('/')[1]
        exopy_qtbot.wait_until(assert_mode)
