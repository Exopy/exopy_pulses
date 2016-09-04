# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the base sequences views.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import enaml

from ecpy.testing.util import show_widget, handle_dialog

from ecpy_pulses.pulses.sequences.base_sequences import (BaseSequence,
                                                         RootSequence)
with enaml.imports():
    from ecpy_pulses.pulses.sequences.views.abstract_sequence_view\
        import AbstractSequenceView
    from ecpy_pulses.pulses.sequences.views.base_sequences_views\
        import BaseSequenceView, RootSequenceView


def test_abstract_refresh(windows):
    """Test the refresh function of the abstract view.

    """
    view = AbstractSequenceView()
    show_widget(view)
    view.hide()
    view.refresh()
    assert view.visible


def test_base_sequence_refresh(windows):
    """Test the refresh function of the base sequence view.

    """
    view = BaseSequenceView()
    show_widget(view)
    view.hide()
    view.refresh()
    assert view.visible


def test_root_sequence_view(windows, workbench):
    """Test the root sequence view.

    """
    core = workbench.get_plugin('enaml.workbench.core')
    view = RootSequenceView(item=RootSequence(),
                            core=core)

    show_widget(view)
    seq = BaseSequence()
    view.item.add_child_item(0, seq)
    assert seq in view._cache
    view.item.remove_child_item(0)
    assert seq not in view._cache

    but = view.widgets()[-1].pages()[1].page_widget().widgets()[0]
    with handle_dialog('reject'):
        but.clicked = True
