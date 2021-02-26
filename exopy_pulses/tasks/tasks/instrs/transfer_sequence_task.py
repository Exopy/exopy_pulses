# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to transfer a sequence on an AWG.

"""
import os
from pprint import pformat
from collections import OrderedDict

from atom.api import Value, Str, Float, Typed
from exopy.tasks.api import InstrumentTask
from exopy.utils.atom_util import ordered_dict_from_pref, ordered_dict_to_pref
from exopy.utils.traceback import format_exc

import matplotlib.pyplot as plt
import numpy as np


class TransferPulseSequenceTask(InstrumentTask):
    """Build and transfer a pulse sequence to an instrument.

    """
    #: Sequence path for the case of sequence simply referenced.
    sequence_path = Str().tag(pref=True)

    #: Time stamp of the last modification of the sequence file.
    sequence_timestamp = Float().tag(pref=True)

    #: Sequence of pulse to compile and transfer to the instrument.
    sequence = Value()

    #: Global variable to use for the sequence.
    sequence_vars = Typed(OrderedDict, ()).tag(pref=(ordered_dict_to_pref,
                                                     ordered_dict_from_pref))
    

    def check(self, *args, **kwargs):
        """Check that the sequence can be compiled.

        """
        test, traceback = super(TransferPulseSequenceTask,
                                self).check(*args, **kwargs)
        err_path = self.path + '/' + self.name + '-'

        if not self.sequence:
            traceback[err_path+'sequence'] = 'There is no selected sequence.'
            return False, traceback

        msg = 'Failed to evaluate {} ({}): {}'
        seq = self.sequence
        for k, v in self.sequence_vars.items():
            try:
                seq.external_vars[k] = self.format_and_eval_string(v)
            except Exception:
                test = False
                traceback[err_path+k] = msg.format(k, v, format_exc())

        if not test:
            return test, traceback

        context = seq.context
        res, infos, errors = context.compile_and_transfer_sequence(seq)

        if not res:
            traceback[err_path+'compil'] = errors
            return False, traceback

        for k, v in infos.items():
            self.write_in_database(k, v)

        if self.sequence_path:
            if not (self.sequence_timestamp ==
                    os.path.getmtime(self.sequence_path)):
                msg = 'The sequence is outdated, consider refreshing it.'
                traceback[err_path+'outdated'] = msg

        return test, traceback

    def perform(self):
        """Compile the sequence.

        """
        seq = self.sequence
        context = seq.context
        for k, v in self.sequence_vars.items():
            seq.external_vars[k] = self.format_and_eval_string(v)

#        self.driver.run_mode = 'CONT'
        res, infos, errors = context.compile_and_transfer_sequence(seq,
                                                                   self.driver)
        if not res:
            raise Exception('Failed to compile sequence :\n' +
                            pformat(errors))

        for k, v in infos.items():
            self.write_in_database(k, v)
            
    def compile_and_plot(self, variables):
        """Compile the sequence and plot it.

        """
        
        seq = self.sequence
        context = seq.context
        for k, v in variables.items():
            seq.external_vars[k] = self.format_and_eval_string(v)

        table, marker1, marker2, errors = context.compile_sequence(seq)
        if not table:
            raise Exception('Failed to compile sequence :\n' +
                            pformat(errors))
        freq = context.list_sequence_infos()['sampling_frequency'] 
        
        channel_num = len(table)
        #fig, axs = plt.subplots(4,1, figsize=(15, 8))
        fig, axs = plt.subplots(channel_num,1, figsize=(15, 2.5*channel_num),
                                sharex=True)
        fig.subplots_adjust(hspace = 0.5, wspace=.001)
        
        x = np.arange(len(table[list(table.keys())[0]]))/freq*10**6
        
        if len(list(table.keys())) == 1:
            key = list(table.keys())[0]
            axs.plot(x,table[key], label = 'wvfm')
            axs.plot(x,marker1[key], label = 'M1')
            axs.plot(x,marker2[key], label = 'M2')
            axs.set_xlabel('time (us)')
            axs.set_ylabel(key)
            axs.axis(xmin = 0, xmax = x[-1],ymin = -1.2, ymax = 1.2)
            axs.legend(loc=6)
        else:
            for i, key in enumerate(np.sort(list(table.keys()))):
                axs[i].plot(x,table[key], label = 'wvfm')
                axs[i].plot(x,marker1[key], label = 'M1')
                axs[i].plot(x,marker2[key], label = 'M2')
                axs[i].set_xlabel('time (us)')
                axs[i].set_ylabel(key)
                axs[i].axis(xmin = 0, xmax = x[-1],ymin = -1.2, ymax = 1.2)
                axs[i].legend(loc=6)
        return fig

    def register_preferences(self):
        """Register the task preferences into the preferences system.

        """
        super(TransferPulseSequenceTask, self).register_preferences()

        if self.sequence:
            self.preferences['sequence'] =\
                self.sequence.preferences_from_members()

    update_preferences_from_members = register_preferences

    def traverse(self, depth=-1):
        """Reimplemented to also yield the sequence

        """
        infos = super(TransferPulseSequenceTask, self).traverse(depth)

        for i in infos:
            yield i

        if self.sequence:
            for item in self.sequence.traverse():
                yield item

    @classmethod
    def build_from_config(cls, config, dependencies):
        """Rebuild the task and the sequence from a config file.

        """
        builder = cls.mro()[1].build_from_config.__func__
        task = builder(cls, config, dependencies)

        if 'sequence' in config:
            pulse_dep = dependencies['exopy.pulses.item']
            builder = pulse_dep['exopy_pulses.RootSequence']
            conf = config['sequence']
            seq = builder.build_from_config(conf, dependencies)
            task.sequence = seq

        return task

    def _post_setattr_sequence(self, old, new):
        """Set up n observer on the sequence context to properly update the
        database entries.

        """
        entries = self.database_entries.copy()
        if old:
            old.unobserve('context', self._update_database_entries)
            if old.context:
                for k in old.context.list_sequence_infos():
                    del entries[k]
        if new:
            new.observe('context', self._update_database_entries)
            if new.context:
                entries.update(new.context.list_sequence_infos())

        if entries != self.database_entries:
            self.database_entries = entries

    def _update_database_entries(self, change):
        """Reflect in the database the sequence infos of the context.

        """
        entries = self.database_entries.copy()
        if change.get('oldvalue'):
            for k in change['oldvalue'].list_sequence_infos():
                del entries[k]
        if change['value']:
            context = change['value']
            entries.update(context.list_sequence_infos())

        self.database_entries = entries
