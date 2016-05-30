# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


from atom.api import (Enum, Unicode, Bool, Float, Property, Tuple, List,
                      Constant)
from inspect import cleandoc

from ecpy.utils.atom_util import HasPrefAtom

DEP_TYPE = 'ecpy.pulses.contexts'

# Time conversion dictionary first key is the original unit, second the final
# one.
TIME_CONVERSION = {'s': {'s': 1, 'ms': 1e3, 'mus': 1e6, 'ns': 1e9},
                   'ms': {'s': 1e-3, 'ms': 1, 'mus': 1e3, 'ns': 1e6},
                   'mus': {'s': 1e-6, 'ms': 1e-3, 'mus': 1, 'ns': 1e3},
                   'ns': {'s': 1e-9, 'ms': 1e-6, 'mus': 1e-3, 'ns': 1}}


class BaseContext(HasPrefAtom):
    """Base Class describing a Context

    """
    #: Identifier for the build dependency collector
    dep_type = Constant(DEP_TYPE).tag(pref=True)

    #: Time unit.
    time_unit = Enum('mus', 's', 'ms', 'ns').tag(pref=True)

    #: Duration in unit of the context of a pulse. It is the responsability
    #: of subclasses to implement a getter.
    sampling_time = Property(cached=True)

    #: List of analogical channels defined by this context.
    analogical_channels = Tuple()

    #: List of logical channels defined by this context
    logical_channels = Tuple()

    #: List of logical channels whose meaning should be inverted.
    inverted_log_channels = List().tag(pref=True)

    #: Whether or not to round times to the nearest multiple of sampling time
    #: when checking.
    rectify_time = Bool(True).tag(pref=True)

    #: When times are not rectified tolerance above which a time is considered
    #: to be too far from a multiple of the sampling time to be used.
    tolerance = Float(0.000000001).tag(pref=True)

    #: Name of the context class. Used for persistence purposes.
    context_id = Unicode().tag(pref=True)

    def compile_sequence(self, pulses, **kwargs):
        """

        """
        mes = cleandoc('''compile_sequence should be implemented by subclass of
                       BaseContext.''')
        raise NotImplementedError(mes)

    def len_sample(self, duration):
        """ Compute the number of points used to describe a lapse of time.

        Parameters
        ----------
        duration : float
            Duration of the interval to describe.


        Returns
        -------
        length : int
            Number of samples the instr will use to represent the interval
            between start and stop

        """
        return int(round(duration / self.sampling_time))

    def check_time(self, time):
        """ Check a given time can be represented by an int given the
        sampling frequency.

        """
        if time is None or time < 0:
            return time

        rectified_time = self.sampling_time*round(time/self.sampling_time)

        if self.rectify_time:
            return rectified_time

        else:
            if abs(time - rectified_time) > self.tolerance:
                raise ValueError('Time does not fit the instr resolution')
            return time

    def _default_context_id(self):
        """ Default value the context class member.

        """
        pack, _ = self.__module__.split('.', 1)
        return pack + '.' + type(self).__name__

    def _answer(self, members, callables):
        """ Collect answers for the walk method.

        """
        answers = {m: getattr(self, m, None) for m in members}
        answers.update({k: c(self) for k, c in callables.items()})
        return answers
