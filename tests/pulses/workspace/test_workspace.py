# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the pulse sequence edition workspace.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from ecpy.testing.util import handle_dialog, handle_question


pytest_plugins = str('ecpy_pulses.testing.workspace.fixtures'),


def test_workspace_lifecycle(workspace, process_and_sleep):
    """Test the workspace life cycle.

    """
    workbench = workspace.workbench
    ui = workbench.get_plugin('enaml.workbench.ui')
    ui.show_window()
    process_and_sleep()

    log = workbench.get_plugin('ecpy.app.logging')
    # Check UI creation
    assert workspace.log_model
    assert workspace.state
    assert workspace.content
    assert workspace.dock_area
    assert workbench.get_manifest('ecpy.pulses.workspace.menus')

    # Check log handling
    assert 'ecpy.pulses.workspace' in log.handler_ids

    w_state = workspace.state
    plugin = workspace.plugin

    # Test stopping the workspace
    core = workbench.get_plugin('enaml.workbench.core')
    cmd = 'enaml.workbench.ui.close_workspace'
    core.invoke_command(cmd, {'workspace': 'ecpy.pulses.workspace'})

    assert workspace.plugin.workspace is None
    assert workbench.get_manifest('ecpy.pulses.workspace.menus') is None
    assert 'ecpy.measure.workspace' not in log.handler_ids

    # Test restarting now that state exists.
    cmd = 'enaml.workbench.ui.select_workspace'
    core.invoke_command(cmd, {'workspace': 'ecpy.pulses.workspace'})
    assert plugin.workspace.state is w_state


def test_new_sequence(workspace, windows, process_and_sleep):
    """Test creating a new sequence.

    """
    workbench = workspace.workbench
    ui = workbench.get_plugin('enaml.workbench.ui')
    ui.show_window()
    process_and_sleep()

    core = workbench.get_plugin('enaml.workbench.core')
    old_seq = workspace.state.sequence

    with handle_question('yes'):
        cmd = 'ecpy.pulses.workspace.new'
        core.invoke_command(cmd, dict())

    assert old_seq is not workspace.state.sequence
    old_seq = workspace.state.sequence

    with handle_question('no'):
        cmd = 'ecpy.pulses.workspace.new'
        core.invoke_command(cmd, dict())

    assert old_seq is workspace.state.sequence


def test_save_load_sequence(workspace, windows, process_and_sleep, tmpdir):
    """Test saving and reloading a sequence.

    """
    pass
