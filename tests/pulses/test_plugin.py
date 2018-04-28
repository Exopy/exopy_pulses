# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the pulses plugin capabilities.

"""
import os

from configobj import ConfigObj


def test_init(workbench):
    """Test starting the plugin.

    """
    plugin = workbench.get_plugin('exopy.pulses')

    core = workbench.get_plugin('enaml.workbench.core')
    core.invoke_command('exopy.app.errors.enter_error_gathering')

    state = core.invoke_command('exopy.app.states.get',
                                {'state_id': 'exopy.app.directory'})

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
                              caplog):
    """Test that new templates are properly detected.

    """
    import logging
    caplog.set_level(logging.WARNING)

    plugin = workbench.get_plugin('exopy.pulses')
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
    assert caplog.records

    plugin.templates_folders = [os.path.join(app_dir, 'pulses', 'templates')]
    assert template_sequence in plugin.sequences


def test_get_item_infos(workbench, template_sequence):
    """Test getting the infos related to an item (pulse or sequence).

    """
    plugin = workbench.get_plugin('exopy.pulses')
    for id_ in ('exopy_pulses.Pulse', 'exopy_pulses.BaseSequence',
                template_sequence, 'exopy_pulses.__template__', 'unknown'):
        infos = plugin.get_item_infos(id_)
        if id_ == 'unknown':
            assert infos is None
        else:
            assert infos and infos.cls, infos.view


# TODO test using the commands
def test_get_item(workbench):
    """Test getting an item class and potentially view.

    """
    plugin = workbench.get_plugin('exopy.pulses')
    for view in (False, True):
        for id_ in ('exopy_pulses.Pulse', 'exopy_pulses.BaseSequence',
                    'exopy_pulses.__template__', 'unknown'):
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
    plugin = workbench.get_plugin('exopy.pulses')
    items, missing = plugin.get_items(('exopy_pulses.Pulse',
                                       'exopy_pulses.BaseSequence',
                                       'exopy_pulses.__template__', 'unknown'))
    for id_ in ('exopy_pulses.Pulse', 'exopy_pulses.BaseSequence',
                'exopy_pulses.__template__'):
        assert id_ in items
        assert items[id_] is plugin.get_item(id_)

    assert 'unknown' in missing


def test_get_context_infos(workbench):
    """Test get a context infos.

    """
    plugin = workbench.get_plugin('exopy.pulses')
    infos = plugin.get_context_infos('exopy_pulses.TestContext')
    assert infos and infos.cls and infos.view
    assert plugin.get_context_infos('__unknown__') is None


def test_get_context(workbench):
    """Test getting a context class and view.

    """
    plugin = workbench.get_plugin('exopy.pulses')
    cls = plugin.get_context('exopy_pulses.TestContext')
    assert cls is plugin.get_context_infos('exopy_pulses.TestContext').cls

    cls, view = plugin.get_context('exopy_pulses.TestContext', True)
    assert cls is plugin.get_context_infos('exopy_pulses.TestContext').cls
    assert view is plugin.get_context_infos('exopy_pulses.TestContext').view

    assert plugin.get_context('__unknown__', True) == (None, None)


def test_get_shape_infos(workbench):
    """Test getting a shape infos.

    """
    plugin = workbench.get_plugin('exopy.pulses')
    infos = plugin.get_shape_infos('exopy_pulses.SquareShape')
    assert infos and infos.cls and infos.view
    assert plugin.get_shape_infos('__unknown__') is None


def test_get_shape(workbench):
    """Test getting a shape class and view.

    """
    plugin = workbench.get_plugin('exopy.pulses')
    cls = plugin.get_shape('exopy_pulses.SquareShape')
    assert cls is plugin.get_shape_infos('exopy_pulses.SquareShape').cls

    cls, view = plugin.get_shape('exopy_pulses.SquareShape', True)
    assert cls is plugin.get_shape_infos('exopy_pulses.SquareShape').cls
    assert view is plugin.get_shape_infos('exopy_pulses.SquareShape').view

    assert plugin.get_shape('__unknown__', True) == (None, None)


# TODO add real test when this is complete
def test_get_modulation(workbench):
    """Test retrieving the for the time being unique modulation.

    """
    plugin = workbench.get_plugin('exopy.pulses')
    cls = plugin.get_modulation('exopy_pulses.Modulation')
    assert cls

    cls = plugin.get_modulation('__unknown__')
    assert cls is None


# TODO add a test for the template case when template are back
def test_get_config(workbench):
    """Test getting a config for a sequence class.

    """
    plugin = workbench.get_plugin('exopy.pulses')
    cls, view = plugin.get_config('exopy_pulses.BaseSequence')

    assert cls and view

    cls, view = plugin.get_config('__unknown__')
    assert cls is None and view is None


def test_list_sequences(workbench, template_sequence, caplog):
    """Test iltering sequences.

    """
    import logging
    caplog.set_level(logging.WARNING)

    plugin = workbench.get_plugin('exopy.pulses')

    seq = plugin.list_sequences('All')
    assert 'exopy_pulses.BaseSequence' in seq
    assert 'exopy_pulses.Pulse' not in seq
    assert 'exopy_pulses.RootSequence' not in seq

    plugin.list_sequences('__unknown__')
    assert caplog.records
