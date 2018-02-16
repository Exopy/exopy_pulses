# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Ramp like shape for a pulse.

"""
from numbers import Real

import numpy as np
from atom.api import Unicode, Enum

from ..utils.validators import Feval

from .base_shape import AbstractShape


class SlopeShape(AbstractShape):
    """Shape whose amplitude varies linearly with time.

    """
    #: Interpretation of the input values.
    #: Note that the slope is interpreted with respect to the context time
    #: unit.
    mode = Enum('Start/Stop', 'Start/Slope', 'Slope/Stop').tag(pref=True)

    #: First input parameter, will be interpreted based on the selected mode.
    def1 = Unicode('0.5').tag(pref=True, feval=Feval(types=Real))

    #: Second input parameter, will be interpreted based on the selected mode.
    def2 = Unicode('1.0').tag(pref=True, feval=Feval(types=Real))

    def eval_entries(self, root_vars, sequence_locals, missing, errors):
        """ Evaluate the parameters of the pulse shape.

        Parameters
        ----------
        root_vars : dict
            Global variables. As shapes and modulation cannot update them an
            empty dict is passed.

        sequence_locals : dict
            Known locals variables for the pulse sequence.

        missing : set
            Set of variables missing to evaluate some entries in the sequence.

        errors : dict
            Errors which occurred when trying to compile the pulse sequence.

        Returns
        -------
        result : bool
            Flag indicating whether or not the evaluation succeeded.

        """
        res = super(SlopeShape, self).eval_entries(root_vars, sequence_locals,
                                                   missing, errors)

        if res:
            if self.mode in ('Start/Stop', 'Start/Slope'):
                start = self._cache['def1']
                if not -1.0 <= start <= 1.0:
                    msg = 'Shape start must be between -1 and 1 (got %s).'
                    errors[self.format_error_id('start')] = msg % start
                    res = False
            if self.mode in ('Start/Stop', 'Slope/Stop'):
                stop = self._cache['def2']
                if not -1.0 <= stop <= 1.0:
                    msg = 'Shape stop must be between -1 and 1 (got %s).'
                    errors[self.format_error_id('stop')] = msg % stop
                    res = False
            if self.mode == 'Start/Slope':
                duration = sequence_locals['{}_duration'.format(self.index)]
                stop = self._cache['def1'] + self._cache['def2']*duration
                if not -1.0 <= stop <= 1.0:
                    msg = ('For the given slope and pulse duration, the stop '
                           'is not between -1 and 1 (got %s).')
                    errors[self.format_error_id('slope')] = msg % stop
                    res = False
            elif self.mode == 'Slope/Stop':
                duration = sequence_locals['{}_duration'.format(self.index)]
                start = self._cache['def2'] - self._cache['def1']*duration
                if not -1.0 <= start <= 1.0:
                    msg = ('For the given slope and pulse duration, the start '
                           'is not between -1 and 1 (got %s).')
                    errors[self.format_error_id('slope')] = msg % start
                    res = False

        return res

    def compute(self, time, unit):
        """ Computes the shape of the pulse at a given time.

        Parameters
        ----------
        time : ndarray
            Times at which to compute the modulation.

        unit : str
            Unit in which the time is expressed.

        Returns
        -------
        shape : ndarray
            Amplitude of the pulse.

        """
        if self.mode == 'Start/Stop':
            start = self._cache['def1']
            stop = self._cache['def2']
        elif self.mode == 'Start/Slope':
            start = self._cache['def1']
            stop = start + self._cache['def2']*time[-1]
        else:
            stop = self._cache['def2']
            start = stop - self._cache['def1']*time[-1]

        return np.linspace(start, stop, len(time))
