# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Load pulses plugin specific fixtures.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import enaml
import pytest

with enaml.imports():
    from .contributions import PulsesContributions

pytest_plugins = str('ecpy_pulses.testing.fixtures'),


@pytest.fixture
def workbench(pulses_workbench):
    """Simply register the contributions for testing.

    """
    pulses_workbench.register(PulsesContributions())
    return pulses_workbench
