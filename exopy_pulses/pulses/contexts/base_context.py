# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Definition of the interface for base pulse sequence context.

"""
from atom.api import (Enum, Str, Bool, Float, Property, Tuple, List,
                      Constant)

from ..utils.entry_eval import HasEvaluableFields

DEP_TYPE = 'exopy.pulses.context'

# Time conversion dictionary first key is the original unit, second the final
# one.
TIME_CONVERSION = {'s': {'s': 1, 'ms': 1e3, 'mus': 1e6, 'ns': 1e9},
                   'ms': {'s': 1e-3, 'ms': 1, 'mus': 1e3, 'ns': 1e6},
                   'mus': {'s': 1e-6, 'ms': 1e-3, 'mus': 1, 'ns': 1e3},
                   'ns': {'s': 1e-9, 'ms': 1e-6, 'mus': 1e-3, 'ns': 1}}


class BaseContext(HasEvaluableFields):
    """Base class describing a Context

    Dependind on the targetted waveform generator the context should offer the
    possibility to name the sequence, select it after transfer, clean channels
    for which no sequence was uploaded and immediately start running the
    transferred sequence.

    """
    #: Identifier for the build dependency collector
    dep_type = Constant(DEP_TYPE).tag(pref=True)

    #: Tuple of sequence types that should not be simplified.
    supported_sequences = Tuple()

    #: Time unit.
    time_unit = Enum('mus', 's', 'ms', 'ns').tag(pref=True)

    #: Duration in unit of the context of a time step. It is the responsability
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
    context_id = Str().tag(pref=True)

    def compile_and_transfer_sequence(self, sequence, driver=None):
        """Compile the pulse sequence and send it to the instruments.

        When this method is called the sequence has not yet been evaluated nor
        simplified. If the context does not need any special controls on those
        it can call the preprocess_sequence method to carry out those two
        operations.

        Parameters
        ----------
        sequence : RootSequence
            Sequence to compile and transfer.

        driver : object, optional
            Instrument driver to use to transfer the sequence once compiled.
            If absent the context should do its best to assert that the
            compilation can succeed.

        Returns
        -------
        result : bool
            Whether the compilation succeeded.

        infos : dict
            Infos about the transferred and compiled sequence. The keys
            should match the ones listed in sequence_infos_keys.

        errors : dict
            Errors that occured during compilation.

        """
        raise NotImplementedError()

    def list_sequence_infos(self):
        """List the sequence infos returned after a successful completion.

        Returns
        -------
        infos : dict
            Dict mimicking the one returned on successful completion of
            a compilation and transfer. The values types should match the
            the ones found in the real infos.

        """
        raise NotImplementedError()

    def preprocess_sequence(self, sequence):
        """Evaluate and simplify a sequence in the standard way.

        Parameters
        ----------
        sequence : RootSequence
            Sequence to preprocess.

        Returns
        -------
        items : list
            List of simple items ready to be compiled.

        errors : dict
            Errors that occured during evaluation and simplification.

        """
        res, missings, errors = sequence.evaluate_sequence()
        if not res:
            msg = 'The following variables were never computed : %s'
            errors['Unknown variables'] = msg % missings
            return [], errors

        items = sequence.simplify_sequence()
        return items, errors

    def len_sample(self, duration):
        """Compute the number of points used to describe a lapse of time.

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
                raise ValueError('Time does not fit the instrument resolution')
            return time

    def format_error_id(self, member):
        """Format the error id for the given member.

        """
        return 'context_{}'.format(member)

    def format_global_vars_id(self, member):
        """Shapes are not allowed to store in the global namespace so raise.

        """
        msg = 'Context cannot store values as global.'
        raise RuntimeError(msg)

    # =========================================================================
    # --- Private API ---------------------------------------------------------
    # =========================================================================

    def _default_context_id(self):
        """ Default value the context class member.

        """
        pack, _ = self.__module__.split('.', 1)
        return pack + '.' + type(self).__name__
