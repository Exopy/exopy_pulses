# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the version script

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


def test_version():
    """Try importing the version.

    """
    from exopy_pulses.version import __version__
