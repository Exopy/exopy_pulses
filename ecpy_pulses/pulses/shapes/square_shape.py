# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2017 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Most basic shape for an analogical pulse.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from numbers import Real

import numpy as np
from atom.api import Unicode

from ..utils.validators import Feval

from .base_shape import AbstractShape


class SquareShape(AbstractShape):
    """ Basic square pulse with a variable amplitude.

    """
    #: Amplitude of the pulse this should be a number between -1.0 and 1.0
    amplitude = Unicode('1.0').tag(pref=True, feval=Feval(types=Real))

    def eval_entries(self, root_vars, sequence_locals, missing, errors):
        """ Evaluate the amplitude of the pulse.

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
        res = super(SquareShape, self).eval_entries(root_vars, sequence_locals,
                                                    missing, errors)

        if res:
            if not -1.0 <= self._cache['amplitude'] <= 1.0:
                msg = 'Shape amplitude must be between -1 and 1.'
                errors[self.format_error_id('amplitude')] = msg
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
        return self._cache['amplitude'] * np.ones(len(time))
