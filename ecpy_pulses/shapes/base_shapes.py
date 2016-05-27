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


from atom.api import (Unicode)

from ecpy.utils.atom_util import HasPrefAtom


class AbstractShape(HasPrefAtom):
    """
    """

    shape_class = Unicode().tag(pref=True)

    def eval_entries(self, sequence_locals, missing, errors, index):
        """ Evaluate the entries defining the shape.

        Parameters
        ----------
        sequence_locals : dict
            Known locals variables for the pulse sequence.

        missing : set
            Set of variables missing to evaluate some entries in the sequence.

        errors : dict
            Errors which occurred when trying to compile the pulse sequence.

        index : int
            Index of the pulse to which this shape object belongs.

        Returns
        -------
        result : bool
            Flag indicating whether or not the evaluation succeeded.

        """
        return True

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
            Amplitudes of the pulse at the given time.

        """
        raise NotImplementedError('')

    def _default_shape_class(self):
        return type(self).__name__

    def _answer(self, members, callables):
        """ Collect answers for the walk method.

        """
        answers = {m: getattr(self, m, None) for m in members}
        answers.update({k: c(self) for k, c in callables.items()})
        return answers
