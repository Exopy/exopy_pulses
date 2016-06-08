# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
""" Module defining the basic filters.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from atom.api import Value, Subclass, Unicode, Property, set_default
from enaml.core.api import d_func, d_

from ecpy.utils.declarator import Declarator

from ..item import Item


class ItemFilter(Declarator):
    """ Base class for all item filters.

    Filters should simply override the filter_items classmethod.

    """

    id = d_(Unicode())

    @d_func
    def filter_items(self, py_sequences, template_sequences):
        """ Class method used to filter tasks.

        Parameters
        ----------
            py_items : dict
                Dictionary of known python items as name : class

            template_sequences : dict
                Dictionary of known templates as name : path

        Returns
        -------
            task_names : list(str)
                List of the name of the task matching the filters criteria.

        """
        items = list(py_sequences.keys()) + list(template_sequences.keys())
        return items


class SequenceFilter(ItemFilter):
    """ Filter returning sequences selected in the method list_sequences.

    """

    @d_func
    def filter_items(self, py_sequences, template_sequences):

        return list(py_sequences.keys())


class TemplateFilter(ItemFilter):
    """ Filter keeping only the templates.

    """

    @d_func
    def filter_items(self, py_sequences, template_sequences):

        return list(template_sequences.keys())


class SubclassItemFilter(ItemFilter):
    """ Filter keeping only the python items which are subclass of task_class.

    """

    # Class attribute to which task will be compared.
    subclass = d_(Subclass(Item))

    @d_func
    def filter_items(self, py_sequences, template_sequences):
        """
        """
        sequences = []
        for name, t_class in py_sequences.items():
            if issubclass(t_class, self.subclass):
                sequences.append(name)

        try:
            sequences.remove('Pulse')
            sequences.remove('RootSequence')
        except ValueError:
            pass

        return sequences


class MetadataItemFilter(ItemFilter):
    """ Filter keeping only the items with the right class attribute.

    """
    #: Attribute name that the filter should have to be selected
    meta_key = d_(Unicode())

    #: Value that the attribute should have to be selected
    meta_value = d_(Value())

    @d_func
    def filter_items(self, py_sequences, template_sequences):
        """

        """
        sequences = []
        attr_name = self.meta_key
        attr_val = self.meta_value
        for name, t_class in py_sequences.items():
            if (hasattr(t_class, attr_name) and
                    getattr(t_class, attr_name) == attr_val):
                sequences.append(name)

        try:
            sequences.remove('Pulse')
            sequences.remove('RootSequence')
        except ValueError:
            pass

        return sequences


class GroupItemFilter(MetadataItemFilter):
    """Filter keeping only the items from the right groupm which is a
    metadata property of those items.

    """
    #: Group to which the task must belong.
    grup = d_(Unicode())

    meta_key = set_default('group')

    meta_value = Property()

    def _get_meta_value(self):
        return self.group
