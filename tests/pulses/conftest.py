# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Load pulses plugin specific fixtures.

"""
import enaml
import pytest

with enaml.imports():
    from .contributions import PulsesContributions

pytest_plugins = str('exopy_pulses.testing.fixtures'),


@pytest.fixture
def workbench(pulses_workbench):
    """Simply register the contributions for testing.

    """
    pulses_workbench.register(PulsesContributions())
    return pulses_workbench
