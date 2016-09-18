# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Tests for the base context.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest

from ecpy_pulses.testing.context import TestContext


@pytest.fixture
def context():
    """BaseContext instance for testing.

    """
    return TestContext(sampling=0.1)


def test_len_sample(context):
    """Test the computation of the len_sample.

    """
    assert context.len_sample(1) == 10


def test_check_time(context):
    """Test validating a time.

    """
    assert context.check_time(0) == 0
    assert context.check_time(None) is None
    assert context.check_time(0.101) == 0.1

    context.rectify_time = False

    with pytest.raises(ValueError):
        context.check_time(0.101)

    context.tolerance = 0.01

    assert context.check_time(0.101) == 0.101


def test_getting_error_and_gloabl_vars_ids(context):
    """Test getting the id used for variables.

    """
    assert context.format_error_id('value') == 'context_value'
    with pytest.raises(RuntimeError):
        context.format_global_vars_id('value')


def test_context_id(context):
    """Test getting the context id.

    """
    assert context.context_id == 'ecpy_pulses.TestContext'
