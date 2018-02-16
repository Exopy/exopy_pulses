# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
""" Module defining the basic filters.

"""
from atom.api import Value, Subclass, Unicode, Property, set_default
from enaml.core.api import d_func, d_

from exopy.utils.declarator import Declarator

from .item import Item


class SequenceFilter(Declarator):
    """ Base class for all item filters.

    Filters should simply override the filter_sequences declarative function.

    """

    id = d_(Unicode())

    @d_func
    def filter_sequences(self, py_sequences, template_sequences):
        """Declarative function filtering the items.

        Parameters
        ----------
        py_items : dict
            Dictionary of known python items as id : infos

        template_sequences : dict
            Dictionary of known templates as id : path

        Returns
        -------
        items_names : list(str)
            List of the name of the items matching the filters criteria.

        """
        items = list(py_sequences) + list(template_sequences)
        return items


class PySequenceFilter(SequenceFilter):
    """Filter returning only Python implemented sequences.

    """

    @d_func
    def filter_sequences(self, py_sequences, template_sequences):

        return list(py_sequences.keys())


class TemplateFilter(SequenceFilter):
    """Filter keeping only the templates.

    """

    @d_func
    def filter_sequences(self, py_sequences, template_sequences):

        return list(template_sequences.keys())


class SubclassSequenceFilter(SequenceFilter):
    """Filter keeping only the python items which are subclass of subclass.

    """

    #: Ancestor class of the item to keep.
    subclass = d_(Subclass(Item))

    @d_func
    def filter_sequences(self, py_sequences, template_sequences):
        """Filter based on the specified item subclass.

        """
        sequences = []
        for name, infos in py_sequences.items():
            if issubclass(infos.cls, self.subclass):
                sequences.append(name)

        return sequences


class MetadataSequenceFilter(SequenceFilter):
    """ Filter keeping only the items with the right class attribute.

    """
    #: Metadata key on which the filtering is performed.
    meta_key = d_(Unicode())

    #: Metadata value on which the filtering is performed.
    meta_value = d_(Value())

    @d_func
    def filter_sequences(self, py_sequences, template_sequences):
        """Filter keeping only the items whose metadata fit the provided
        key/value pair.

        """
        sequences = []
        for name, s_infos in py_sequences.items():
            if (self.meta_key in s_infos.metadata and
                    s_infos.metadata[self.meta_key] == self.meta_value):
                sequences.append(name)

        return sequences


class GroupSequenceFilter(MetadataSequenceFilter):
    """Filter keeping only the items from the right group which is a
    metadata property of those items.

    """
    #: Group to which the task must belong.
    group = d_(Unicode())

    meta_key = set_default('group')

    meta_value = Property()

    def _get_meta_value(self):
        return self.group
