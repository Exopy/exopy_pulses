# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test basic capabilities of an item.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest

from ecpy_pulses.pulses.item import Item
from ecpy_pulses.pulses.sequences.base_sequences import RootSequence
from ecpy_pulses.testing.context import TestContext


@pytest.fixture
def item():
    return Item(root=RootSequence(context=TestContext()))


def test_item_id(item):
    """Test getting the id of an item.

    """
    assert item.item_id == 'ecpy_pulses.Item'


def test_removing_root(item):
    """Test removing the reference to the root from an item.

    """
    item.root = None
    assert not item.has_root
