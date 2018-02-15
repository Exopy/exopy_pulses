# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test listing the contributed manifests.

"""
from exopy_pulses import list_manifests


def test_list_manifests():
    """Try listing the manifests to register.

    """
    assert len(list_manifests()) == 3
