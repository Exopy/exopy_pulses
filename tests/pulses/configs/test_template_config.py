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
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from ast import literal_eval

import pytest

from exopy_pulses.pulses.api import RootSequence, BaseSequence
from exopy_pulses.pulses.sequences.template_sequence import TemplateSequence
from exopy_pulses.pulses.configs.template_config import TemplateConfig


def test_init(pulses_plugin, template_sequence):
    """Test the context is properly created at config init.

    """
    infos = pulses_plugin.get_item_infos('__dummy__')
    meta = infos.metadata
    t_config = TemplateConfig(manager=pulses_plugin,
                              template_doc=meta['template_doc'],
                              template_config=meta['template_config'])

    assert set(t_config.context.logical_channels) == {'A', 'B'}
    assert set(t_config.context.analogical_channels) == {'Ch1', 'Ch2'}
    assert (t_config.context.channel_mapping ==
            {'A': '', 'B': '', 'Ch1': '', 'Ch2': ''})


@pytest.mark.xfail
def test_building_template1(pulses_plugin, template_sequence):
    """Test building a template.

    """
    infos = pulses_plugin.get_item_infos('__dummy__')
    meta = infos.metadata
    t_config = TemplateConfig(manager=pulses_plugin,
                              template_doc=meta['template_doc'],
                              template_config=meta['template_config'])
    t_config.template_name = 'Test'

    seq = t_config.build_sequence()
    assert not t_config.errors
    assert isinstance(seq, TemplateSequence)
    assert seq.name == 'Test'
    # No need to check more as build_from_config is already tested in
    # test_template_sequence.


@pytest.mark.xfail
def test_building_template2(pulses_plugin, template_sequence):
    """Test building a template for which some dependencies are missing.

    """
    del pulses_plugin._sequences.contributions['exopy_pulses.BaseSequence']
    infos = pulses_plugin.get_item_infos('__dummy__')
    meta = infos.metadata
    t_config = TemplateConfig(manager=pulses_plugin,
                              template_doc=meta['template_doc'],
                              template_config=meta['template_config'])
    t_config.template_name = 'Test'

    seq = t_config.build_sequence()
    assert t_config.errors
    assert seq is None


@pytest.mark.xfail
def test_merging_template1(pulses_plugin, template_sequence):
    """Test merging a template.

    """
    infos = pulses_plugin.get_item_infos('__dummy__')
    meta = infos.metadata
    t_config = TemplateConfig(manager=pulses_plugin,
                              template_doc=meta['template_doc'],
                              template_config=meta['template_config'])
    t_config.template_name = 'Test'
    t_config.merge = True
    t_config.root = RootSequence()
    t_config.context.channel_mapping =\
        {'A': 'Ch1_M1', 'Ch1': 'Ch3'}

    seq = t_config.build_sequence()
    assert not t_config.errors
    assert isinstance(seq, BaseSequence)
    assert seq.name == 'Test'
    loc_vars = literal_eval(meta['template_config']['local_vars'])
    loc_vars.update(literal_eval(meta['template_config']['template_vars']))
    assert seq.local_vars == loc_vars
    assert not t_config.root.external_vars

    assert seq.items[0].channel == 'Ch1_M1'
    assert seq.items[1].channel == ''
    assert seq.items[2].items[0].channel == ''
    assert seq.items[3].channel == 'Ch3'

# TODO test failed collection of dependencies
# TODO test adding template vars as globals
# TODO test merging a template containing a template and check that the
#     channel mapping is correct
# TODO test the view
