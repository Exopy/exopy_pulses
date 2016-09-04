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


from enaml.widgets.api import Window

from ecpy.testing.util import process_app_events, handle_dialog


pytest_plugins = str('ecpy_pulses.testing.workspace.fixtures'),


def test_workspace_lifecycle(workspace, process_and_sleep):
    """Test the workspace life cycle.

    """
    ui = workspace.workbench.get_plugin('enaml.workbench.ui')
    ui.show_window()
    process_and_sleep()

    workbench = workspace.plugin.workbench
    log = workbench.get_plugin('ecpy.app.logging')
    # Check UI creation
    assert workspace.log_model
    assert workspace.state
    assert workspace.content
    assert workspace.dock_area
    assert workbench.get_manifest('ecpy.pulses.workspace.menus')

    # Check log handling
    assert 'ecpy.pulses.workspace' in log.handler_ids

    # Test creating a new sequence
    # XXX do it

    # Test stopping the workspace
    core = workbench.get_plugin('enaml.workbench.core')
    cmd = 'enaml.workbench.ui.close_workspace'
    core.invoke_command(cmd, {'workspace': 'ecpy.pulses.workspace'})

    assert workspace.plugin.workspace is None
    assert workbench.get_manifest('ecpy.pulses.workspace.menus') is None
    assert 'ecpy.measure.workspace' not in log.handler_ids

    # Test restarting now that we have one edited sequence in state.
#    cmd = 'enaml.workbench.ui.select_workspace'
#    core.invoke_command(cmd, {'workspace': 'ecpy.measure.workspace'})
#    assert len(workspace.plugin.edited_measures.measures) == 1
