# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Base classes for sequence configurers.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from inspect import getdoc
from atom.api import (Atom, Unicode, Bool, Subclass, ForwardTyped, Typed, Dict)

from ..item import Item


# Circular import protection
def pulses_manager():
    from ..plugin import PulsesManagerPlugin
    return PulsesManagerPlugin


class AbstractConfig(Atom):
    """Root class for all config objects.

    """
    #: Ecpy_pulses manager, necessary to retrieve item(pulse/sequence)
    #: implementations.
    manager = ForwardTyped(pulses_manager)

    #: Class of the item to create.
    sequence_class = Subclass(Item)

    #: Root of the sequence in which an item will be added.
    root = Typed(Item)

    #: Bool indicating if the build can be done.
    ready = Bool(False)

    def check_parameters(self, change):
        """Check if enough parameters have been provided to build the item.

        This method should set the ready flag every time it is called, setting
        it to True if everything is allright, False otherwise.

        """
        raise NotImplementedError()

    def build_sequence(self):
        """This method use the user parameters to build the item object.

        Returns
        -------
        item : Item | None
            Item object built using the user parameters. Ready to be
            inserted in a sequence. None if errors occured.

        """
        raise NotImplementedError()


class SequenceConfig(AbstractConfig):
    """Standard config object for sequences.

    """
    #: Name of the sequence used to make the sequence easier to read.
    sequence_name = Unicode()

    #: Docstring of the sequence.
    sequence_doc = Unicode()

    def __init__(self, **kwargs):
        super(SequenceConfig, self).__init__(**kwargs)
        self.sequence_doc = getdoc(self.sequence_class).replace('\n', ' ')

    def build_sequence(self):
        """Build the selected sequence.

        """
        return self.sequence_class(name=self.sequence_name)

    def _post_setattr_sequence_name(self, old, new):
        """ Observer notifying that the configurer is ready to build.

        """
        self.ready = bool(new)
