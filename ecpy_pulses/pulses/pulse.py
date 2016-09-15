# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Definition of a pulse, the elementary building block of sequences.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import numpy as np
from atom.api import (Unicode, Enum, Typed, Property, set_default)
from ecpy.utils.atom_util import (update_members_from_preferences)

from .shapes.base_shape import AbstractShape
from .shapes.modulation import Modulation
from .item import Item


class Pulse(Item):
    """ Represent a pulse to perfom during a sequence.

    """
    #: The kind of pulse can be either logical or ananlogical.
    kind = Enum('Logical', 'Analogical').tag(pref=True)

    #: Channel of the executioner which should perfom the pulse.
    channel = Unicode().tag(pref=True)

    #: Waveform
    waveform = Property()

    #: Modulation to apply to the pulse. Only enabled in analogical mode.
    modulation = Typed(Modulation, ()).tag(pref=True)

    #: Shape of the pulse. Only enabled in analogical mode.
    shape = Typed(AbstractShape).tag(pref=True)

    linkable_vars = set_default(['start', 'stop', 'duration'])

    def eval_entries(self, root_vars, sequence_locals, missings, errors):
        """ Attempt to eval the string parameters of the pulse.

        Parameters
        ----------
        root_vars : dict
            Dictionary of global variables for the all items. This will
            tipically contains the i_start/stop/duration and the root vars.

        sequence_locals : dict
            Dictionary of variables whose scope is limited to this item
            parent.

        missings : set
            Set of unfound local variables.

        errors : dict
            Dict of the errors which happened when performing the evaluation.

        Returns
        -------
        flag : bool
            Boolean indicating whether or not the evaluation succeeded.

        """
        success = super(Pulse, self).eval_entries(root_vars, sequence_locals,
                                                  missings, errors)

        if self.kind == 'Analogical':
            # Shapes are not allowed to modify global vars hence the empty
            # dict
            self
            success &= self.modulation.eval_entries({}, sequence_locals,
                                                    missings, errors)

            success &= self.shape.eval_entries({}, sequence_locals,
                                               missings, errors)

        return success

    @classmethod
    def build_from_config(cls, config, dependencies):
        """ Create a new instance using the provided infos for initialisation.

        Parameters
        ----------
        config : dict(str)
            Dictionary holding the new values to give to the members in string
            format, or dictionnary like for instance with prefs.

        dependencies : dict
            Dictionary holding the necessary classes needed when rebuilding.

        Returns
        -------
        pulse : pulse
            Newly created and initiliazed sequence.

        Notes
        -----
        This method is fairly powerful and can handle a lot of cases so
        don't override it without checking that it works.

        """
        pulse = cls()

        #: Initialize the shape object with the right class, so that after
        #: update_members_from_preferences can do all the rest (initialize
        #: the shape's members)
        if 'shape' in config:
            shape_config = config['shape']
            if not shape_config == 'None':
                s_id = shape_config.pop('shape_id')
                s_cls = dependencies['ecpy.pulses.shapes'][s_id]
                shape = s_cls()
                pulse.shape = shape

        update_members_from_preferences(pulse, config)

        return pulse

    def traverse(self, depth=-1):
        """Yield a task and all of its components.

        The base implementation simply yields the task itself.

        Parameters
        ----------
        depth : int
            How deep should we explore the tree of tasks. When this number
            reaches zero deeper children should not be explored but simply
            yielded.

        """
        for i in super(Pulse, self).traverse(depth=depth):
            yield i

        if self.kind == 'Analogical':

            yield self.modulation

            if self.shape:
                yield self.shape

    def clean_cached_values(self):
        """Also clean modualtion and shape if necessary.

        """
        super(Pulse, self).clean_cached_values()
        if self.kind == 'Analogical':
            self.modulation.clean_cached_values()
            self.shape.clean_cached_values()

    # =========================================================================
    # --- Private API ---------------------------------------------------------
    # =========================================================================

    def _get_waveform(self):
        """ Getter for the waveform property.

        """
        context = self.root.context
        n_points = context.len_sample(self.duration)
        if self.kind == 'Analogical':
            time = np.linspace(self.start, self.stop, n_points, False)
            mod = self.modulation.compute(time, context.time_unit)
            shape = self.shape.compute(time, context.time_unit)
            return mod * shape
        else:
            return np.ones(n_points, dtype=np.int8)
