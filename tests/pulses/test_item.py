# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test basic capabilities of an item.

"""
import pytest

from exopy_pulses.pulses.item import Item
from exopy_pulses.pulses.sequences.base_sequences import RootSequence
from exopy_pulses.testing.context import TestingContext


@pytest.fixture
def item():
    return Item(root=RootSequence(context=TestingContext()))


def test_item_id(item):
    """Test getting the id of an item.

    """
    assert item.item_id == 'exopy_pulses.Item'


def test_removing_root(item):
    """Test removing the reference to the root from an item.

    """
    item.root = None
    assert not item.has_root
