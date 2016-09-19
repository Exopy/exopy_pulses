# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test for base sequences filters.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import pytest

from ecpy_pulses.pulses.api import BaseSequence
from ecpy_pulses.pulses.sequences.conditional_sequence\
    import ConditionalSequence
from ecpy_pulses.pulses.infos import SequenceInfos
from ecpy_pulses.pulses.filters import (SequenceFilter, PySequenceFilter,
                                        TemplateFilter, MetadataSequenceFilter,
                                        GroupSequenceFilter,
                                        SubclassSequenceFilter)


@pytest.fixture
def sequences():
    return {'ecpy_pulses.BaseSequence':
            SequenceInfos(cls=BaseSequence, metadata={'meta': True}),
            'ecpy_pulses.ConditionalSequence':
            SequenceInfos(cls=ConditionalSequence,
                          metadata={'group': 'Logic', 'meta': False})}


@pytest.fixture
def templates():
    return {'Template1': ''}


def test_sequence_filter(sequences, templates):
    """Test the default sequence filter.

    """
    filtered = SequenceFilter().filter_sequences(sequences, templates)
    assert sorted(filtered) == sorted(list(sequences) + list(templates))


def test_py_sequence_filter(sequences, templates):
    """Test filtering only Python sequences.

    """
    filtered = PySequenceFilter().filter_sequences(sequences, templates)
    assert sorted(filtered) == sorted(sequences)


def test_template_sequence_filter(sequences, templates):
    """Test filtering only template sequences.

    """
    filtered = TemplateFilter().filter_sequences(sequences, templates)
    assert sorted(filtered) == sorted(templates)


def test_group_sequence_filter(sequences, templates):
    """Test filtering by group.

    """
    filtered = GroupSequenceFilter(group='Logic').filter_sequences(sequences,
                                                                   templates)
    assert sorted(filtered) == ['ecpy_pulses.ConditionalSequence']


def test_subclass_sequence_filter(sequences, templates):
    """Test filtering by subclass.

    """
    filt = SubclassSequenceFilter(subclass=ConditionalSequence)
    filtered = filt.filter_sequences(sequences, templates)
    assert sorted(filtered) == ['ecpy_pulses.ConditionalSequence']


def test_meta_sequence_filter(sequences, templates):
    """Test filtering by metadata.

    """
    filt = MetadataSequenceFilter(meta_key='meta', meta_value=True)
    filtered = filt.filter_sequences(sequences, templates)
    assert sorted(filtered) == ['ecpy_pulses.BaseSequence']
