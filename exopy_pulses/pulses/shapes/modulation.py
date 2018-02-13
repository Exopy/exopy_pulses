# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Modulation to overlap on the shape of the pulse.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from math import pi as Pi
from numbers import Real

import numpy as np
from atom.api import Unicode, Enum, Bool, Constant, Int

from ..utils.validators import Feval
from ..utils.entry_eval import HasEvaluableFields

FREQ_TIME_UNIT_MAP = {'s': {'Hz': 1, 'kHz': 1000, 'MHz': 1e6, 'GHz': 1e9},
                      'ms': {'Hz': 1e-3, 'kHz': 1, 'MHz': 1e3, 'GHz': 1e6},
                      'mus': {'Hz': 1e-6, 'kHz': 1e-3, 'MHz': 1, 'GHz': 1e3},
                      'ns': {'Hz': 1e-9, 'kHz': 1e-6, 'MHz': 1e-3, 'GHz': 1}}

DEP_TYPE = 'exopy.pulses.modulation'


class Modulation(HasEvaluableFields):
    """ Modulation to apply to the pulse.

    Only sinusoidal and cosinusoidal modulations are supported. As the
    modulation is applied on top of the shape is more complicated modulation
    are requested they can be implemented in cutom shapes.

    """
    #: Identifier for the build dependency collector
    dep_type = Constant(DEP_TYPE).tag(pref=True)

    #: Id of the modulation used to query it from the plugin.
    modulation_id = Unicode().tag(pref=True)

    #: Flag indicating whether or not the modulation is activated.
    activated = Bool().tag(pref=True)

    #: Kind of modulation to use : cos or sin
    kind = Enum('sin', 'cos').tag(pref=True)

    #: Frequency of modulation to use.
    frequency = Unicode().tag(pref=True, feval=Feval(types=Real))

    #: Unit of the frequency use for the modulation.
    frequency_unit = Enum('MHz', 'GHz', 'kHz', 'Hz').tag(pref=True)

    #: Phase to use in the modulation.
    phase = Unicode('0.0').tag(pref=True, feval=Feval(types=Real))

    #: Unit of the phase used in the modulation.
    phase_unit = Enum('rad', 'deg').tag(pref=True)

    #: Index of the parent pulse. This is set whe evaluating the entries.
    index = Int()

    def eval_entries(self, root_vars, sequence_locals, missing, errors):
        """ Evaluate amplitude, frequency, and phase.

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
        if not self.activated:
            return True

        return super(Modulation, self).eval_entries(root_vars, sequence_locals,
                                                    missing, errors)

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
        phase = self._cache['phase']
        if self.phase_unit == 'deg':
            phase *= Pi / 180

        if self.kind == 'sin':
            return np.sin(unit_corr * self._cache['frequency'] * time + phase)
        else:
            return np.cos(unit_corr * self._cache['frequency'] * time + phase)

    def format_error_id(self, member):
        """Assemble the id used to report an evaluation error.

        """
        return '{}_modulation_{}'.format(self.index, member)

    def format_global_vars_id(self, member):
        """Modulation is not allowed to store in the global namespace so raise.

        """
        msg = 'Modulation cannot store values as global (from pulse {})'
        raise RuntimeError(msg.format(self.index))

    # --- Private API ---------------------------------------------------------

    def _default_modulation_id(self):
        """Compute the class id.

        """
        pack, _ = self.__module__.split('.', 1)
        return pack + '.' + type(self).__name__
