# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the base sequences views.

"""
import enaml

from exopy.testing.util import show_widget, handle_dialog

from exopy_pulses.pulses.sequences.base_sequences import (BaseSequence,
                                                          RootSequence)
with enaml.imports():
    from exopy_pulses.pulses.sequences.views.abstract_sequence_view\
        import AbstractSequenceView
    from exopy_pulses.pulses.sequences.views.base_sequences_views\
        import BaseSequenceView, RootSequenceView


def test_abstract_refresh(exopy_qtbot):
    """Test the refresh function of the abstract view.

    """
    view = AbstractSequenceView(item=BaseSequence())
    show_widget(exopy_qtbot, view)
    view.hide()
    view.refresh()
    assert view.visible


def test_base_sequence_refresh(exopy_qtbot):
    """Test the refresh function of the base sequence view.

    """
    view = BaseSequenceView(item=BaseSequence())
    show_widget(exopy_qtbot, view)
    view.hide()
    view.refresh()
    assert view.visible


def test_root_sequence_view(exopy_qtbot, workbench):
    """Test the root sequence view.

    """
    core = workbench.get_plugin('enaml.workbench.core')
    view = RootSequenceView(item=RootSequence(),
                            core=core)

    show_widget(exopy_qtbot, view)
    seq = BaseSequence()
    view.item.add_child_item(0, seq)
    assert seq in view._cache
    view.item.remove_child_item(0)
    assert seq not in view._cache

    but = view.widgets()[-1].pages()[1].page_widget().widgets()[0]
    with handle_dialog(exopy_qtbot, 'reject'):
        but.clicked = True
