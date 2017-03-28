# -*- coding: utf-8 -*-
# =============================================================================
# module : transfer_pulse_loop_task.py
# author : Matthieu Dartiailh & Nathanael Cottet
# license : MIT license
# =============================================================================
"""
"""
from traceback import format_exc
from inspect import cleandoc

import numpy as np
from atom.api import (Value, Str, Bool, Unicode, Dict, set_default)

from ecpy.tasks.api import (InstrumentTask, InterfaceableTaskMixin,
                            TaskInterface)


class TransferPulseLoopTask(InterfaceableTaskMixin, InstrumentTask):
    """Build and transfer several pulse sequences to an instrument.
    Awg_start task needed to turn it on.
    """
    #: Sequence path for the case of sequence simply referenced.
    sequence_path = Unicode()

    #: Sequence of pulse to compile and transfer to the instrument.
    sequence = Value()

    #: Global variable to use for the sequence.
    sequence_vars = Dict().tag(pref=True)

    #: Loop variables: channels on which the loop will be done, loop parameters
    #: names, start value, stop value and number of points per loop
    loopable_channels = Str().tag(pref=True)

    loop_names = Str().tag(pref=True)

    loop_start = Str().tag(pref=True)

    loop_stop = Str().tag(pref=True)

    loop_points = Str().tag(pref=True)

    #: Check if each sequence has to wait for a trigger
    wait_trigger = Bool().tag(pref=False)

    #: internal or external trigger
    internal_trigger = Bool().tag(pref=False)

    #: Internal trigger period in mus
    trigger_period = Str().tag(pref=True)

    def intricate_loops(self, var_count, variables):
        """
        """
        loop_points = np.array(self.format_and_eval_string(self.loop_points))
        loop_start = np.array(self.format_and_eval_string(self.loop_start))
        loop_stop = np.array(self.format_and_eval_string(self.loop_stop))

        if var_count == np.size(self.loop_names.split(',')):
            return variables
        else:
            if np.size(loop_points) == 1:
                value = np.linspace(loop_start, loop_stop, loop_points)
                variables = value
            else:
                Npoints = loop_points[var_count]
                changeN = np.product(loop_points[:var_count])
                repeatN = np.product(loop_points[var_count + 1:])
                value = np.linspace(loop_start[var_count], loop_stop[var_count],
                                Npoints)
                for p in range(0, repeatN):
                    for k in range(p*Npoints, (p+1)*Npoints): variables[k*changeN :
                        (k + 1)*changeN, var_count] = value[k % Npoints]

            var_count = var_count + 1
            return self.intricate_loops(var_count, variables)

    def check(self, *args, **kwargs):
        """Generic check making sure sequence can be compiled.
        """
        test, traceback = super(TransferPulseLoopTask,
                                self).check(*args, **kwargs)
        err_path = self.task_path + '/' + self.task_name + '_'

        loop_names = self.loop_names.split(',')
        loop_points = np.array(self.format_and_eval_string(self.loop_points))
        loop_start = np.array(self.format_and_eval_string(self.loop_start))
        loop_stop = np.array(self.format_and_eval_string(self.loop_stop))

        if (np.size(loop_names) != np.size(loop_points)
                 or np.size(loop_names) != np.size(loop_start)
                 or np.size(loop_names) != np.size(loop_stop)):
            mess = '''The numbers of loop variables, start, stop and points values do not match'''
            test =  False
            traceback[err_path+'seq'] = mess
        elif 0 in loop_points:
            mess = '''Cannot set a loop with 0 points. Please set at least 1 step.
                        '''
            test =  False
            traceback[err_path+'seq'] = mess
        else:
            if self.interface and self.sequence:

                if not self.interface.validate_context(self.sequence.context):
                    test = False
                    mess = 'Invalid context, instrument combination : {}, {}'
                    traceback[err_path+'context'] = \
                        mess.format(self.driver, self.sequence.context)

            else:
                test = False
                traceback[err_path+'seq'] = 'No interface or sequence'

        return test, traceback

    def compile_sequence(self, loop_names, value):
        """Compile the sequence.
        """
        for k, v in self.sequence_vars.items():
            if np.size(value) == 1:
                if loop_names[0] in v:
                    v = v.replace(loop_names[0], str(value))
            else:
                for p in range(np.size(value)):
                    if loop_names[p] in v:
                        v = v.replace(loop_names[p], value[p])

            self.sequence.external_vars[k] = self.format_and_eval_string(v)
        return self.sequence.compile_sequence()

    def traverse(self, depth=-1):
        """Reimplemented to also yield the sequence

        """
        infos = super(TransferPulseLoopTask, self).traverse(depth)

        for i in infos:
            yield i

        for item in self.sequence.traverse():
            yield item

    def register_preferences(self):
        """Handle the sequence specific registering in the preferences.
        """
        # super(TransferPulseLoopTask, self).register_preferences()
        if self.sequence_path:
            self.task_preferences['sequence_path'] = self.sequence_path
        elif self.sequence:
            seq = self.sequence
            self.task_preferences['sequence'] = {}
            prefs = seq.preferences_from_members()
            prefs['external_vars'] = \
                repr(dict.fromkeys(seq.external_vars.keys()))
            self.task_preferences['sequence'] = prefs

    update_preferences_from_members = register_preferences

    @classmethod
    def build_from_config(cls, config, dependencies):
        """Rebuild the task and the sequence from a config file.

        """
        builder = cls.mro()[1].build_from_config.__func__
        task = builder(cls, config, dependencies)
        if 'sequence_path' in config:
            path = config['sequence_path']
            builder = dependencies['pulses']['RootSequence']
            conf = dependencies['pulses']['sequences'][path]
            seq = builder.build_from_config(conf, dependencies)
            task.sequence = seq
            task.sequence_path = path
        elif 'sequence' in config:
            builder = dependencies['pulses']['RootSequence']
            conf = config['sequence']
            seq = builder.build_from_config(conf, dependencies)
            task.sequence = seq

        return task


class AWGTransferLoopInterface(TaskInterface):
    """Interface for the AWG, handling naming the transfered sequences and
    selecting it.
    """
    #: Generic name to use for the sequence (the number of the channel will be
    #: appended automatically).
    sequence_name = Str().tag(pref=True)

    has_view = True

    interface_database_entries = {'sequence_name': ''}

    def perform(self):
        """Compile and transfer the sequence into the AWG. Automatically
        turn off the AWG.
        """
        task = self.task
        if not task.driver:
            task.start_driver()

        task.driver.run_mode = 'SEQUENCE'

        loopable_ch = task.format_and_eval_string(task.loopable_channels)
        loopable_ch = np.array(loopable_ch)

        loop_names = task.loop_names.split(',')
        loop_points = np.array(task.format_and_eval_string(task.loop_points))

        Nwaveforms = np.product(loop_points)
        variables = np.empty((Nwaveforms, np.size(loop_names)))
        variables = task.intricate_loops(0, variables)

        task.driver.clear_sequence()

        if task.wait_trigger:
            if task.internal_trigger:
                period = task.format_and_eval_string(task.trigger_period)*10**3
                task.driver.internal_trigger = 'INT'
                task.driver.internal_trigger_period = period
            else:
                task.driver.internal_trigger = 'EXT'

        for i in range(0, Nwaveforms):
            seq_name = task.format_string(self.sequence_name) if self.sequence_name else 'Sequence'
            seq_name_iter = seq_name + '_' + str(int(i))
            res, seqs = task.compile_sequence(loop_names, variables[i])
            if not res:
                mess = 'Failed to compile the pulse sequence: missing {}, errs {}'
                raise RuntimeError(mess.format(*seqs))

            for ch_id in task.driver.defined_channels:
                if ch_id in seqs and i == 0:
                     task.driver.to_send(seq_name_iter
                                     + '_Ch{}'.format(ch_id), seqs[ch_id], False)
                     task.driver.set_sequence_pos(seq_name_iter
                                     + '_Ch{}'.format(ch_id), ch_id, i +1)

                elif ch_id in seqs and ch_id in loopable_ch:
                    task.driver.to_send(seq_name_iter
                                    + '_Ch{}'.format(ch_id), seqs[ch_id], False)
                    task.driver.set_sequence_pos(seq_name_iter
                                    + '_Ch{}'.format(ch_id), ch_id, i + 1)
                elif ch_id in seqs:
                    task.driver.set_sequence_pos(seq_name + '_' + str(0)
                                + '_Ch{}'.format(ch_id), ch_id, i +1)

            index_start = (i + 1)
            index_stop = (i + 1) % Nwaveforms + 1
            task.driver.set_goto_pos(index_start, index_stop)
            if task.wait_trigger:
                task.driver.set_trigger_pos(index_start)

        for ch_id in task.driver.defined_channels:
            if ch_id in seqs:
                ch = task.driver.get_channel(ch_id)
                ch.output_state = 'ON'

    def check(self, *args, **kwargs):
        """Simply add the sequence name in the database.

        """
        task = self.task
        task.write_in_database('sequence_name', self.sequence_name)
        return True, {}

    def validate_context(self, context):
        """Validate the context is appropriate for the driver.

        """
        return context.__class__.__name__ == 'AWGContext'
