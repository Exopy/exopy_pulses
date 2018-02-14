# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Declaration for the Template Context.

This context is used to provide channel mapping when saving a sequence as
a Template.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from atom.api import Float, List, Dict, Typed

from .base_context import BaseContext
from ..sequences.template_sequence import TemplateSequence


class TemplateContext(BaseContext):
    """Context mapping the temmplate channels to real instrument channels.

    """
    #: Declared analogical channels to use inside the template.
    analogical_channels = List().tag(pref=True)

    #: Declared logical channels to use inside the template.
    logical_channels = List().tag(pref=True)

    #: Mapping between the template channels and the channels of the true
    #: context.
    channel_mapping = Dict().tag(pref=True)

    #: Reference to the template sequence to which this context is attached.
    template_sequence = Typed(TemplateSequence)

    def prepare_evaluation(self, errors):
        """Copy the necessary information from the root context.

        """
        context = self.template_sequence.root.context
        self._sampling_time = context.sampling_time
        self.time_unit = context.time_unit
        self.rectify_time = context.rectify_time
        self.tolerance = context.tolerance
        self.supported_sequences = context.supported_sequences
        mess = 'Missing/Erroneous mapping for channels {}'
        mapping = self.channel_mapping
        c_errors = [c for c in self.analogical_channels
                    if c not in mapping or
                    mapping[c] not in context.analogical_channels]
        c_errors.extend([c for c in self.logical_channels
                         if c not in mapping or
                         mapping[c] not in context.logical_channels])
        if c_errors:
            errors['{}-context'.format(self.template_sequence.name)] = \
                mess.format(c_errors)
            return False

        return True

    # --- Private API ---------------------------------------------------------

    _sampling_time = Float()

    def _get_sampling_time(self):
        """ Getter for the sampling time prop of BaseContext.

        """
        return self._sampling_time
