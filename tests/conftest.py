# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Load exopy fixtures.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

# HINT workaround a completely stupid bug in Py2
from exopy_pulses.pulses.utils.normalizers import (normalize_sequence_name,
                                                   normalize_context_name,
                                                   normalize_shape_name)

pytest_plugins = (str('exopy.testing.fixtures'),)
