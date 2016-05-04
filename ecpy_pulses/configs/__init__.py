# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
from ..pulses.sequences.base_sequences import Sequence
from .base_config import SequenceConfig


# Defining the special config dictionnary used by the builder to select the
# right config task class.
SEQUENCE_CONFIG = {Sequence: SequenceConfig}

import enaml
with enaml.imports():
    from .base_config_views import SimpleView, NoneView

CONFIG_MAP_VIEW = {type(None): NoneView, SequenceConfig: SimpleView}
