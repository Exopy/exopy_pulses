# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2019 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Load exopy fixtures.

"""

pytest_plugins = ('exopy.testing.fixtures',
                  'exopy.testing.measurement.fixtures',
                  'exopy.testing.measurement.fixtures',
                  'exopy_pulses.testing.fixtures',
                  'exopy_pulses.testing.workspace.fixtures',
                  'exopy_pulses.testing.fixtures',
                  'exopy.testing.tasks.fixtures')
