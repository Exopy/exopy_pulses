# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the commands defined in the plugin manifest

"""
import os

import pytest
import enaml
from configobj import ConfigObj
from exopy.testing.util import handle_dialog
with enaml.imports():
    from exopy.app.errors.widgets import ErrorsDialog

from exopy_pulses.pulses.sequences.base_sequences import RootSequence
from exopy_pulses.testing.context import DummyContext
with enaml.imports():
    from exopy_pulses.pulses.utils.widgets.building import BuilderView


@pytest.fixture
def root():
    root = RootSequence(context=DummyContext())
    return root


def test_create_sequence(root, workbench, exopy_qtbot, monkeypatch):
    """Test creating a sequence.

    """
    core = workbench.get_plugin('enaml.workbench.core')

    def select_sequence(exopy_qtbot, dial):
        """Select the sequence to build.

        """
        dial.selector.selected_sequence = 'exopy_pulses.BaseSequence'

    with handle_dialog(exopy_qtbot, 'accept', select_sequence):
        cmd = 'exopy.pulses.create_sequence'
        seq = core.invoke_command(cmd, dict(root=root))

    assert seq is not None

    with handle_dialog(exopy_qtbot, 'reject'):
        cmd = 'exopy.pulses.create_sequence'
        seq = core.invoke_command(cmd, dict(root=root))

    assert seq is None

    def raise_on_build(*args, **kwargs):
        raise Exception()

    from exopy_pulses.pulses.configs.base_config import SequenceConfig
    monkeypatch.setattr(SequenceConfig, 'build_sequence', raise_on_build)

    with handle_dialog(exopy_qtbot, 'accept', cls=ErrorsDialog, time=500):
        with handle_dialog(exopy_qtbot, 'accept', cls=BuilderView):
            cmd = 'exopy.pulses.create_sequence'
            seq = core.invoke_command(cmd, dict(root=root))


def test_build_sequence_from_path(workbench, root, tmpdir):
    """Test building a sequence stored in a file.

    """
    path = os.path.join(str(tmpdir), 'test.pulse.ini')
    pref = root.preferences_from_members()
    conf = ConfigObj(pref)
    with open(path, 'wb') as f:
        conf.write(f)

    core = workbench.get_plugin('enaml.workbench.core')
    cmd = 'exopy.pulses.build_sequence'
    assert isinstance(core.invoke_command(cmd, dict(path=path)), type(root))

    with pytest.raises(ValueError):
        core.invoke_command(cmd, dict())


def test_build_sequence_from_config(workbench, root):
    """Test building a sequence stored in a file.

    """
    prefs = ConfigObj(root.preferences_from_members())

    core = workbench.get_plugin('enaml.workbench.core')
    cmd = 'exopy.pulses.build_sequence'
    assert isinstance(core.invoke_command(cmd, dict(prefs=prefs)), type(root))


def test_build_sequence_handle_dependencies_issues(workbench, root):
    """Test handling issue in collecting dependencies.

    """
    prefs = ConfigObj(root.preferences_from_members())
    prefs['dep_type'] = '__dumb__'

    core = workbench.get_plugin('enaml.workbench.core')
    cmd = 'exopy.pulses.build_sequence'
    with pytest.raises(RuntimeError):
        core.invoke_command(cmd, dict(prefs=prefs))

    prefs = ConfigObj(root.preferences_from_members())
    prefs['item_id'] = '__dumb__'

    core = workbench.get_plugin('enaml.workbench.core')
    cmd = 'exopy.pulses.build_sequence'
    with pytest.raises(RuntimeError):
        core.invoke_command(cmd, dict(prefs=prefs))


def test_create_context(workbench, root, exopy_qtbot):
    """Test creating a context for a sequence.

    """
    core = workbench.get_plugin('enaml.workbench.core')

    def select_context(exopy_qtbot, dial):
        """Select the sequence to build.

        """
        obj_combo = dial.central_widget().widgets()[0]
        obj_combo.selected_item = 'Dummy'

    with handle_dialog(exopy_qtbot, 'accept', select_context):
        cmd = 'exopy.pulses.create_context'
        core.invoke_command(cmd, dict(root=root))

    assert root.context is not None

    del root.context

    with handle_dialog(exopy_qtbot, 'reject'):
        cmd = 'exopy.pulses.create_context'
        core.invoke_command(cmd, dict(root=root))

    assert root.context is None
