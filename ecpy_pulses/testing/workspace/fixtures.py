# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
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
    from ecpy.app.log.manifest import LogManifest


pytests_plugin = str('ecpy_pulses.testing.fixtures'),


@pytest.yield_fixture
def pulses_workspace(pulses_workbench, windows):
    """Create a measure workspace.

    """
    pulses_workbench.register(UIManifest())
    pulses_workbench.register(LogManifest())
    pulses_plugin = pulses_workbench.get_plugin('ecpy.pulses')
    core = pulses_workbench.get_plugin('enaml.workbench.core')
    cmd = 'enaml.workbench.ui.select_workspace'
    core.invoke_command(cmd, {'workspace': 'ecpy.pulses.workspace'})

    yield pulses_plugin.workspace

    cmd = 'enaml.workbench.ui.close_workspace'
    core.invoke_command(cmd, {'workspace': 'ecpy.measure.workspace'})

    for m_id in ('ecpy.app.logging'):
        try:
            pulses_workbench.unregister(m_id)
        except ValueError:
            pass
