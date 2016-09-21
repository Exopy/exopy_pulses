# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Objects used to store filters, sequences and configs in the manager.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from atom.api import Atom, Subclass, Dict, Coerced
import enaml

from .sequences.base_sequences import AbstractSequence
from .configs.base_config import AbstractConfig
from .contexts.base_context import BaseContext
from .shapes.base_shape import AbstractShape
from .pulse import Pulse

with enaml.imports():
    from .sequences.views.abstract_sequence_view import AbstractSequenceView
    from .configs.base_config_views import AbstractConfigView
    from .shapes.views.base_shape_view import AbstractShapeView
    from .contexts.views.base_context_view import BaseContextView
    from .pulse_view import PulseView


# HINT : the notion of dependencies is currently unused but there in case
# we need it

class ObjectDependentInfos(Atom):
    """ Base info object for everything with dependencies.

    """
    #: Runtime dependencies ids of this object.
    dependencies = Coerced(set, ())


class SequenceInfos(ObjectDependentInfos):
    """An object used to store the informations about a sequence.

    """
    #: Class representing this sequence.
    cls = Subclass(AbstractSequence)

    #: Widget associated with this sequence.
    view = Subclass(AbstractSequenceView)

    #: Metadata associated with this sequence such as group, looping
    #: capabilities, etc
    metadata = Dict()


class PulseInfos(ObjectDependentInfos):
    """An object used to store the informations about a pulse.

    """
    #: Class representing this pulse.
    cls = Subclass(Pulse)

    #: Widget associated with this pulse.
    view = Subclass(PulseView)

    #: Metadata associated with this sequence such as group, looping
    #: capabilities, etc
    metadata = Dict()


class ConfigInfos(Atom):
    """An object used to store the informations about a sequence configurer.

    """
    #: Class representing this configurer.
    cls = Subclass(AbstractConfig)

    #: Widget associated with this configurer.
    view = Subclass(AbstractConfigView)


class ContextInfos(ObjectDependentInfos):
    """Object used to store informations about a Context, declared in a manifest.

    """
    #: Class representing this context.
    cls = Subclass(BaseContext)

    #: Widget associated with this context.
    view = Subclass(BaseContextView)

    #: List of instrument supported by this context.
    instruments = Coerced(set, ())

    #: Metadata associated with this context such as who knows what.
    metadata = Dict()


class ShapeInfos(ObjectDependentInfos):
    """Object used to store informations about a shape.

    """
    #: Class representing this Shape.
    cls = Subclass(AbstractShape)

    #: Widget associated with this Shape.
    view = Subclass(AbstractShapeView)

    #: Metadata associated with this shape such as I have no idea what.
    metadata = Dict()
