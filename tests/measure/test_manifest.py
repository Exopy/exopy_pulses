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

with enaml.imports():
    from ecpy_pulses.measure.manifest import PulsesMeasureManifest

pytest_plugins = (str('ecpy.testing.measure.fixtures'),)


def test_manifest(measure_workbench):
    """Test the addition of the sequence editor.

    """
    measure_workbench.register(PulsesMeasureManifest())
    pl = measure_workbench.get_plugin('ecpy.measure')

    # XXX complete with editor id
    assert '' in pl.editors
