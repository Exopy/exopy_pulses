# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Fixtures for testing ecpy_pulses related components.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import os

import pytest
from pprint import pformat

import enaml
from enaml.workbench.api import Workbench

from ..pulses.utils.sequences_io import save_sequence_prefs

with enaml.imports():
    from enaml.workbench.core.core_manifest import CoreManifest

    from ecpy.app.app_manifest import AppManifest
    from ecpy.app.preferences.manifest import PreferencesManifest
    from ecpy.app.dependencies.manifest import DependenciesManifest
    from ecpy.app.states.manifest import StateManifest
    from ecpy.app.errors.manifest import ErrorsManifest
    from ecpy.app.errors.plugin import ErrorsPlugin
    from ecpy_pulses.pulses.manifest import PulsesManagerManifest


pytests_plugin = str('ecpy.testing.fixtures'),


@pytest.yield_fixture
def pulses_workbench(monkeypatch, app_dir):
    """Setup the workbench in such a way that the pulses manager can be tested.

    """
    def exit_err(self):
        """Turn error reporting into an exception.

        """
        if self._delayed:
            raise Exception('Unexpected exceptions occured :\n' +
                            pformat(self._delayed))

    monkeypatch.setattr(ErrorsPlugin, 'exit_error_gathering', exit_err)
    workbench = Workbench()
    workbench.register(CoreManifest())
    workbench.register(AppManifest())
    workbench.register(PreferencesManifest())
    workbench.register(ErrorsManifest())
    workbench.register(StateManifest())
    workbench.register(DependenciesManifest())
    workbench.register(PulsesManagerManifest())

    yield workbench

    for m_id in ('ecpy.pulses', 'ecpy.app.dependencies', 'ecpy.app.errors',
                 'ecpy.app.preferences', 'ecpy.app'):
        try:
            workbench.unregister(m_id)
        except Exception:
            pass


@pytest.fixture
def pulses_plugin(pulses_workbench):
    """Setup the workbench and return the pulses manager plugin.

    """
    return pulses_workbench.get_plugin('ecpy.pulses')


@pytest.fixture
def template_sequence(pulses_plugin):
    """Create a template sequence and make sure the plugin pick it up.

    """
    from ecpy_pulses.pulses.pulse import Pulse
    from ecpy_pulses.pulses.sequences.base_sequences import (RootSequence,
                                                             BaseSequence)
    from ecpy_pulses.pulses.shapes.square_shape import SquareShape
    from ecpy_pulses.pulses.contexts.template_context import TemplateContext

    root = RootSequence()
    context = TemplateContext(logical_channels=['A', 'B'],
                              analogical_channels=['Ch1', 'Ch2'],
                              channel_mapping={'A': '', 'B': '', 'Ch1': '',
                                               'Ch2': ''})
    root.context = context
    root.local_vars = {'a': '1.5'}

    pulse1 = Pulse(channel='A', def_1='1.0', def_2='{a}')
    pulse2 = Pulse(channel='B', def_1='{a} + 1.0', def_2='3.0')
    pulse3 = Pulse(channel='Ch1', def_1='{2_stop} + 0.5', def_2='{b}',
                   kind='Analogical', shape=SquareShape())
    seq = BaseSequence()
    seq.add_child_item(0, Pulse(channel='Ch2', def_1='{2_stop} + 0.5',
                       def_2='{sequence_end}', kind='Analogical',
                       shape=SquareShape()))
    for i in [pulse1, pulse2, seq,  pulse3][::-1]:
        root.add_child_item(0, i)

    pref = root.preferences_from_members()
    pref['template_vars'] = repr(dict(b=''))
    del pref['item_id']
    del pref['external_vars']
    del pref['time_constrained']

    temp_path = os.path.join(pulses_plugin.templates_folders[0],
                             '__dummy__.temp_pulse.ini')
    save_sequence_prefs(temp_path, pref, 'dummy doc')

    pulses_plugin._refresh_known_template_sequences()

    return '__dummy__'
