# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Pulse sequence workspace fixture functions.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest
import enaml


with enaml.imports():
    from enaml.workbench.ui.ui_manifest import UIManifest
    from exopy.app.log.manifest import LogManifest


pytests_plugin = str('exopy_pulses.testing.fixtures'),


@pytest.yield_fixture
def pulses_workspace(pulses_workbench, windows):
    """Create a.measurement workspace.

    """
    pulses_workbench.register(UIManifest())
    pulses_workbench.register(LogManifest())
    pulses_plugin = pulses_workbench.get_plugin('exopy.pulses')
    core = pulses_workbench.get_plugin('enaml.workbench.core')
    cmd = 'enaml.workbench.ui.select_workspace'
    core.invoke_command(cmd, {'workspace': 'exopy.pulses.workspace'})

    yield pulses_plugin.workspace

    cmd = 'enaml.workbench.ui.close_workspace'
    core.invoke_command(cmd, {'workspace': 'exopy.measurement.workspace'})

    for m_id in ('exopy.app.logging'):
        try:
            pulses_workbench.unregister(m_id)
        except ValueError:
            pass
