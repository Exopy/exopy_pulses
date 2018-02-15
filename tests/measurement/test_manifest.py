# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Check that the manifest does register the editor.

"""
import enaml

from exopy_pulses.tasks.tasks.instrs.transfer_sequence_task\
    import TransferPulseSequenceTask

with enaml.imports():
    from exopy_pulses.measurement.manifest import PulsesMeasurementManifest

pytest_plugins = (str('exopy.testing.measurement.fixtures'),)


def test_manifest(measurement_workbench):
    """Test the addition of the sequence editor.

    """
    measurement_workbench.register(PulsesMeasurementManifest())
    pl = measurement_workbench.get_plugin('exopy.measurement')

    assert 'exopy_pulses.pulse_sequence' in pl.editors

    decls = pl.get_declarations('editor', ['exopy_pulses.pulse_sequence'])
    decl = decls['exopy_pulses.pulse_sequence']

    # Check the is_meant_for function
    assert decl.is_meant_for(measurement_workbench, TransferPulseSequenceTask())
    assert not decl.is_meant_for(measurement_workbench, object())

    # Test editor creation
    ed = decl.new(measurement_workbench)
    assert ed
