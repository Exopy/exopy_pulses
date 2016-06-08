# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


from atom.api import (Unicode, Enum, Float, Bool, Constant)
from math import pi as Pi
import numpy as np

from ecpy.utils.atom_util import HasPrefAtom
from ..utils.entry_eval import eval_entry

FREQ_TIME_UNIT_MAP = {'s': {'Hz': 1, 'kHz': 1000, 'MHz': 1e6, 'GHz': 1e9},
                      'ms': {'Hz': 1e-3, 'kHz': 1, 'MHz': 1e3, 'GHz': 1e6},
                      'mus': {'Hz': 1e-6, 'kHz': 1e-3, 'MHz': 1, 'GHz': 1e3},
                      'ns': {'Hz': 1e-9, 'kHz': 1e-6, 'MHz': 1e-3, 'GHz': 1}}

DEP_TYPE = 'ecpy.pulses.modulation'


class Modulation(HasPrefAtom):
    """ Modulation to apply to the pulse.

    Only sinusoidal and cosinusoidal modulations are supported. As the
    modulation is applied on top of the shape is more complicated modulation
    are requested they can be implemented in cutom shapes.

    """
    #: Identifier for the build dependency collector
    dep_type = Constant(DEP_TYPE).tag(pref=True)

    #: Flag indicating whether or not the modulation is activated.
    activated = Bool().tag(pref=True)

    #: Kind of modulation to use : cos or sin
    kind = Enum('sin', 'cos').tag(pref=True)

    #: Frequency of modulation to use.
    frequency = Unicode().tag(pref=True)

    #: Unit of the frequency use for the modulation.
    frequency_unit = Enum('MHz', 'GHz', 'kHz', 'Hz').tag(pref=True)

    #: Phase to use in the modulation.
    phase = Unicode('0.0').tag(pref=True)

    #: Unit of the phase used in the modulation.
    phase_unit = Enum('rad', 'deg').tag(pref=True)

    def eval_entries(self, sequence_locals, missing, errors, index):
        """ Evaluate amplitude, frequency, and phase.

        Parameters
        ----------
        sequence_locals : dict
            Known locals variables for the pulse sequence.

        missing : set
            Set of variables missing to evaluate some entries in the sequence.

        errors : dict
            Errors which occurred when trying to compile the pulse sequence.

        index : int
            Index of the pulse to which this Modulation object belongs.

        Returns
        -------
        result : bool
            Flag indicating whether or not the evaluation succeeded.

        """
        if not self.activated:
            return True

        prefix = '{}_'.format(index) + 'mod_'
        eval_success = True

        # Computing frequency
        freq = None
        try:
            freq = eval_entry(self.frequency, sequence_locals, missing)
        except Exception as e:
            eval_success = False
            errors[prefix + 'frequency'] = repr(e)

        if freq is not None:
            self._frequency = freq
        else:
            eval_success = False
            m = 'Failed to evaluate {} expression: {}'.format('frequency',
                                                              self.frequency)
            errors[prefix + 'frequency'] = m

        # Computing phase
        phase = None
        try:
            phase = eval_entry(self.phase, sequence_locals, missing)
            self._phase = phase
        except Exception as e:
            eval_success = False
            errors[prefix + 'phase'] = repr(e)

        if phase is not None:
            self._phase = phase
        else:
            eval_success = False
            m = 'Failed to evaluate {} expression: {}'.format('phase',
                                                              self.phase)
            errors[prefix + 'phase'] = m

        return eval_success

    def compute(self, time, unit):
        """ Computes the modulation impact at a given time.

        Parameters
        ----------
        time : ndarray
            Times at which to compute the modulation.

        unit : str
            Unit in which the time is expressed.

        Returns
        -------
        modulation : ndarray
            Values by which to multiply the shape to get the pulse value at
            time t.

        """
        if not self.activated:
            return 1

        unit_corr = 2 * Pi * FREQ_TIME_UNIT_MAP[unit][self.frequency_unit]
        phase = self._phase
        if self.phase_unit == 'deg':
            phase *= Pi / 180

        if self.kind == 'sin':
            return np.sin(unit_corr * self._frequency * time + phase)
        else:
            return np.cos(unit_corr * self._frequency * time + phase)

    # --- Private API ---------------------------------------------------------

    _frequency = Float()

    _phase = Float()
