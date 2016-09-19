# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyHqcLegacy Authors, see AUTHORS for more details.
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
    from ecpy_pulses.version import __version__
