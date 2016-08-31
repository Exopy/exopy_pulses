# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the pulses plugin capabilities.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import os

import pytest
import enaml
from configobj import ConfigObj

with enaml.imports():
    from .contributions import PulsesContributions


@pytest.fixture
def workbench(pulses_workbench):
    """Simply register the contributions for testing.

    """
    pulses_workbench.register(PulsesContributions())
    return pulses_workbench


def test_init(workbench):
    """Test starting the plugin.

    """
    plugin = workbench.get_plugin('ecpy.pulses')

    core = workbench.get_plugin('enaml.workbench.core')
    core.invoke_command('ecpy.app.errors.enter_error_gathering')

    state = core.invoke_command('ecpy.app.states.get',
                                {'state_id': 'ecpy.app.directory'})

    assert os.path.isdir(os.path.join(state.app_directory, 'pulses'))
    assert os.path.isdir(os.path.join(state.app_directory, 'pulses',
                                      'templates'))

    # check collector : sequences, shapes, filters, context, configs
    assert plugin.sequences
    assert plugin.shapes
    assert plugin.filters
    assert plugin.contexts
    assert plugin._configs.contributions

    # check pulse infos
    assert plugin._pulse_infos


def test_template_observation(workbench, template_sequence, app_dir,
                              capturelog):
    """Test that new templates are properly detected.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    assert template_sequence in plugin.sequences
    template_path = os.path.join(app_dir, 'pulses', 'templates')
    prof = ConfigObj(os.path.join(template_path, 'template.temp_pulse.ini'))
    prof.write()
    from time import sleep
    sleep(1)
    assert template_sequence in plugin.sequences
    assert 'template' in plugin.sequences
    os.remove(os.path.join(template_path, 'template.temp_pulse.ini'))
    sleep(1)
    assert template_sequence in plugin.sequences
    assert 'template' not in plugin.sequences

    plugin.templates_folders = ['']
    assert capturelog.records()

    plugin.templates_folders = [os.path.join(app_dir, 'pulses', 'templates')]
    assert template_sequence in plugin.sequences


def test_get_item_infos(workbench, template_sequence):
    """Test getting the infos related to an item (pulse or sequence).

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    for id_ in ('ecpy_pulses.Pulse', 'ecpy_pulses.BaseSequence',
                template_sequence, 'ecpy_pulses.__template__', 'unknown'):
        infos = plugin.get_item_infos(id_)
        if id_ == 'unknown':
            assert infos is None
        else:
            assert infos and infos.cls, infos.view


def test_get_item(workbench):
    """Test getting an item class and potentially view.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    for view in (False, True):
        for id_ in ('ecpy_pulses.Pulse', 'ecpy_pulses.BaseSequence',
                    'ecpy_pulses.__template__', 'unknown'):
            res = plugin.get_item(id_, view) if view else plugin.get_item(id_)
            if view:
                if id_ == 'unknown':
                    assert res == (None, None)
                else:
                    infos = plugin.get_item_infos(id_)
                    assert res[0] is infos.cls
                    assert res[1] is infos.view
            else:
                if id_ == 'unknown':
                    assert res is None
                else:
                    infos = plugin.get_item_infos(id_)
                    assert res is infos.cls


def test_get_items(workbench):
    """Test getting multiple items class.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    items, missing = plugin.get_items(('ecpy_pulses.Pulse',
                                       'ecpy_pulses.BaseSequence',
                                       'ecpy_pulses.__template__', 'unknown'))
    for id_ in ('ecpy_pulses.Pulse', 'ecpy_pulses.BaseSequence',
                'ecpy_pulses.__template__'):
        assert id_ in items
        assert items[id_] is plugin.get_item(id_)

    assert 'unknown' in missing


def test_get_context_infos(workbench):
    """Test get a context infos.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    infos = plugin.get_context_infos('ecpy_pulses.TestContext')
    assert infos and infos.cls and infos.view
    assert plugin.get_context_infos('__unknown__') is None


def test_get_context(workbench):
    """Test getting a context class and view.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    cls = plugin.get_context('ecpy_pulses.TestContext')
    assert cls is plugin.get_context_infos('ecpy_pulses.TestContext').cls

    cls, view = plugin.get_context('ecpy_pulses.TestContext', True)
    assert cls is plugin.get_context_infos('ecpy_pulses.TestContext').cls
    assert view is plugin.get_context_infos('ecpy_pulses.TestContext').view

    assert plugin.get_context('__unknown__', True) == (None, None)


def test_get_shape_infos(workbench):
    """Test getting a shape infos.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    infos = plugin.get_shape_infos('ecpy_pulses.SquareShape')
    assert infos and infos.cls and infos.view
    assert plugin.get_shape_infos('__unknown__') is None


def test_get_shape(workbench):
    """Test getting a shape class and view.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    cls = plugin.get_shape('ecpy_pulses.SquareShape')
    assert cls is plugin.get_shape_infos('ecpy_pulses.SquareShape').cls

    cls, view = plugin.get_shape('ecpy_pulses.SquareShape', True)
    assert cls is plugin.get_shape_infos('ecpy_pulses.SquareShape').cls
    assert view is plugin.get_shape_infos('ecpy_pulses.SquareShape').view

    assert plugin.get_shape('__unknown__', True) == (None, None)


# TODO add real test when this is complete
def test_get_modulation(workbench):
    """Test retrieving the for the time being unique modulation.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    cls = plugin.get_modulation('ecpy_pulses.Modulation')
    assert cls

    cls = plugin.get_modulation('__unknown__')
    assert cls is None


# TODO add a test for the template case when template are back
def test_get_config(workbench):
    """Test getting a config for a sequence class.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    cls, view = plugin.get_config('ecpy_pulses.BaseSequence')

    assert cls and view

    cls, view = plugin.get_config('__unknown__')
    assert cls is None and view is None


def test_list_sequences(workbench, template_sequence, capturelog):
    """Test iltering sequences.

    """
    plugin = workbench.get_plugin('ecpy.pulses')

    seq = plugin.list_sequences('All')
    assert 'ecpy_pulses.BaseSequence' in seq
    assert 'ecpy_pulses.Pulse' not in seq
    assert 'ecpy_pulses.RootSequence' not in seq

    plugin.list_sequences('__unknown__')
    assert capturelog.records()
