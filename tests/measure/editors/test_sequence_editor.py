# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Check that the manifest does register the editor.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from collections import OrderedDict

import enaml
import pytest

from ecpy.testing.util import show_widget

with enaml.imports():
    from ecpy_pulses.pulses.manifest import PulsesManagerManifest
    from ecpy_pulses.measure.manifest import PulsesMeasureManifest

from ...tasks.tasks.test_transfer_sequence_task import task, sequence
with enaml.imports():
    from ...pulses.contributions import PulsesContributions

pytest_plugins = (str('ecpy.testing.measure.fixtures'),)


@pytest.fixture
def editor(measure_workbench):
    """Create a pulse sequence editor.

    """
    measure_workbench.register(PulsesManagerManifest())
    measure_workbench.register(PulsesMeasureManifest())
    measure_workbench.register(PulsesContributions())
    pl = measure_workbench.get_plugin('ecpy.measure')

    decls = pl.get_declarations('editor', ['ecpy_pulses.pulse_sequence'])
    decl = decls['ecpy_pulses.pulse_sequence']
    ed = decl.new(measure_workbench)
    return ed


def test_sequence_vars_update(measure_workbench, editor, task,
                              process_and_sleep, windows):
    """Test that when unselecting the editor we properly synchronize the vars.

    """
    task.sequence_vars = OrderedDict({'a': '1.5', 'b': '2'})
    win = show_widget(editor)
    editor.selected_task = task
    process_and_sleep()

    root_view = editor.page_widget().widgets()[0].scroll_widget().widgets()[0]
    vars_editor = root_view.additional_pages[0]
    vars_editor.page_widget().widgets()[0].text = 'a, c'

    editor.react_to_unselection(measure_workbench)
    assert task.sequence_vars == OrderedDict([('a', '1.5'), ('c', '')])
    win.close()


def test_sequence_replacement(editor, task, windows, process_and_sleep):
    """Test replacing the sequence (a priori not possible).

    """
    editor.selected_task = task
    show_widget(editor)

    root_view = editor.page_widget().widgets()[0].scroll_widget().widgets()[0]
    old = root_view.additional_pages[0]

    seq = task.sequence
    task.sequence = sequence()
    process_and_sleep()
    task.sequence = seq
    process_and_sleep()

    root_view = editor.page_widget().widgets()[0].scroll_widget().widgets()[0]
    process_and_sleep()
    new = root_view.additional_pages[0]

    assert old is not new
