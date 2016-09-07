# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyHqcLegacy Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Task to transfer a sequence on an AWG.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

from traceback import format_exc
from pprint import pformat

from atom.api import Value, Unicode, Dict, Bool

from ecpy.tasks.api import InstrumentTask


class TransferPulseSequenceTask(InstrumentTask):
    """Build and transfer a pulse sequence to an instrument.

    """
    #: Sequence path for the case of sequence simply referenced.
    sequence_path = Unicode().tag(pref=True)

    #: Time stamp of the last modification of the sequence file.
    sequence_timestamp = Unicode().tag(pref=True)

    #: Sequence of pulse to compile and transfer to the instrument.
    sequence = Value().tag(pref=True)

    #: Global variable to use for the sequence.
    sequence_vars = Dict().tag(pref=True)

    def check(self, *args, **kwargs):
        """Check that the sequence can be compiled.

        """
        test, traceback = super(TransferPulseSequenceTask,
                                self).check(*args, **kwargs)
        err_path = self.task_path + '/' + self.task_name + '-'

        msg = 'Failed to evaluate {} ({}): {}'
        for k, v in self.sequence_vars.items():
            try:
                self.format_and_eval_string(v)
            except Exception:
                test = False
                traceback[err_path+k] = msg.format(k, v, format_exc())

        if test:
            res, missings, errors = self.sequence.evaluate_sequence()
            if not res:
                test = False
                msg = 'Those variables were never evaluated : %s'
                errors['missings'] = msg % missings
                msg = 'Evaluation failed. Errors : {}.'.format(errors)
                traceback[err_path+'compil'] = msg

        return test, traceback

    def perform(self):
        """Compile the sequence.

        """
        seq = self.sequence
        context = seq.context
        for k, v in self.sequence_vars.items():
            self.sequence.external_vars[k] = self.format_and_eval_string(v)

        res, missings, errors = seq.evaluate_sequence()
        if not res:
            msg = 'The following variables were never computed : %s'
            errors['Unknown variables'] = msg % missings
            raise Exception('Failed to evaluate sequence :\n' +
                            pformat(errors))

        res, errors = context.compile_and_transfer_sequence(res, self.driver)

        # XXX the context may need to write in the database

        if not res:
            raise Exception('Failed to compile sequence :\n' +
                            pformat(errors))

    def traverse(self, depth=-1):
        """Reimplemented to also yield the sequence

        """
        infos = super(TransferPulseSequenceTask, self).traverse(depth)

        for i in infos:
            yield i

        for item in self.sequence.traverse():
            yield item

    @classmethod
    def build_from_config(cls, config, dependencies):
        """Rebuild the task and the sequence from a config file.

        """
        builder = cls.mro()[1].build_from_config.__func__
        task = builder(cls, config, dependencies)

        builder = dependencies['pulses']['sequences']['RootSequence']
        conf = config['sequence']
        seq = builder.build_from_config(conf, dependencies)
        task.sequence = seq

        return task
