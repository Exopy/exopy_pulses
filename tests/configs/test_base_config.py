# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Tests for the base configuration.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import enaml
from ecpy.testing.util import show_widget, process_app_events

from ecpy_pulses.api import BaseSequence
from ecpy_pulses.configs.base_config import SequenceConfig

with enaml.imports():
    from ecpy_pulses.configs.base_config_views import SequenceConfigView


def test_sequence_config():
    """Test the base sequence config.

    """
    conf = SequenceConfig(sequence_class=BaseSequence)
    conf.sequence_name = 'test'
    assert conf.ready
    conf.sequence_name = ''
    assert not conf.ready
    conf.sequence_name = 'test'
    seq = conf.build_sequence()
    assert isinstance(seq, BaseSequence) and seq.name == 'test'


def test_sequence_config_view(windows):
    """Test the view of the base config.

    """
    w = SequenceConfigView(model=SequenceConfig(sequence_doc='test',))
    show_widget(w)
    w.widgets()[1].text = 'test'
    process_app_events()
    assert w.model.ready
