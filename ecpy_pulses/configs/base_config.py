# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Root Config objects to be used by ecpy_pulses.

Holds the AbstractConfig, which is the base class for all config objects in
ecpy_pulses, and SequenceConfig, which is the base config object for all 
sequences.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from inspect import getdoc, cleandoc
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

    #: Dict of errors which happened during construction.
    errors = Dict()

    def check_parameters(self, change):
        """Check if enough parameters have been provided to build the item.

        This method should set the ready flag every time it is called, setting
        it to True if everything is allright, False otherwise.

        """
        err_str = '''This method should be implemented by subclasses of
        AbstractConfig. This method is called each time a member is changed
        to check if enough parameters has been provided to build the item.'''
        raise NotImplementedError(cleandoc(err_str))

    def build_sequence(self):
        """This method use the user parameters to build the item object

        Returns
        -------
        item : Item
            Item object built using the user parameters. Ready to be
            inserted in a sequence.

        """
        err_str = '''This method should be implemented by subclasses of
        AbstractConfig. This method is called when the user validate its
        choices and that the item must be built.'''
        raise NotImplementedError(cleandoc(err_str))


class SequenceConfig(AbstractConfig):
    """Root class for all Sequence Config Objects.

    """

    #: Name of the sequence used to make the sequence easier to read.
    sequence_name = Unicode()

    #: Docstring of the sequence.
    sequence_doc = Unicode()

    def __init__(self, **kwargs):
        super(SequenceConfig, self).__init__(**kwargs)
        self.sequence_doc = getdoc(self.sequence_class).replace('\n', ' ')

    def build_sequence(self):
        return self.sequence_class(name=self.sequence_name)

    def _post_setattr_sequence_name(self, old, new):
        """ Observer notifying that the configurer is ready to build.

        """
        self.ready = bool(new)
