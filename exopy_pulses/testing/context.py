# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Sequence context used for testing.

"""
from atom.api import Float, set_default
from exopy_pulses.pulses.contexts.base_context import BaseContext


class DummyContext(BaseContext):
    """Context limited to testing purposes.

    """
    logical_channels = set_default(('Ch1_L', 'Ch2_L'))

    analogical_channels = set_default(('Ch1_A', 'Ch2_A'))

    sampling = Float(1.0)

    def compile_and_transfer_sequence(self, sequence, driver=None):
        """Simply evaluate and simplify the underlying sequence.

        """
        items, errors = self.preprocess_sequence(sequence)
        if not items:
            return False, {}, errors
        return True, {'test': True}, {}

    def list_sequence_infos(self):
        return {'test': False}

    def _get_sampling_time(self):
        return self.sampling
