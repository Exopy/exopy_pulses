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
from ecpy.testing.util import handle_dialog, show_widget, handle_question

with enaml.imports():
    from ecpy.tasks.manifest import TasksManagerManifest
    from ecpy.tasks.tasks.base_views import RootTaskView

from ecpy_pulses.pulses.pulse import Pulse
from ecpy_pulses.pulses.utils.sequences_io import save_sequence_prefs
from ecpy_pulses.pulses.sequences.base_sequences\
    import RootSequence
from ecpy_pulses.testing.context import TestContext
from ecpy_pulses.tasks.tasks.instrs.transfer_sequence_task\
    import TransferPulseSequenceTask
with enaml.imports():
    from ecpy_pulses.tasks.tasks.instrs.views.transfer_sequence_task_view\
         import (TransferPulseSequenceView, validate_context_driver_pair,
                 load_sequence)
    from ecpy_pulses.tasks.manifest import PulsesTasksManifest

with enaml.imports():
    from ...pulses.contributions import PulsesContributions

p_id = PROFILE_DEPENDENCY_ID
d_id = DRIVER_DEPENDENCY_ID

pytest_plugins = str('ecpy_pulses.testing.fixtures'),


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
def workbench(pulses_workbench):
    """Simply register the contributions for testing.

    """
    pulses_workbench.register(PulsesContributions())
    return pulses_workbench


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
    save_sequence_prefs(path, sequence.preferences_from_members())
    task = TransferPulseSequenceTask(sequence=sequence, sequence_path=path,
                                     sequence_timestamp=os.path.getmtime(path),
                                     sequence_vars={'a': '1.5'},
                                     name='Test',
                                     selected_instrument=('p', 'd', 'c', 's'))
    root.add_child_task(0, task)
    return task


@pytest.fixture
def task_view(task, workbench):
    """Transfer sequence task view for testing.

    """
    workbench.register(TasksManagerManifest())
    core = workbench.get_plugin('enaml.workbench.core')
    cmd = 'ecpy.pulses.get_context_infos'
    c_infos = core.invoke_command(cmd,
                                  dict(context_id='ecpy_pulses.TestContext'))
    c_infos.instruments = set(['ecpy_pulses.TestDriver'])
    task.selected_instrument = ('p', 'ecpy_pulses.TestDriver', 'c', 's')
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
    workbench.register(TasksManagerManifest())
    core = workbench.get_plugin('enaml.workbench.core')
    deps = core.invoke_command('ecpy.app.dependencies.analyse',
                               dict(obj=task, dependencies=['build']))
    deps = core.invoke_command('ecpy.app.dependencies.collect',
                               dict(dependencies=deps.dependencies,
                                    kind='build'))

    task.update_preferences_from_members()
    prefs = task.preferences
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
    assert task.database_entries == {'instrument': '', 'dummy': True}

    task.sequence = sequence()
    assert task.database_entries == {'instrument': '', 'test': False}

    task.sequence.context = FancyContext()
    assert task.database_entries == {'instrument': '', 'dummy': True}


def test_task_check1(task):
    """Test that if there is not problem tests pass.

    """
    res, traceback = task.check()
    print(traceback)
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
    task.sequence.local_vars = {}
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
    task.sequence_timestamp = -1
    res, traceback = task.check()
    assert res
    assert 'root/Test-outdated' in traceback


def test_task_perform1(task):
    """Test performing the task when everything goes right.

    """
    assert task.get_from_database('Test_test') is False
    task.perform()
    assert task.get_from_database('Test_test')


def test_task_perform2(task):
    """Test handling error in sequence evaluation.

    """
    task.sequence.local_vars = {}
    with pytest.raises(Exception):
        task.perform()


def test_task_perform3(task, monkeypatch):
    """Test handling error in sequence compilation and transfer.

    """
    def fail_compil(*args, **kwargs):
        return False, {}, {'test': ''}
    monkeypatch.setattr(TestContext, 'compile_and_transfer_sequence',
                        fail_compil)
    with pytest.raises(Exception):
        task.perform()


def test_view_validate_driver_context(windows, task_view):
    """Test the validation of a context/driver pair.

    """
    task_view.task.selected_instrument = ('p', 'ecpy_pulses.TestDriver',
                                          'c', 's')
    with handle_dialog('accept'):
        validate_context_driver_pair(task_view.root.core,
                                     task_view.task.sequence.context,
                                     task_view.task, task_view)

    assert task_view.task.selected_instrument[0]

    task_view.task.selected_instrument = ('p', '__dummy__',
                                          'c', 's')
    with handle_dialog('accept'):
        validate_context_driver_pair(task_view.root.core,
                                     task_view.task.sequence.context,
                                     task_view.task, task_view)

    assert not task_view.task.selected_instrument[0]


def test_load_refresh_save(task_view, monkeypatch, process_and_sleep, windows):
    """Test loading a sequence, refreshing, modifying and saving.

    """
    from enaml.widgets.api import FileDialogEx

    @classmethod
    def get_filename(cls, parent, path, name_filters):
        return task_view.task.sequence_path
    monkeypatch.setattr(FileDialogEx, 'get_open_file_name', get_filename)

    task_view.task.sequence_timestamp = -1

    show_widget(task_view)
    # Check detection of outdated sequence
    assert task_view.widgets()[4].style_class

    old_seq = task_view.task.sequence
    task_view.task.sequence_vars = {'a': '1*23', 'c': '1'}
    # Load
    task_view.widgets()[2].clicked = True
    process_and_sleep()
    assert task_view.task.sequence is not old_seq
    assert task_view.task.sequence_vars == {'a': '1*23'}
    assert not task_view.widgets()[4].style_class

    old_seq = task_view.task.sequence
    task_view.task.sequence_vars = {}
    # Refresh
    with handle_question('no'):
        task_view.widgets()[4].clicked = True
    assert task_view.task.sequence is old_seq
    with handle_question('yes'):
        task_view.widgets()[4].clicked = True
    assert task_view.task.sequence is not old_seq
    assert task_view.task.sequence_vars == {'a': ''}

    old_timestamp = task_view.task.sequence_timestamp
    # Save
    btn = task_view.widgets()[5]
    actions = btn.menu().items()
    with handle_question('no'):
        btn.clicked = True
        actions[0].triggered = True
    assert task_view.task.sequence_timestamp == old_timestamp
    with handle_question('yes'):
        btn.clicked = True
        actions[0].triggered = True
    assert task_view.task.sequence_timestamp != old_timestamp

    @classmethod
    def get_save_filename1(cls, parent, path, name_filters):
        return ''

    new_path = task_view.task.sequence_path.rstrip('.pulse.ini')
    new_path += '2'

    @classmethod
    def get_save_filename2(cls, parent, path, name_filters):
        return new_path

    old_timestamp = task_view.task.sequence_timestamp
    # Save as
    monkeypatch.setattr(FileDialogEx, 'get_save_file_name', get_save_filename1)
    btn.clicked = True
    actions[1].triggered = True
    assert task_view.task.sequence_timestamp == old_timestamp

    monkeypatch.setattr(FileDialogEx, 'get_save_file_name', get_save_filename2)
    btn.clicked = True
    actions[1].triggered = True
    assert task_view.task.sequence_timestamp != old_timestamp
    assert task_view.task.sequence_path == new_path + '.pulse.ini'


def test_handling_error_in_loading(task_view, windows, monkeypatch):
    """Test handling an error when re-building the sequence.

    """
    from enaml.workbench.core.core_plugin import CorePlugin
    old = CorePlugin.invoke_command

    def false_invoke(self, cmd, *args, **kwargs):
        if cmd == 'ecpy.pulses.build_sequence':
            raise Exception()
        else:
            old(self, cmd, *args, **kwargs)

    monkeypatch.setattr(CorePlugin, 'invoke_command', false_invoke)

    with handle_dialog('accept'):
        load_sequence(task_view.root.core, task_view.task, task_view,
                      task_view.task.sequence_path)


@pytest.mark.timeout(10)
def test_changing_context_sequence(task_view, windows):
    """Test changing the context of a sequence.

    This should trigger a new validation of the driver.

    """
    show_widget(task_view)
    task = task_view.task
    task.selected_instrument = ('p', 'ecpy_pulses.TestDriver', 'c', 's')

    task.sequence.context = None
    assert task.selected_instrument[0]

    task.selected_instrument = ('p', '__dummy__',  'c', 's')
    with handle_question('yes'):
        task.sequence.context = TestContext()
    assert not task.selected_instrument[0]

    # Test changing the sequence.
    task.selected_instrument = ('p', '__dummy__',  'c', 's')
    with handle_question('yes'):
        task.sequence = sequence()
    assert not task.selected_instrument[0]

    # Check  the observer has been installed on the new sequence.
    task.selected_instrument = ('p', 'ecpy_pulses.TestDriver', 'c', 's')

    task.sequence.context = None
    assert task.selected_instrument[0]

    task.selected_instrument = ('p', '__dummy__',  'c', 's')
    with handle_question('yes'):
        task.sequence.context = TestContext()
    assert not task.selected_instrument[0]


def test_profile_filtering(task_view):
    """Test filtering the valid profiles based on context specifications.

    """
    from atom.api import Atom, Value

    class DInfos(Atom):
        id = Value()

    class MInfos(Atom):
        drivers = Value()

    class PInfos(Atom):
        model = Value()

    p1 = PInfos(model=MInfos(drivers=[DInfos(id='__dummy__'),
                                      DInfos(id='ecpy_pulses.TestDriver')]))
    p2 = PInfos(model=MInfos(drivers=[DInfos(id='dummy2')]))

    assert task_view.filter_profiles({'p1': p1, 'p2': p2}) == ['p1']

    del task_view.task.sequence.context

    assert (sorted(task_view.filter_profiles({'p1': p1, 'p2': p2})) ==
            ['p1', 'p2'])


def test_drivers_filtering(task_view):
    """Test filtering the valid drivers based on context specifications.

    """
    from atom.api import Atom, Value

    class DInfos(Atom):
        id = Value()

    d = DInfos(id='ecpy_pulses.TestDriver')

    drivers = task_view.filter_drivers([DInfos(id='__dummy__'), d])
    assert drivers == [d]

    del task_view.task.sequence.context

    assert len(task_view.filter_drivers([DInfos(id='__dummy__'), d])) == 2

