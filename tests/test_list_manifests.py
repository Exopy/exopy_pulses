# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test listing the contributed manifests.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from ecpy_pulses import list_manifests


def test_list_manifests():
    """Try listing the manifests to register.

    """
    assert len(list_manifests()) == 3
