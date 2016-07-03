# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015 by Ecpy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Basic element of a sequence. Pulse is a subclass of Item.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


from atom.api import (Int, Unicode, List, Bool, Float, Enum, ForwardTyped,
                      Value, Constant, Dict)
from ecpy.utils.atom_util import HasPrefAtom

from .utils.entry_eval import eval_entry


def sequence():
    from .sequences.base_sequences import BaseSequence
    return BaseSequence


def root_sequence():
    from .sequences.base_sequences import RootSequence
    return RootSequence


#: Id used to identify dependencies type.
DEP_TYPE = 'ecpy.pulses.items'


class Item(HasPrefAtom):
    """ Base component of a pulse Sequence

    """
    #: Identifier for the build dependency collector
    dep_type = Constant(DEP_TYPE).tag(pref=True)

    #: Index identifying the item inside the sequence.
    index = Int()

    #: Flag to disable a particular item.
    enabled = Bool(True).tag(pref=True)

    #: Class of the item to use when rebuilding a sequence.
    item_id = Unicode().tag(pref=True)

    #: Name of the variable which can be referenced in other items.
    linkable_vars = List()

    #: Reference to the parent sequence.
    parent = ForwardTyped(sequence)

    #: Reference to the root sequence.
    root = ForwardTyped(root_sequence)

    #: Boolean representing whever this item has a root sequence or not
    has_root = Bool(False)

    #: Mode defining how the def_1 and def_2 attrs shiould be interpreted.
    def_mode = Enum('Start/Stop',
                    'Start/Duration',
                    'Duration/Stop').tag(pref=True)

    #: String representing the item first element of definition : according
    #: to the selected mode it evaluated value will either be used for the
    #: start instant, or duration of the item.
    def_1 = Unicode().tag(pref=True)

    #: String representing the item second element of definition : according
    #: to the selected mode it evaluated value will either be used for the
    #: duration, or stop instant of the item.
    def_2 = Unicode().tag(pref=True)

    #: Actual start instant of the item with respect to the beginning of the
    #: root sequence. The unit of this time depends of the setting of the
    #: context.
    start = Float()

    #: Actual duration of the item. The unit of this time depends of the
    #: setting of the context.
    duration = Float()

    #: Actual stop instant of the item with respect to the beginning of the
    #: root sequence. The unit of this time depends of the setting of the
    #: context.
    stop = Float()

    #: Evaluated entries by the eval_entries method
    eval_entries = Dict()

    def eval_entries(self, root_vars, sequence_locals, missings, errors):
        """ Attempt to eval the  def_1 and def_2 parameters of the item.

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
        # Flag indicating good completion.

        #: TODO Should only do this at the right and needed times

        success = True

        # Reference to the sequence context.
        context = self.root.context

        # Name of the parameter which will be evaluated.
        par1 = self.def_mode.split('/')[0].lower()
        par2 = self.def_mode.split('/')[1].lower()
        prefix = '{}_'.format(self.index)

        # Evaluation of the first parameter.
        d1 = None
        try:
            d1 = eval_entry(self.def_1, sequence_locals, missings)
            d1 = context.check_time(d1)
        except Exception as e:
            errors[prefix + par1] = repr(e)

        # Check the value makes sense as a start time or duration.
        if d1 is not None and d1 >= 0 and (par1 == 'start' or d1 != 0):
            setattr(self, par1, d1)
            root_vars[prefix + par1] = d1
            sequence_locals[prefix + par1] = d1
        elif d1 is None:
            success = False
        else:
            success = False
            if par1 == 'start':
                m = 'Got a strictly negative value for start: {}'.format(d1)

            else:
                m = 'Got a negative value for duration: {}'.format(d1)

            errors[prefix + par1] = m

        # Evaluation of the second parameter.
        d2 = None
        try:
            d2 = eval_entry(self.def_2, sequence_locals, missings)
            d2 = context.check_time(d2)
        except Exception as e:
            errors[prefix + par2] = repr(e)

        # Check the value makes sense as a duration or stop time.
        if d2 is not None and d2 > 0 and (par2 == 'duration' or d2 > d1):
            setattr(self, par2, d2)
            root_vars[prefix + par2] = d2
            sequence_locals[prefix + par2] = d2
        elif d2 is None:
            success = False
        else:
            success = False
            if par2 == 'stop' and d2 <= 0.0:
                m = 'Got a negative or null value for stop: {}'.format(d2)
            elif par2 == 'stop':
                m = 'Got a stop smaller than start: {} < {}'.format(d1, d2)
            elif d2 <= 0.0:
                m = 'Got a negative value for duration: {}'.format(d2)

            errors[prefix + par2] = m

        # Computation of the third parameter.
        if success:
            if self.def_mode == 'Start/Duration':
                self.stop = d1 + d2
                root_vars[prefix + 'stop'] = self.stop
                sequence_locals[prefix + 'stop'] = self.stop
            elif self.def_mode == 'Start/Stop':
                self.duration = d2 - d1
                root_vars[prefix + 'duration'] = self.duration
                sequence_locals[prefix + 'duration'] = self.duration
            else:
                self.start = d2 - d1
                root_vars[prefix + 'start'] = self.start
                sequence_locals[prefix + 'start'] = self.start

        return success

    # --- Private API ---------------------------------------------------------

    def _default_item_id(self):
        """ Default value for the item_id member.

        """
        pack, _ = self.__module__.split('.', 1)
        return pack + '.' + type(self).__name__

    def _post_setattr_root(self, old, new):
        """Make sure that all children get all the info they need to behave
        correctly when the item get its root parent.

        """
        if new is None:
            self.has_root = False
            return

        self.has_root = True
