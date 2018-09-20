# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Most basic shape for an analogical pulse.

"""
from numbers import Real

import numpy as np
from scipy.signal import convolve
from atom.api import Unicode

from ..utils.validators import Feval

from .base_shape import AbstractShape


class ArbitraryShape(AbstractShape):
    """ Arbitrary pulse with a variable amplitude and sigma.

    """
    #: Amplitude of the pulse this should be a number between -1.0 and 1.0
    item = Unicode('0').tag(pref=True, feval=Feval(types=Real))
    amplitude = Unicode('1.0').tag(pref=True, feval=Feval(types=Real))
    sigma = Unicode('10.0').tag(pref=True, feval=Feval(types=Real))

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
        res = super(ArbitraryShape, self).eval_entries(root_vars, sequence_locals,
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
        amp = self._cache['amplitude']
        item = self._cache['item']
        sigma = self._cache['sigma']

        shape_array =np.array([[ 0.  ,  0.7425981 ,  0.67598838, -0.96084179,  0.54595441,  0.32625353,  0.09909314,  0.91510778,  0.64309465,  0.  ],
                               [ 0.  , -0.79977044, -0.62003171,  0.77406773, -0.23440129,  -0.87675365, -0.6848697 , -0.3033923 , -0.93459392,  0.  ],
                               [ 0.  , -0.79000746,  0.19294993, -0.27256032, -0.06989739,  -0.45341508,  0.64134526, -0.34669047,  0.23336246,  0. ],
                               [ 0.  ,  0.18304203, -0.25811938, -0.77773187,  0.87413684,  0.97542405, -0.564533  , -0.98984496, -0.330256  ,  0.  ],
                               [ 0.  , -0.73491874,  0.54894737, -0.54666462, -0.34280741,  0.18528991,  0.94649001,  0.09240971,  0.58266813,  0.  ]])
        n_time = len(time)
        n_bins = len(shape_array[0])
        n_time_bins = n_time-n_time%n_bins
        shape = (np.ones(n_time_bins).reshape(n_bins, -1).T*shape_array[int(item)]).T.flatten()
        shape = list(shape)
        shape += [0.0 for ii in range(n_time%n_bins)]
#        print(time)
#        print(shape)
        shape = np.asarray(shape)

        t0 = (time[0]+time[-1])/2
#        print(t0)
        dt = time[1]-time[0]
        gauss = np.exp(-(time-t0)**2/2/sigma**2)
        
        pulse_shape = convolve(shape, gauss, mode='same')
        full_shape = amp*pulse_shape/(dt*(pulse_shape)**2).sum()**0.5
        return full_shape
