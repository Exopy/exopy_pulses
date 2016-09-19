# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test dependency collection functions.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from operator import getitem

import pytest

from ecpy.app.dependencies.api import BuildDependency
from ecpy_pulses.pulses.sequences.base_sequences import BaseSequence
from ecpy_pulses.pulses.pulse import Pulse
from ecpy_pulses.pulses.shapes.modulation import Modulation
from ecpy_pulses.pulses.shapes.square_shape import SquareShape
from ecpy_pulses.testing.context import TestContext


@pytest.fixture
def item_dep_collector(workbench):
    """Collector for items dependencies.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    dep_ext = [e for e in plugin.manifest.extensions
               if e.id == 'build_deps'][0]
    return [b for b in dep_ext.get_children(BuildDependency)
            if b.id == 'ecpy.pulses.items'][0]


@pytest.fixture
def shape_dep_collector(workbench):
    """Collector for shapes dependencies.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    dep_ext = [e for e in plugin.manifest.extensions
               if e.id == 'build_deps'][0]
    return [b for b in dep_ext.get_children(BuildDependency)
            if b.id == 'ecpy.pulses.shapes'][0]


@pytest.fixture
def context_dep_collector(workbench):
    """Collector for contexts dependencies.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    dep_ext = [e for e in plugin.manifest.extensions
               if e.id == 'build_deps'][0]
    return [b for b in dep_ext.get_children(BuildDependency)
            if b.id == 'ecpy.pulses.contexts'][0]


@pytest.fixture
def modulation_dep_collector(workbench):
    """Collector for modulation dependencies.

    """
    plugin = workbench.get_plugin('ecpy.pulses')
    dep_ext = [e for e in plugin.manifest.extensions
               if e.id == 'build_deps'][0]
    return [b for b in dep_ext.get_children(BuildDependency)
            if b.id == 'ecpy.pulses.modulation'][0]


def test_analysing_item_dependencies(workbench, item_dep_collector):
    """Test analysing the dependencies of an item.

    """
    dep = set()
    errors = dict()
    run = item_dep_collector.analyse(workbench, BaseSequence(), getattr,
                                     dep, errors)

    assert not run
    assert 'ecpy_pulses.BaseSequence' in dep
    assert not errors

    dep = set()
    errors = dict()
    run = item_dep_collector.analyse(workbench, Pulse(), getattr,
                                     dep, errors)

    assert not run
    assert 'ecpy_pulses.Pulse' in dep
    assert not errors

    dep = set()
    run = item_dep_collector.analyse(workbench, {'item_id': '__dummy__'},
                                     getitem, dep, errors)
    assert not run
    assert not dep
    assert '__dummy__' in errors


def test_validating_item_dependencies(workbench, item_dep_collector):
    """Test validating item dependencies.

    """
    errors = {}
    item_dep_collector.validate(workbench,
                                {'ecpy_pulses.BaseSequence', '__dummy__'},
                                errors)
    assert 'ecpy_pulses.BaseSequence' not in errors
    assert '__dummy__' in errors


def test_collecting_item_dependencies(workbench, item_dep_collector):
    """Test collecting the dependencies found in an item.

    """
    dependencies = dict.fromkeys(['ecpy_pulses.BaseSequence', '__dummy__'])
    errors = {}
    item_dep_collector.collect(workbench, dependencies, errors)
    assert dependencies['ecpy_pulses.BaseSequence'] is not None
    assert '__dummy__' in errors


def test_analysing_shape_dependencies(workbench, shape_dep_collector):
    """Test analysing the dependencies of an shape.

    """
    dep = set()
    errors = dict()
    run = shape_dep_collector.analyse(workbench, SquareShape(), getattr,
                                      dep, errors)

    assert not run
    assert 'ecpy_pulses.SquareShape' in dep
    assert not errors

    dep = set()
    run = shape_dep_collector.analyse(workbench, {'shape_id': '__dummy__'},
                                      getitem, dep, errors)
    assert not run
    assert not dep
    assert '__dummy__' in errors


def test_validating_shape_dependencies(workbench, shape_dep_collector):
    """Test validating shape dependencies.

    """
    errors = {}
    shape_dep_collector.validate(workbench,
                                 {'ecpy_pulses.SquareShape', '__dummy__'},
                                 errors)
    assert 'ecpy_pulses.SquareShape' not in errors
    assert '__dummy__' in errors


def test_collecting_shape_dependencies(workbench, shape_dep_collector):
    """Test collecting the dependencies found in a shape.

    """
    dependencies = dict.fromkeys(['ecpy_pulses.SquareShape', '__dummy__'])
    errors = {}
    shape_dep_collector.collect(workbench, dependencies, errors)
    assert dependencies['ecpy_pulses.SquareShape'] is not None
    assert '__dummy__' in errors


def test_analysing_context_dependencies(workbench, context_dep_collector):
    """Test analysing the dependencies of an context.

    """
    dep = set()
    errors = dict()
    run = context_dep_collector.analyse(workbench, TestContext(), getattr,
                                        dep, errors)

    assert not run
    assert 'ecpy_pulses.TestContext' in dep
    assert not errors

    dep = set()
    run = context_dep_collector.analyse(workbench, {'context_id': '__dummy__'},
                                        getitem, dep, errors)
    assert not run
    assert not dep
    assert '__dummy__' in errors


def test_validating_context_dependencies(workbench, context_dep_collector):
    """Test validating context dependencies.

    """
    errors = {}
    context_dep_collector.validate(workbench,
                                   {'ecpy_pulses.TestContext', '__dummy__'},
                                   errors)
    assert 'ecpy_pulses.TestContext' not in errors
    assert '__dummy__' in errors


def test_collecting_context_dependencies(workbench, context_dep_collector):
    """Test collecting the dependencies found in a context.

    """
    dependencies = dict.fromkeys(['ecpy_pulses.TestContext', '__dummy__'])
    errors = {}
    context_dep_collector.collect(workbench, dependencies, errors)
    assert dependencies['ecpy_pulses.TestContext'] is not None
    assert '__dummy__' in errors


def test_analysing_modulation_dependencies(workbench,
                                           modulation_dep_collector):
    """Test analysing the dependencies of a modulation.

    """
    dep = set()
    errors = dict()
    run = modulation_dep_collector.analyse(workbench, Modulation(), getattr,
                                           dep, errors)

    assert not run
    assert 'ecpy_pulses.Modulation' in dep
    assert not errors

    dep = set()
    run = modulation_dep_collector.analyse(workbench,
                                           {'modulation_id': '__dummy__'},
                                           getitem, dep, errors)
    assert not run
    assert not dep
    assert '__dummy__' in errors


def test_validating_modulation_dependencies(workbench,
                                            modulation_dep_collector):
    """Test validating modulation dependencies.

    """
    errors = {}
    modulation_dep_collector.validate(workbench,
                                      {'ecpy_pulses.Modulation', '__dummy__'},
                                      errors)
    assert 'ecpy_pulses.Modulation' not in errors
    assert '__dummy__' in errors


def test_collecting_modulation_dependencies(workbench,
                                            modulation_dep_collector):
    """Test collecting the dependencies found in a modulation.

    """
    dependencies = dict.fromkeys(['ecpy_pulses.Modulation', '__dummy__'])
    errors = {}
    modulation_dep_collector.collect(workbench, dependencies, errors)
    assert dependencies['ecpy_pulses.Modulation'] is not None
    assert '__dummy__' in errors


def test_collect_dependencies(workbench):
    """Test collecting build dependencies.

    """
    from ecpy_pulses.pulses.sequences.base_sequences import RootSequence
    root = RootSequence(context=TestContext())

    pulse1 = Pulse(def_1='1.0', def_2='{7_start} - 1.0')
    pulse2 = Pulse(def_1='{a} + 1.0', def_2='{6_start} + 1.0')
    pulse3 = Pulse(def_1='{3_stop} + 0.5', def_2='10.0')
    pulse4 = Pulse(def_1='2.0', def_2='0.5', def_mode='Start/Duration')
    pulse5 = Pulse(def_1='{1_stop}', def_2='0.5',
                   def_mode='Start/Duration')
    pulse5.shape = SquareShape(amplitude='0.5')
    pulse5.kind = 'Analogical'

    pulse5.modulation.frequency = '1.0**'
    pulse5.modulation.phase = '1.0'
    pulse5.modulation.activated = True

    sequence2 = BaseSequence()
    sequence2.add_child_item(0, pulse3)
    sequence1 = BaseSequence()
    sequence1.add_child_item(0, pulse2)
    sequence1.add_child_item(1, sequence2)
    sequence1.add_child_item(2, pulse4)

    root.add_child_item(0, pulse1)
    root.add_child_item(1, sequence1)
    root.add_child_item(2, pulse5)

    core = workbench.get_plugin(u'enaml.workbench.core')
    com = 'ecpy.app.dependencies.analyse'
    dep = core.invoke_command(com, {'obj': root, 'dependencies': 'build'})
    assert not dep.errors

    com = 'ecpy.app.dependencies.collect'
    dep = core.invoke_command(com, {'kind': 'build',
                                    'dependencies': dep.dependencies})

    assert not dep.errors
    assert 'ecpy.pulses.items' in dep.dependencies
    assert 'ecpy.pulses.contexts' in dep.dependencies
    assert 'ecpy.pulses.shapes' in dep.dependencies
    assert 'ecpy.pulses.modulation' in dep.dependencies
