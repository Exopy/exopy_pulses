# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Base class for all analogical pulses shapes.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from atom.api import Unicode, Constant, Int

from ..utils.entry_eval import HasEvaluableFields

#: Id used to identify dependencies type.
DEP_TYPE = 'ecpy.pulses.shapes'


class AbstractShape(HasEvaluableFields):
    """Base class for all shapes.

    """
    #: Identifier for the build dependency collector
    dep_type = Constant(DEP_TYPE).tag(pref=True)

    #: Id of the shape used to query it from the plugin.
    shape_id = Unicode().tag(pref=True)

    #: Index of the parent pulse. This is set whe evaluating the entries.
    index = Int()

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

    def format_error_id(self, member):
        """Assemble the id used to report an evaluation error.

        """
        return '{}_shape_{}'.format(self.index, member)

    def format_global_vars_id(self, member):
        """Shapes are not allowed to store in the global namespace so raise.

        """
        msg = 'Shapes cannot store values as global (from pulse {})'
        raise RuntimeError(msg.format(self.index))

    # =========================================================================
    # --- Private API ---------------------------------------------------------
    # =========================================================================

    def _default_shape_id(self):
        """Compute the shape id.

        """
        pack, _ = self.__module__.split('.', 1)
        return pack + '.' + type(self).__name__
