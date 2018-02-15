# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Tests for the base configuration.

"""
import enaml
from exopy.testing.util import show_widget

from exopy_pulses.pulses.api import BaseSequence
from exopy_pulses.pulses.configs.base_config import SequenceConfig

with enaml.imports():
    from exopy_pulses.pulses.configs.base_config_views\
        import SequenceConfigView


def test_sequence_config(pulses_plugin):
    """Test the base sequence config.

    """
    conf = SequenceConfig(sequence_class=BaseSequence, manager=pulses_plugin)
    conf.sequence_name = 'test'
    assert conf.ready
    conf.sequence_name = ''
    assert not conf.ready
    conf.sequence_name = 'test'
    seq = conf.build_sequence()
    assert isinstance(seq, BaseSequence) and seq.name == 'test'


def test_sequence_config_view(exopy_qtbot):
    """Test the view of the base config.

    """
    w = SequenceConfigView(model=SequenceConfig(sequence_doc='test',))
    show_widget(exopy_qtbot, w)
    w.widgets()[1].text = 'test'

    def assert_ready():
        assert w.model.ready
    exopy_qtbot.wait_until(assert_ready)
