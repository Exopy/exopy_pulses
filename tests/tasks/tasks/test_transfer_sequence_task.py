# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the transfer pulse sequence task.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import os

import enaml
import pytest
from ecpy.tasks.api import RootTask
from ecpy.tasks.tasks.instr_task import (PROFILE_DEPENDENCY_ID,
                                         DRIVER_DEPENDENCY_ID)
with enaml.imports():
    from ecpy.tasks.manifest import TaskManagerManifest
    from ecpy.tasks.base_tasks_views import RootTaskView

from ecpy_pulses.pulses.pulse import Pulse
from ecpy_pulses.pulses.utils.sequences_io import save_sequence_prefs
from ecpy_pulses.pulses.sequences.base_sequences\
    import RootSequence
from ecpy_pulses.testing.context import TestContext
from ecpy_pulses.tasks.tasks.transfer_sequence_task\
    import TransferPulseSequenceTask
with enaml.imports():
    from ecpy_pulses.tasks.tasks.views.transfer_sequence_task_view\
         import TransferPulseSequenceView
    from ecpy_pulses.tasks.manifest import PulsesTasksManifest


p_id = PROFILE_DEPENDENCY_ID
d_id = DRIVER_DEPENDENCY_ID


class FalseStarter(object):
    """False instrument starter used for testing.

    """
    finalize_called = False

    def __init__(self, should_pass=True):
        self.should_pass = should_pass

    def check_infos(self, driver_cls, connection, settings):
        return self.should_pass, 'Message'

    def start(self, driver_cls, connection, settings):
        return object()

    def stop(self, driver):
        FalseStarter.stop_called = True


@pytest.fixture
def sequence():
    """Create a sequence.

    """
    root = RootSequence()
    context = TestContext(sampling=0.5)
    root.context = context

    root.external_vars = {'a': 1.5}
    root.local_vars = {'b': '2*{a}'}

    pulse1 = Pulse(def_1='1.0', def_2='{a}')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(def_1='{2_stop} + 0.5', def_2='10 + {b}')
    for i, c in enumerate((pulse1, pulse2, pulse3)):
        root.add_child_item(i, c)

    return root


@pytest.fixture
def task(sequence, tmpdir):
    """Transfer sequence task for testing.

    """
    root = RootTask()
    root.run_time = {d_id: {'d': (object, FalseStarter())},
                     p_id: {'p': {'connections': {'c': {}, 'c2': {}},
                                  'settings': {'s': {}}}}}
    path = os.path.join(str(tmpdir), 'test.pulse.ini')
    save_sequence_prefs(path, sequence.prefs_from_config())
    task = TransferPulseSequenceTask(sequence=sequence, sequence_path=path,
                                     sequence_timestamp=os.path.getmtime(path),
                                     sequence_vars={'a': '1.5'},
                                     name='Test')
    root.add_child_task(0, task)
    return task


@pytest.fixture
def task_view(task, workbench):
    """Transfer sequence task view for testing.

    """
    workbench.register(TaskManagerManifest())
    core = workbench.get_plugin('enaml.workbench.core')
    root_view = RootTaskView(task=task.root, core=core)
    view = TransferPulseSequenceView(task=task, root=root_view)
    return view


def test_task_traversal(task):
    """Test that the task does yield the sequence.

    """
    components = list(task.traverse())
    assert task.sequence in components


def test_task_saving_building(workbench, task):
    """Test saving and rebuilbing the sequence.

    """
    workbench.register(PulsesTasksManifest())
    core = workbench.get_plugin('enaml.workbench.core')
    deps = core.invoke_command('ecpy.app.dependencies.analyse',
                               dict(obj=task, dependencies=['build']))
    deps = core.invoke_command('ecpy.app.dependencies.collect',
                               dict(dependencies=deps.dependencies,
                                    kind='build'))

    prefs = task.get_from_preferences()
    task2 = TransferPulseSequenceTask.build_from_config(prefs,
                                                        deps.dependencies)

    assert task2.sequence
    assert task2.sequence.context
    assert task2.sequence.items


def test_update_of_task_database_entries(task):
    """Test that changing of context does trigger the expected update.

    """
    class FancyContext(TestContext):
        def list_sequence_infos(self):
            return {'dummy': True}

    task.sequence.context = FancyContext()
    assert task.database_entries == {'dummy': True}

    task.sequence = sequence()
    assert task.database_entries == {'test': True}

    task.sequence.context = FancyContext()
    assert task.database_entries == {'dummy': True}


def test_task_check1(task):
    """Test that if there is not problem tests pass.

    """
    res, traceback = task.check()
    assert res
    assert not traceback


def test_task_check2(task):
    """Test handling errors in variable evaluation.

    """
    task.sequence_vars = {'a': '+*'}
    res, traceback = task.check()
    assert not res
    assert 'root/Test-a' in traceback


def test_task_check3(task):
    """Test handling an evaluation error.

    """
    task.sequence.internal_vars = {}
    res, traceback = task.check()
    assert not res
    assert 'root/Test-compil' in traceback


def test_task_check4(task, monkeypatch):
    """Test handling a compilation error.

    """
    def fail_compil(*args, **kwargs):
        return False, {}, {'test': ''}
    monkeypatch.setattr(TestContext, 'compile_and_transfer_sequence',
                        fail_compil)
    res, traceback = task.check()
    assert not res
    assert 'root/Test-compil' in traceback
    assert 'test' in traceback['root/Test-compil']


def test_task_check5(task):
    """Test that we get a warning on outdated sequence.

    """
    task.sequence_timestamp = ''
    res, traceback = task.check()
    assert res
    assert 'root/Test-outdated' in traceback


def test_task_perform1(task):
    """Test performing the task when everything goes right.

    """
    assert task.get_from_database('Test-test') is False
    task.perform()
    assert task.get_from_database('Test-test')


def test_task_perform2(task):
    """Test handling error in sequence evaluation.

    """
    task.sequence.internal_vars = {}
    with pytest.raises(ValueError):
        task.perform()


def test_task_perform3(task, monkeypatch):
    """Test handling error in sequence compilation and transfer.

    """
    def fail_compil(*args, **kwargs):
        return False, {}, {'test': ''}
    monkeypatch.setattr(TestContext, 'compile_and_transfer_sequence',
                        fail_compil)
    with pytest.raises(ValueError):
        task.perform()


def test_view_validate_driver_context(task_view):
    """
    """
    pass


def test_load_refresh_save(task_view, tmpdir):
    """
    """
    pass


def test_changing_context_sequence(task_view):
    """
    """
    pass


def test_profile_filtering(task_view):
    """
    """
    pass


def test_drivers_filtering(task_view):
    """
    """
    pass

# XXX add tests for view
# - test context/driver validation
# - test load/refresh/save
# - test sequence/context observation
# - test profiles/drivers filtering
