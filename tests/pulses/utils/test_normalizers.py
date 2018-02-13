# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the names normalizers.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from exopy_pulses.pulses.utils.normalizers import (normalize_sequence_name,
                                                  normalize_context_name,
                                                  normalize_shape_name)

TEST = 'exopy_pulses.AnIDIOTDumbDummy_Test'


def test_sequence_name_normalizer():
    """Test normalizing sequences names.

    """
    assert (normalize_sequence_name(TEST + 'Sequence') ==
            'exopy_pulses.An IDIOT dumb dummy test')

    assert normalize_sequence_name('test.temp_pulse.ini') == 'Test'


def test_shape_name_normalizer():
    """Test normalizing a shape name.

    """
    assert (normalize_shape_name(TEST + 'Shape') ==
            'exopy_pulses.An IDIOT dumb dummy test')


def test_context_name_normalizer():
    """Test normalizing a context name.

    """
    assert (normalize_context_name(TEST + 'Context') ==
            'exopy_pulses.An IDIOT dumb dummy test')
