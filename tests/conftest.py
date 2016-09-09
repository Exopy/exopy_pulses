# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Load ecpy fixtures.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

# HINT workaround a completely stupid bug in Py2
from ecpy_pulses.pulses.utils.normalizers import (normalize_sequence_name,
                                                  normalize_context_name,
                                                  normalize_shape_name)

pytest_plugins = (str('ecpy.testing.fixtures'),)
