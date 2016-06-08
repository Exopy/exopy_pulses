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

from itertools import chain
from inspect import cleandoc
from copy import deepcopy

from atom.api import (Int, Instance, Unicode, Dict, Bool, List,
                      Signal, set_default, Typed)
from ecpy.utils.container_change import ContainerChange
from ecpy.utils.atom_util import (tagged_members, member_to_pref,
                                  member_from_pref,
                                  update_members_from_preferences)

from ..contexts.base_context import BaseContext
from ..utils.entry_eval import eval_entry
from ..item import Item
from ..pulse import Pulse


class AbstractSequence(Item):
    """ Base class for all sequences.

    This class defines the basic of a sequence but with only a very limited
    child support : only construction is supported, indexing is not handled
    nor is child insertion, deletion or displacement (This is because
    TemplateSequence inherits from AbstractSequence, while everything else
    inherits from Sequence which supports insertion/deletion/displacement).

    """

    #: Name of the sequence (help make a sequence more readable)
    name = Unicode().tag(pref=True)

    #: List of items this sequence consists of.
    items = List(Instance(Item)).tag(child=100)

    #: Signal emitted when the list of items in this sequence changes. The
    #: payload will be a ContainerChange instance.
    items_changed = Signal().tag(child_notifier='items')

    #: Dict of variables whose scope is limited to the sequence. Each key/value
    #: pair represents the name and definition of the variable.
    local_vars = Dict(Unicode()).tag(pref=True)

    #: Evaluated entries by the eval_entries method
    evaluated_entries_cache = Dict(Unicode())

    #: Cache is valid?
    cache_valid = Bool(False)

    def cleanup_cache(self):
        """ Clear all internal caches after successfully compiling the sequence

        """
        self._evaluated_vars = {}
        self._compiled = []
        for i in self.items:
            if isinstance(i, AbstractSequence):
                i.cleanup_cache()

    def compile_sequence(self, root_vars, sequence_locals, missings, errors):
        """ Evaluate the sequence vars and compile the list of pulses.

        Parameters
        ----------
        root_vars : dict
            Dictionary of global variables for the all items. This will
            tipically contains the i_start/stop/duration and the root vars.
            This dict must be updated with global new values but for
            evaluation sequence_locals must be used.

        sequence_locals : dict
            Dictionary of variables whose scope is limited to this sequence
            parent. This dict must be updated with global new values and
            must be used to perform evaluation (It always contains all the
            names defined in root_vars).

        missings : set
            Set of unfound local variables.

        errors : dict
            Dict of the errors which happened when performing the evaluation.

        Returns
        -------
        flag : bool
            Boolean indicating whether or not the evaluation succeeded.

        pulses : list
            List of pulses in which all the string entries have been evaluated.

        """
        raise NotImplementedError()

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
        sequence : AbstractSequence
            Newly created and initiliazed sequence.

        Notes
        -----
        This method is fairly powerful and can handle a lot of cases so
        don't override it without checking that it works.

        """
        sequence = cls()
        update_members_from_preferences(sequence, config)

        i = 0
        pref = 'item_{}'
        validated = []
        while True:
            item_name = pref.format(i)
            if item_name not in config:
                break
            item_config = config[item_name]
            i_id = item_config.pop('item_id')
            i_cls = dependencies['ecpy.pulses.items'][i_id]
            item = i_cls.build_from_config(item_config,
                                           dependencies)
            validated.append(item)
            i += 1

        setattr(sequence, 'items', validated)

        return sequence

    # --- Private API ---------------------------------------------------------

    #: Dict of all already evaluated vars.
    _evaluated_vars = Dict()

    #: List of already compiled items.
    _compiled = List()

    def _compile_items(self, root_vars, sequence_locals, missings, errors):
        """ Compile the sequence in a flat list of pulses.

        Parameters
        ----------
        root_vars : dict
            Dictionary of global variables for the all items. This will
            tipically contains the i_start/stop/duration and the root vars.

        sequence_locals : dict
            Dictionary of variables whose scope is limited to this sequence.

        missings : set
            Set of unfound local variables.

        errors : dict
            Dict of the errors which happened when performing the evaluation.

        Returns
        -------
        flag : bool
            Boolean indicating whether or not the evaluation succeeded.

        pulses : list
            List of pulses in which all the string entries have been evaluated.

        """

        # Inplace modification of compile will update self._compiled.
        if not self._compiled:
            self._compiled = [None for i in self.items if i.enabled]
        compiled = self._compiled

        # Compilation of items in multiple passes.
        while True:
            miss = set()

            index = -1
            for item in self.items:
                # Skip disabled items
                if not item.enabled:
                    continue

                # Increment index so that we set the right object in compiled.
                index += 1

                # Skip evaluation if object has already been compiled.
                if compiled[index] is not None:
                    continue

                # If we get a pulse simply evaluate the entries, to add their
                # values to the locals and keep track of the missings to now
                # when to abort compilation.
                if isinstance(item, Pulse):
                    success = item.eval_entries(root_vars, sequence_locals,
                                                miss, errors)
                    if success:
                        compiled[index] = [item]

                # Here we got a sequence so we must try to compile it.
                else:
                    success, items = item.compile_sequence(root_vars,
                                                           sequence_locals,
                                                           miss, errors)
                    if success:
                        compiled[index] = items

            known_locals = set(sequence_locals.keys())
            # If none of the variables found missing during last pass is now
            # known stop compilation as we now reached a dead end. Same if an
            # error occured.
            if errors or miss and (not known_locals & miss):
                # Update the missings given by caller so that it knows it this
                # failure is linked to circle references.
                missings.update(miss)
                return False, []

            # If no var was found missing during last pass (and as no error
            # occured) it means the compilation succeeded.
            elif not miss:
                pulses = list(chain.from_iterable(compiled))
                # Clean the compiled items once the pulse is transfered
                self.cleanup_cache()
                return True, pulses


class BaseSequence(AbstractSequence):
    """ A sequence is an ensemble of pulses.

    """

    #: Bool indicating whether or not the sequence has a hard defined
    #: start/stop/duration. In case it does not the associated values won't
    #: be computed.
    time_constrained = Bool().tag(pref=True)


    def evaluate_sequence(self, root_vars, sequence_locals, missings, errors):
        """ Evaluate the sequence vars and compile the list of pulses.

        Parameters
        ----------
        root_vars : dict
            Dictionary of global variables for the all items. This will
            tipically contains the i_start/stop/duration and the root vars.
            This dict must be updated with global new values but for
            evaluation sequence_locals must be used.

        sequence_locals : dict
            Dictionary of variables whose scope is limited to this sequence
            parent. This dict must be updated with global new values and
            must be used to perform evaluation (It always contains all the
            names defined in root_vars).

        missings : set
            Set of unfound local variables.

        errors : dict
            Dict of the errors which happened when performing the evaluation.

        Returns
        -------
        flag : bool
            Boolean indicating whether or not the evaluation succeeded.

        pulses : list
            List of pulses in which all the string entries have been evaluated.

        """
        prefix = '{}_'.format(self.index)

        # Definition evaluation.
        if self.time_constrained:
            self.eval_entries(root_vars, sequence_locals, missings, errors)

        # Local vars computation.
        for name, formula in self.local_vars.items():
            if name not in self._evaluated_vars:
                try:
                    val = eval_entry(formula, sequence_locals, missings)
                    self._evaluated_vars[name] = val
                except Exception as e:
                    errors[prefix + name] = repr(e)

        local_namespace = sequence_locals.copy()
        local_namespace.update(self._evaluated_vars)

        res, pulses = self._compile_items(root_vars, local_namespace,
                                          missings, errors)

        if res:
            if self.time_constrained:
                # Check if start, stop and duration of sequence are compatible.
                start_err = [pulse for pulse in pulses
                             if pulse.start < self.start]
                stop_err = [pulse for pulse in pulses
                            if pulse.stop > self.stop]

                if start_err:
                    mess = cleandoc('''The start time of the following items {}
                        is before the start time of the sequence {}''')
                    mess = mess.replace('\n', ' ')
                    ind = [p.index for p in start_err]
                    errors[self.name + '-start'] = mess.format(ind, self.index)
                if stop_err:
                    mess = cleandoc('''The stop time of the following items {}
                        is after the stop time of the sequence {}''')
                    mess = mess.replace('\n', ' ')
                    ind = [p.index for p in stop_err]
                    errors[self.name + '-stop'] = mess.format(ind, self.index)

                if errors:
                    return False, []

            return True, pulses

        else:
            return False, []

    def compile_sequence(self, root_vars, sequence_locals, missings, errors):
        """ Evaluate the sequence vars and compile the list of pulses.

        Parameters
        ----------
        root_vars : dict
            Dictionary of global variables for the all items. This will
            tipically contains the i_start/stop/duration and the root vars.
            This dict must be updated with global new values but for
            evaluation sequence_locals must be used.

        sequence_locals : dict
            Dictionary of variables whose scope is limited to this sequence
            parent. This dict must be updated with global new values and
            must be used to perform evaluation (It always contains all the
            names defined in root_vars).

        missings : set
            Set of unfound local variables.

        errors : dict
            Dict of the errors which happened when performing the evaluation.

        Returns
        -------
        flag : bool
            Boolean indicating whether or not the evaluation succeeded.

        pulses : list
            List of pulses in which all the string entries have been evaluated.

        """
        prefix = '{}_'.format(self.index)

        # Definition evaluation.
        if self.time_constrained:
            self.eval_entries(root_vars, sequence_locals, missings, errors)

        # Local vars computation.
        for name, formula in self.local_vars.items():
            if name not in self._evaluated_vars:
                try:
                    val = eval_entry(formula, sequence_locals, missings)
                    self._evaluated_vars[name] = val
                except Exception as e:
                    errors[prefix + name] = repr(e)

        local_namespace = sequence_locals.copy()
        local_namespace.update(self._evaluated_vars)

        res, pulses = self._compile_items(root_vars, local_namespace,
                                          missings, errors)

        if res:
            if self.time_constrained:
                # Check if start, stop and duration of sequence are compatible.
                start_err = [pulse for pulse in pulses
                             if pulse.start < self.start]
                stop_err = [pulse for pulse in pulses
                            if pulse.stop > self.stop]

                if start_err:
                    mess = cleandoc('''The start time of the following items {}
                        is before the start time of the sequence {}''')
                    mess = mess.replace('\n', ' ')
                    ind = [p.index for p in start_err]
                    errors[self.name + '-start'] = mess.format(ind, self.index)
                if stop_err:
                    mess = cleandoc('''The stop time of the following items {}
                        is after the stop time of the sequence {}''')
                    mess = mess.replace('\n', ' ')
                    ind = [p.index for p in stop_err]
                    errors[self.name + '-stop'] = mess.format(ind, self.index)

                if errors:
                    return False, []

            return True, pulses

        else:
            return False, []

    def get_bindable_vars(self):
        """ Access the list of bindable vars for the sequence.

        """
        return self.local_vars.keys() + self.parent.get_bindable_vars()

    def preferences_from_members(self):
        """ Get the members values as string to store them in .ini files.

        Reimplemented here to save items.

        """
        pref = super(BaseSequence, self).preferences_from_members()

        for i, item in enumerate(self.items):
            pref['item_{}'.format(i)] = item.preferences_from_members()

        return pref

    def update_members_from_preferences(self, **parameters):
        """ Use the string values given in the parameters to update the members

        This function will call itself on any tagged HasPrefAtom member.
        Reimplemented here to update items.

        """
        super(BaseSequence, self).update_members_from_preferences(**parameters)

        for i, item in enumerate(self.items):
            para = parameters['item_{}'.format(i)]
            item.update_members_from_preferences(**para)

    def add_child_item(self, index, child):
        """Add a child item at the given index.

        Parameters
        ----------
        index : int
            Index at which to insert the new child item.

        child : Item
            Item to insert in the list of items.

        """
        self.items.insert(index, child)
        child.parent = self

        child.observe('linkable_vars', self.root._update_linkable_vars)
        if isinstance(child, BaseSequence):
            child.observe('_last_index', self._item_last_index_updated)

        self._last_index += 1
        child.index = self._last_index

        # In the absence of a root item do nothing else than inserting the
        # child.
        if self.has_root:
            # Give him its root so that it can proceed to any child
            # registration it needs to.
            child.root = self.root

            #: If we update linkable vars on this item then we need to inform
            #: the root of this.
            child.observe('linkable_vars', self.root._update_linkable_vars)
            if isinstance(child, BaseSequence):
                child.observe('_last_index', self._item_last_index_updated)

        self._recompute_indexes()

        #: Wrap it up and notify the rest of the world, if it is listening.
        notification = ContainerChange(obj=self, name='items',
                                       added=[(index, child)])
        self.items_changed(notification)

    def move_child_item(self, old, new):
        """Move a child item.

        Parameters
        ----------
        old : int
            Index at which the child to move is currently located.

        new : Item
            Index at which to insert the child item.

        """
        child = self.items.pop(old)
        self.items.insert(new, child)

        self._recompute_indexes()

        notification = ContainerChange(obj=self, name='items',
                                       moved=[(old, new, child)])
        self.items_changed(notification)

    def remove_child_item(self, index):
        """Remove a child item from the items list.

        Parameters
        ----------
        index : int
            Index at which the child to remove is located.

        """
        child = self.items.pop(index)

        child.unobserve('linkable_vars', self.root._update_linkable_vars)
        with child.suppress_notifications():
            del child.root
            del child.parent

            child.root = None
            child.parent = None
            child.index = 0
        if isinstance(child, BaseSequence):
            child.unobserve('_last_index', self._item_last_index_updated)

        self._recompute_indexes()

        notification = ContainerChange(obj=self, name='items',
                                       removed=[(index, child)])
        self.items_changed(notification)

    # --- Private API ---------------------------------------------------------

    #: Last index used by the sequence.
    _last_index = Int()

    def _post_setattr_root(self, old, new):
        """If the root is modified, pass it to all sub-items.

        This allow to build a sequence without a root and parent it later.

        """
        #: Call the item post_setattr (will set has_root to true).
        super(BaseSequence, self)._post_setattr_root(old, new)

        if new:
            for item in self.items:
                item.root = self.root
                if isinstance(item, Item):
                    item.parent = self
                if isinstance(item, BaseSequence):
                    item.observe('_last_index', self._item_last_index_updated)
            # Connect only now to avoid cleaning up in an unwanted way the
            # root linkable vars attr.

        else:
            print("The code is wrong")
            for item in self.items:
                item.root = None
                if isinstance(item, BaseSequence):
                    item.unobserve('_last_index',
                                   self._item_last_index_updated)

    def _post_setattr_time_constrained(self, change):
        """

        """
        if change['value']:
            self.linkable_vars = ['start', 'stop', 'duration']
        else:
            self.linkable_vars = []

    def _recompute_indexes(self, first_index=0, free_index=None):
        """ Recompute the item indexes and update the vars of the root_seq.

        Parameters
        ----------
        first_index : int, optional
            Index in items of the first item whose index needs to be updated.

        free_index : int, optional
            Value of the first free index.

        """
        print("Recompute indexes: ", self, first_index, free_index)
        if free_index is None:
            free_index = self.index + 1

        # Cleanup the linkable_vars for all the pulses which will be reindexed.
        linked_vars = self.root.linkable_vars
        for var in linked_vars[:]:
            if var[0].isdigit() and int(var[0]) >= free_index:
                linked_vars.remove(var)

        for item in self.items[first_index:]:

            print("free index for item:", item, item.index)
            item.index = free_index
            prefix = '{}_'.format(free_index)
            linkable_vars = [prefix + var for var in item.linkable_vars]
            linked_vars.extend(linkable_vars)

            if isinstance(item, BaseSequence):
                item.unobserve('_last_index', self._item_last_index_updated)
                item._recompute_indexes()
                item.observe('_last_index', self._item_last_index_updated)
                free_index = item._last_index + 1

            # We have a non indexed item (pulse or template).
            else:
                free_index += 1

        self._last_index = free_index - 1

    def _item_last_index_updated(self, change):
        """ Update the items indexes whenever the last index of a child
        sequence is updated.

        """
        print("_item_last_index_updated: ", self, change)
        index = self.items.index(change['object']) + 1
        free_index = change['value'] + 1
        self._recompute_indexes(index, free_index)


class RootSequence(BaseSequence):
    """ Base of any pulse sequences.

    This Item perform the first step of compilation by evaluating all the
    entries and then unravelling the pulse sequence (elimination of condition
    and loop flattening).

    Notes
    -----

    The linkable_vars of the RootSequence stores all the known linkable vars
    for the sequence.
    The start, stop, duration and def_1, def_2 members are not used by the
    RootSequence. The time_constrained member only affects the use of the
    sequence duration.

    """
    # --- Public API ----------------------------------------------------------

    #: Dictionary of external variables whose values should be given before
    #: the start of the compilation stage.
    external_vars = Dict(Unicode()).tag(pref=True)

    #: Duration of the sequence when it is fixed. The unit of this time is
    # fixed by the context.
    sequence_duration = Unicode().tag(pref=True)

    #: Reference to the executioner context of the sequence.
    context = Typed(BaseContext).tag(pref=True)

    index = set_default(0)
    name = set_default('Root')
    #root = set_default(self)
    #has_root = set_default(True)

    def __init__(self, **kwargs):
        """

        """
        super(RootSequence, self).__init__(**kwargs)
        self.root = self

    def compile_sequence(self, use_context=True):
        """ Compile a sequence to useful format.

        Parameters
        ---------------
        use_context : bool, optional
            Should the context compile the pulse sequence.

        Returns
        -----------
        result : bool
            Flag indicating whether or not the compilation succeeded.

        args : iterable
            Objects depending on the result and use_context flag.
            In case of failure: tuple
                - a set of the entries whose values where never found and a
                dict of the errors which occured during compilation.
            In case of success:
                - a flat list of Pulse if use_context is False
                - a context dependent result otherwise.

        """
        missings = set()
        errors = {}
        root_vars = self.external_vars.copy()

        # Local vars computation.
        for name, formula in self.local_vars.items():
            if name not in self._evaluated_vars:
                try:
                    val = eval_entry(formula, root_vars, missings)
                    self._evaluated_vars[name] = val
                except Exception as e:
                    errors['root_' + name] = repr(e)

        root_vars.update(self._evaluated_vars)

        if self.time_constrained:
            try:
                duration = eval_entry(self.sequence_duration, root_vars,
                                      missings)
                root_vars['sequence_end'] = duration
            except Exception as e:
                errors['root_seq_duration'] = repr(e)

        res, pulses = self._compile_items(root_vars, root_vars,
                                          missings, errors)

        if not res:
            return False, (missings, errors)

        if self.time_constrained:
            err = [p for p in pulses if p.stop > duration]

            if err:
                mess = cleandoc('''The stop time of the following pulses {}
                        is larger than the duration of the sequence.''')
                ind = [p.index for p in err]
                errors['Root-stop'] = mess.format(ind)
                return False, (missings, errors)

        if not use_context:
            return True, pulses

        else:
            kwargs = {}
            if self.time_constrained:
                kwargs['sequence_duration'] = duration
            return self.context.compile_sequence(pulses, **kwargs)

    def get_bindable_vars(self):
        """ Access the list of bindable vars for the sequence.

        """
        return (self.linkable_vars + self.local_vars.keys() +
                self.external_vars.keys())

    @classmethod
    def build_from_config(cls, config, dependencies):
        """ Create a new instance using the provided infos for initialisation.

        Overridden here to allow context creation.

        Parameters
        ----------
        config : dict(str)
            Dictionary holding the new values to give to the members in string
            format, or dictionnary like for instance with prefs.

        dependencies : dict
            Dictionary holding the necessary classes needed when rebuilding.

        Returns
        -------
        sequence : Sequence
            Newly created and initiliazed sequence.

        """
        config = deepcopy(config)
        if 'context' in config:
            context_config = config['context']
            c_id = context_config.pop('context_id')
            c_cls = dependencies['ecpy.pulses.contexts'][c_id]
            context = c_cls()

            context.update_members_from_preferences(context_config)

        seq = super(RootSequence, cls).build_from_config(config,
                                                         dependencies)
        if 'context' in config:
            seq.context = context

        seq._post_setattr_root(True, True)
        return seq

    # --- Private API ---------------------------------------------------------

    def _post_setattr_time_constrained(self, change):
        """ Keep the linkable_vars list in sync with fix_sequence_duration.

        """
        if change['value']:
            link_vars = self.linkable_vars[:]
            link_vars.insert(0, 'sequence_end')
            self.linkable_vars = link_vars
        elif 'sequence_end' in self.linkable_vars:
            link_vars = self.linkable_vars[:]
            link_vars.remove('sequence_end')
            self.linkable_vars = link_vars

    def _update_linkable_vars(self, change):
        """
        TODO
        """
        # Don't want this to happen on member init.
        if change['type'] == 'update':
            link_vars = self.linkable_vars
            item = change['object']
            prefix = '{}_{{}}'.format(item.index)
            added = set(change['value']) - set(change.get('oldvalue', []))
            removed = set(change.get('oldvalue', [])) - set(change['value'])
            link_vars.extend([prefix.format(var)
                              for var in added])
            for var in removed:
                r = prefix.format(var)
                if r in link_vars:
                    link_vars.remove(r)
