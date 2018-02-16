# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2016-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Base classes for pulse sequences.

"""
from copy import deepcopy
from collections import Mapping
from numbers import Real
from collections import OrderedDict

from atom.api import (Int, Instance, Unicode, Bool, List,
                      Signal, set_default, Typed)
from exopy.utils.traceback import format_exc
from exopy.utils.container_change import ContainerChange
from exopy.utils.atom_util import (update_members_from_preferences,
                                   ordered_dict_to_pref,
                                   ordered_dict_from_pref)

from ..contexts.base_context import BaseContext
from ..utils.entry_eval import eval_entry, MissingLocalVars
from ..utils.validators import SkipEmpty
from ..item import Item
from ..pulse import Pulse


class AbstractSequence(Item):
    """ Base class for all sequences.

    This class defines the basic of a sequence but with only a very limited
    child support : only construction is supported, indexing is not handled
    nor is child insertion, deletion or displacement (This is because
    TemplateSequence inherits from AbstractSequence, while everything else
    inherits from BaseSequence which supports insertion/deletion/displacement).

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
    local_vars = Typed(OrderedDict, ()).tag(pref=(ordered_dict_to_pref,
                                                  ordered_dict_from_pref))

    #: String representing the item first element of definition : according
    #: to the selected mode it evaluated value will either be used for the
    #: start instant, or duration of the item.
    def_1 = Unicode().tag(pref=True, feval=SkipEmpty(types=Real))

    #: String representing the item second element of definition : according
    #: to the selected mode it evaluated value will either be used for the
    #: duration, or stop instant of the item.
    def_2 = Unicode().tag(pref=True, feval=SkipEmpty(types=Real))

    def clean_cached_values(self):
        """ Clear all internal caches.

        This should be called before evaluating a sequence.

        """
        super(AbstractSequence, self).clean_cached_values()
        self._evaluated = []
        for i in self.items:
            i.clean_cached_values()

    def evaluate_sequence(self, root_vars, sequence_locals, missing, errors):
        """Evaluate the sequence vars and all the underlying items.

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

        """
        raise NotImplementedError()

    def simplify_sequence(self):
        """Simplify the items found in the sequence.

        Pulses are always kept as they are, sequences are simplified based
        on the context ability to deal with them.

        Returns
        -------
        items : list
            List of items after simplification.

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

        """
        raise NotImplementedError()

    def traverse(self, depth=-1):
        """Traverse the items.

        """
        for i in super(AbstractSequence, self).traverse(depth=depth):
            yield i

        if depth == 0:
            for c in self.items:
                if c:
                    yield c

        else:
            for c in self.items:
                if c:
                    for subc in c.traverse(depth - 1):
                        yield subc

    # --- Private API ---------------------------------------------------------

    #: List of already evaluated items.
    _evaluated = List()

    def _evaluate_items(self, root_vars, sequence_locals, missings, errors):
        """Evaluate all the children item of the sequence

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

        """

        # Inplace modification during evaluation will update self._evaluated.
        if not self._evaluated:
            self._evaluated = [None for i in self.items if i.enabled]
        evaluated = self._evaluated

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
                if evaluated[index] is not None:
                    continue

                # If we get a pulse simply evaluate the entries, to add their
                # values to the locals and keep track of the missings to now
                # when to abort compilation.
                if isinstance(item, Pulse):
                    success = item.eval_entries(root_vars, sequence_locals,
                                                miss, errors)
                    if success:
                        evaluated[index] = [item]

                # Here we got a sequence so we must try to compile it.
                else:
                    success = item.evaluate_sequence(root_vars,
                                                     sequence_locals,
                                                     miss, errors)
                    if success:
                        evaluated[index] = item

            known_locals = set(sequence_locals.keys())
            # If none of the variables found missing during last pass is now
            # known stop compilation as we now reached a dead end. Same if an
            # error occured.
            if errors or miss and (not known_locals & miss):
                # Update the missings given by caller so that it knows it this
                # failure is linked to circle references.
                missings.update(miss)
                return False

            # If no var was found missing during last pass (and as no error
            # occured) it means the compilation succeeded.
            elif not miss:
                return True


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

        """
        prefix = '{}_'.format(self.index)

        # Definition evaluation.
        if self.time_constrained:
            self.eval_entries(root_vars, sequence_locals, missings, errors)

        # Local vars computation.
        for name, formula in self.local_vars.items():
            if name not in self._cache:
                try:
                    val = eval_entry(formula, sequence_locals)
                    self._cache[name] = val
                except MissingLocalVars as e:
                    missings.update(e.missings)
                except Exception:
                    errors[prefix + name] = format_exc()

        local_namespace = sequence_locals.copy()
        local_namespace.update(self._cache)

        res = self._evaluate_items(root_vars, local_namespace, missings,
                                   errors)
        if res:
            if self.time_constrained:
                # Check if start, stop and duration of sequence are compatible.
                start_err = [item for item in self.items
                             if item.start and item.stop and item.duration and
                             item.start < self.start]
                stop_err = [item for item in self.items
                            if item.start and item.stop and item.duration and
                            item.stop > self.stop]
                if start_err:
                    msg = ('The start time of the following items {} is '
                           'smaller than the start time of the sequence {}')
                    ind = [p.index for p in start_err]
                    errors[self.name + '-start'] = msg.format(ind, self.index)
                if stop_err:
                    msg = ('The stop time of the following items {} is '
                           'larger than  the stop time of the sequence {}')
                    ind = [p.index for p in stop_err]
                    errors[self.name + '-stop'] = msg.format(ind, self.index)

                if errors:
                    return False

            return True

        else:
            return False

    def simplify_sequence(self):
        """Inline the sequences not supported by the context.

        """
        supported = self.root.context.supported_sequences

        seq = []
        for item in self.items:
            if not item.enabled:
                continue
            if isinstance(item, Pulse) or type(item) in supported:
                seq.append(item)
            else:
                seq.extend(item.simplify_sequence())

        return seq

    def get_accessible_vars(self):
        """List the accesible variables for the sequence.

        Accessible variables can be referenced in formulas of the items
        belonging to that sequence.

        """
        return list(self.local_vars) + self.parent.get_accessible_vars()

    def preferences_from_members(self):
        """ Get the members values as string to store them in .ini files.

        Reimplemented here to save items.

        """
        pref = super(BaseSequence, self).preferences_from_members()

        for i, item in enumerate(self.items):
            pref['item_{}'.format(i)] = item.preferences_from_members()

        return pref

    def update_members_from_preferences(self, parameters):
        """Use the string values given in the parameters to update the members

        This function will update any tagged HasPrefAtom member.
        Reimplemented here to update items.

        """
        for i, item in enumerate(self.items):
            if 'item_{}'.format(i) in parameters:
                para = parameters.pop('item_{}'.format(i))
                item.update_members_from_preferences(para)
        super(BaseSequence, self).update_members_from_preferences(parameters)

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

        # In the absence of a root item do nothing else than inserting the
        # child.
        if self.has_root:
            # Give him its root so that it can proceed to any child
            # registration it needs to.
            child.root = self.root

            #: If we update linkable vars on this item then we need to inform
            #: the root of this.
            child.observe('linkable_vars', self.root._update_global_vars)
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

        if self.has_root:
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

        with child.suppress_notifications():
            child.root = None
            child.parent = None

            child.index = 0

        if self.has_root:
            child.unobserve('linkable_vars', self.root._update_global_vars)

            if isinstance(child, BaseSequence):
                child.unobserve('_last_index', self._item_last_index_updated)

            self._recompute_indexes()

        notification = ContainerChange(obj=self, name='items',
                                       removed=[(index, child)])
        self.items_changed(notification)

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

        """
        sequence = cls()
        update_members_from_preferences(sequence, config)

        i = 0
        pref = 'item_{}'
        while True:
            item_name = pref.format(i)
            if item_name not in config:
                break
            item_config = config[item_name]
            i_id = item_config.pop('item_id')
            i_cls = dependencies['exopy.pulses.item'][i_id]
            item = i_cls.build_from_config(item_config,
                                           dependencies)
            sequence.add_child_item(i, item)
            i += 1

        return sequence

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
                if isinstance(item, BaseSequence):
                    item.observe('_last_index', self._item_last_index_updated)
            # Connect only now to avoid cleaning up in an unwanted way the
            # root linkable vars attr.

        else:
            for item in self.items:
                item.root = None
                if isinstance(item, BaseSequence):
                    item.unobserve('_last_index',
                                   self._item_last_index_updated)

    def _post_setattr_time_constrained(self, old, new):
        """Update the linkable vars when the sequence is time constrained.

        """
        if new:
            self.linkable_vars = ['start', 'stop', 'duration']
        else:
            self.linkable_vars = []
            # This ensures that the SkipEmpty will indeed skip evaluation
            del self.def_1
            del self.def_2

    def _recompute_indexes(self, first_index=0, free_index=None):
        """ Recompute the item indexes and update the vars of the root_seq.

        Parameters
        ----------
        first_index : int, optional
            Index in items of the first item whose index needs to be updated.

        free_index : int, optional
            Value of the first free index.

        """
        if free_index is None:
            free_index = self.index + 1

        # Cleanup the linkable_vars for all the pulses which will be reindexed.
        linked_vars = self.root.global_vars
        for var in linked_vars[:]:
            if var[0].isdigit() and int(var[0]) >= free_index:
                linked_vars.remove(var)

        for item in self.items[first_index:]:

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

    The start, stop, duration and def_1, def_2 members are not used by the
    RootSequence. The time_constrained member only affects the use of the
    sequence duration.

    """
    # --- Public API ----------------------------------------------------------

    #: Dictionary of external variables whose values should be given before
    #: the start of the compilation stage.
    external_vars = Typed(OrderedDict, ()).tag(pref=(ordered_dict_to_pref,
                                                     ordered_dict_from_pref))

    #: Duration of the sequence when it is fixed. The unit of this time is
    # fixed by the context.
    sequence_duration = Unicode().tag(pref=True)

    #: Reference to the executioner context of the sequence.
    context = Typed(BaseContext).tag(pref=True)

    #: Ids of the global linkable vars. Those are for example the start, stop
    #: and duration of most items.
    global_vars = List()

    index = set_default(0)
    name = set_default('Root')

    def __init__(self, **kwargs):
        super(RootSequence, self).__init__(**kwargs)
        self.root = self

    def clean_cached_values(self):
        """ Clear all internal caches.

        This is called before evaluating a sequence.

        """
        super(RootSequence, self).clean_cached_values()
        self.context.clean_cached_values()

    def evaluate_sequence(self):
        """Evaluate the root sequence entries and all sub items.

        Returns
        -----------
        result : bool
            Flag indicating whether or not the compilation succeeded.

        missing : set
            Set of the entries whose values where never found and a dict of the
            errors which occured during compilation.

        errors : dict
            Dict describing the errors that occured during evaluation.

        """
        # First make sure the cache is clean
        self.clean_cached_values()

        missings = set()
        errors = {}
        root_vars = self.external_vars.copy()

        # Local vars computation.
        for name, formula in self.local_vars.items():
            if name not in self._cache:
                try:
                    val = eval_entry(formula, root_vars)
                    self._cache[name] = val
                except MissingLocalVars as e:
                    missings.update(e.missings)
                except Exception:
                    errors['root_' + name] = format_exc()

        root_vars.update(self._cache)

        if self.time_constrained:
            try:
                duration = eval_entry(self.sequence_duration, root_vars)
                self.stop = self.duration = duration
                root_vars['sequence_end'] = duration
            except MissingLocalVars as e:
                missings.update(e.missings)
            except Exception:
                errors['root_seq_duration'] = format_exc()

        res = self.context.eval_entries(root_vars, root_vars, missings, errors)

        res &= self._evaluate_items(root_vars, root_vars, missings, errors)

        if not res:
            return False, missings, errors

        if self.time_constrained:
            overtime = []
            self._validate_times(self.items, overtime)

            if overtime:
                mess = ('The stop time of the following pulses {} is larger '
                        'than the duration of the sequence.')
                ind = [p.index for p in overtime]
                errors['root-stop'] = mess.format(ind)
                return False, missings, errors

        return True, missings, errors

    def get_accessible_vars(self):
        """ Access the list of local variables for the sequence.

        """
        return (self.linkable_vars + self.global_vars +
                list(self.local_vars) + list(self.external_vars))

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
        seq = super(RootSequence, cls).build_from_config(config,
                                                         dependencies)
        if 'context' in config and isinstance(config['context'], Mapping):
            context_config = config['context']
            c_id = context_config.pop('context_id')
            c_cls = dependencies['exopy.pulses.context'][c_id]
            context = c_cls()

            context.update_members_from_preferences(context_config)
            seq.context = context

        seq._post_setattr_root(None, seq)
        return seq

    def traverse(self, depth=-1):
        """Traverse the items.

        """
        for i in super(RootSequence, self).traverse(depth=depth):
            yield i

        yield self.context

    # --- Private API ---------------------------------------------------------

    def _validate_times(self, items, overtime):
        """Check The timing of the pulses respect the duration of the sequence.

        Parameters
        ----------
        items : list
            List of items whose end time should be checked.

        overtime : list
            List of items which do not respect the time constraint.

        """
        for i in items:
            if isinstance(i, Pulse):
                if i.stop > self.stop:
                    overtime.append(i)
            else:
                self._validate_times(i.items, overtime)
                if i.duration and i.stop > self.stop:
                    overtime.append(i)

    def _post_setattr_time_constrained(self, old, new):
        """ Keep the linkable_vars list in sync with fix_sequence_duration.

        """
        if new:
            link_vars = self.linkable_vars[:]
            link_vars.insert(0, 'sequence_end')
            self.linkable_vars = link_vars
        elif 'sequence_end' in self.linkable_vars:
            link_vars = self.linkable_vars[:]
            link_vars.remove('sequence_end')
            self.linkable_vars = link_vars

    def _update_global_vars(self, change):
        """Update the global vars each time the linkable vars of an item is
        updated.

        """
        # Don't want this to happen on member init.
        if change['type'] == 'update':
            glob_vars = self.global_vars
            item = change['object']
            prefix = '{}_{{}}'.format(item.index)
            added = set(change['value']) - set(change.get('oldvalue', []))
            removed = set(change.get('oldvalue', [])) - set(change['value'])
            glob_vars.extend([prefix.format(var)
                              for var in added])
            for var in removed:
                r = prefix.format(var)
                if r in glob_vars:
                    glob_vars.remove(r)
