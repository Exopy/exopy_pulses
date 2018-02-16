# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Exopy Pulses plugin public interface.

"""
import enaml

from .declarations import (Sequence, Sequences, Shape, Shapes,
                           Context, Contexts, SequenceConfig, SequenceConfigs)
from .sequences.base_sequences import (AbstractSequence, BaseSequence,
                                       RootSequence)
from .pulse import Pulse
from .item import Item
from .shapes.base_shape import AbstractShape
from .contexts.base_context import BaseContext, TIME_CONVERSION
from .utils.validators import Feval, SkipEmpty

with enaml.imports():
    from .sequences.views.abstract_sequence_view import AbstractSequenceView
    from .sequences.views.base_sequences_views import BaseSequenceView
    from .contexts.views.base_context_view import BaseContextView
    from .shapes.views.base_shape_view import AbstractShapeView

__all__ = ['Sequence', 'Sequences', 'Shape', 'Shapes', 'Context', 'Contexts',
           'SequenceConfig', 'SequenceConfigs', 'AbstractSequence',
           'AbstractSequenceView', 'BaseSequence', 'BaseSequenceView',
           'RootSequence', 'Pulse', 'Item', 'BaseContext', 'BaseContextView',
           'AbstractShape', 'AbstractShapeView', 'Feval', 'SkipEmpty',
           'TIME_CONVERSION']
