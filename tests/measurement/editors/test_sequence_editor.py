# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Check that the manifest does register the editor.

"""
import os
from collections import OrderedDict

import enaml
import pytest

from exopy.tasks.api import RootTask
from exopy.testing.util import show_widget
from exopy.tasks.tasks.instr_task import (PROFILE_DEPENDENCY_ID,
                                          DRIVER_DEPENDENCY_ID)

with enaml.imports():
    from exopy_pulses.pulses.manifest import PulsesManagerManifest
    from exopy_pulses.measurement.manifest import PulsesMeasurementManifest

from exopy_pulses.pulses.pulse import Pulse
from exopy_pulses.pulses.utils.sequences_io import save_sequence_prefs
from exopy_pulses.pulses.sequences.base_sequences\
    import RootSequence
from exopy_pulses.testing.context import TestContext
from exopy_pulses.tasks.tasks.instrs.transfer_sequence_task\
    import TransferPulseSequenceTask

with enaml.imports():
    from .contributions import PulsesContributions

pytest_plugins = (str('exopy.testing.measurement.fixtures'),)


class FalseStarter(object):
    """False instrument starter used for testing.

    """
    finalize_called = False

    def __init__(self, should_pass=True):
        self.should_pass = should_pass

    def check_infos(self, driver_cls, connection, settings):
        return self.should_pass, 'Message'

    def start(self, driver_cls, connection, settings):
        return object()

    def stop(self, driver):
        FalseStarter.stop_called = True


@pytest.fixture
def sequence():
    """Create a sequence.

    """
    root = RootSequence()
    context = TestContext(sampling=0.5)
    root.context = context

    root.external_vars = OrderedDict({'a': None})
    root.local_vars = OrderedDict({'b': '2*{a}'})

    pulse1 = Pulse(def_1='1.0', def_2='{a}', def_mode=str('Start/Stop'))
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10 + {b}')
    for i, c in enumerate((pulse1, pulse2, pulse3)):
        root.add_child_item(i, c)

    return root


@pytest.fixture
def task(sequence, tmpdir):
    """Transfer sequence task for testing.

    """
    p_id = PROFILE_DEPENDENCY_ID
    d_id = DRIVER_DEPENDENCY_ID
    root = RootTask()
    root.run_time = {d_id: {'d': (object, FalseStarter())},
                     p_id: {'p': {'connections': {'c': {}, 'c2': {}},
                                  'settings': {'s': {}}}}}
    path = os.path.join(str(tmpdir), 'test.pulse.ini')
    save_sequence_prefs(path, sequence.preferences_from_members())
    task = TransferPulseSequenceTask(sequence=sequence, sequence_path=path,
                                     sequence_timestamp=os.path.getmtime(path),
                                     sequence_vars=OrderedDict({'a': '1.5'}),
                                     name='Test',
                                     selected_instrument=('p', 'd', 'c', 's'))
    root.add_child_task(0, task)
    return task


@pytest.fixture
def editor(measurement_workbench):
    """Create a pulse sequence editor.

    """
    measurement_workbench.register(PulsesManagerManifest())
    measurement_workbench.register(PulsesMeasurementManifest())
    measurement_workbench.register(PulsesContributions())
    pl = measurement_workbench.get_plugin('exopy.measurement')

    decls = pl.get_declarations('editor', ['exopy_pulses.pulse_sequence'])
    decl = decls['exopy_pulses.pulse_sequence']
    ed = decl.new(measurement_workbench)
    return ed


def test_sequence_vars_update(measurement_workbench, editor, task,
                              exopy_qtbot, dialog_sleep):
    """Test that when unselecting the editor we properly synchronize the vars.

    """
    task.sequence_vars = OrderedDict({'a': '1.5', 'b': '2'})
    win = show_widget(exopy_qtbot, editor)
    editor.selected_task = task
    exopy_qtbot.wait(10 + dialog_sleep)

    root_view = editor.page_widget().widgets()[0].scroll_widget().widgets()[0]
    vars_editor = root_view.additional_pages[0]
    vars_editor.page_widget().widgets()[0].text = 'a, c'

    editor.react_to_unselection(measurement_workbench)
    assert task.sequence_vars == OrderedDict([('a', '1.5'), ('c', '')])
    win.close()


def test_sequence_replacement(editor, task, exopy_qtbot, dialog_sleep):
    """Test replacing the sequence (a priori not possible).

    """
    editor.selected_task = task
    show_widget(exopy_qtbot, editor)

    root_view = editor.page_widget().widgets()[0].scroll_widget().widgets()[0]
    old = root_view.additional_pages[0]

    seq = task.sequence
    task.sequence = sequence()
    exopy_qtbot.wait(10 + dialog_sleep)
    task.sequence = seq
    exopy_qtbot.wait(10 + dialog_sleep)

    root_view = editor.page_widget().widgets()[0].scroll_widget().widgets()[0]
    exopy_qtbot.wait(10 + dialog_sleep)
    new = root_view.additional_pages[0]

    assert old is not new
