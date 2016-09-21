# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Check that the manifest does register the editor.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import enaml

from ecpy_pulses.tasks.tasks.instrs.transfer_sequence_task\
    import TransferPulseSequenceTask

with enaml.imports():
    from ecpy_pulses.measure.manifest import PulsesMeasureManifest

pytest_plugins = (str('ecpy.testing.measure.fixtures'),)


def test_manifest(measure_workbench):
    """Test the addition of the sequence editor.

    """
    measure_workbench.register(PulsesMeasureManifest())
    pl = measure_workbench.get_plugin('ecpy.measure')

    assert 'ecpy_pulses.pulse_sequence' in pl.editors

    decls = pl.get_declarations('editor', ['ecpy_pulses.pulse_sequence'])
    decl = decls['ecpy_pulses.pulse_sequence']

    # Check the is_meant_for function
    assert decl.is_meant_for(measure_workbench, TransferPulseSequenceTask())
    assert not decl.is_meant_for(measure_workbench, object())

    # Test editor creation
    ed = decl.new(measure_workbench)
    assert ed
