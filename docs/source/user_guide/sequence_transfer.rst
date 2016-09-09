.. _sequence_transfer:

.. include:: ../substitutions.sub

Sequence transfer
=================

Once you have created a sequence, you are ready to use it in a measure. To do so
you need to transfer it to the waveform generator. The following section will
describe the interaction between the sequence and the transfer task.

Transfer task
-------------

The transfer task (|TranfserPulseSequenceTask|) allow to load a sequence from a file
and to specify the value of the external variables as functions of the task database
values. It also allows to parametrize the context.

The chosen instrument must match the selected context. If it is not so, a dialog
will notify you that you should choose a new driver.

As it may happen that you edit the sequence after building a measure, each time
you reopen the measure the system will check whether you have loaded the last version
of the pulse sequence. If the loaded version is outdated the refresh button will
be red. In the same way, during enqueuing a warning will be emitted if the sequence
is oudated.

After a successful transfer the task write into the database the informations concerning
the sequence returned by the context (this can be the name under which it is stored on
the instrument for example).

Sequence re-edition
-------------------

No matter the care you take in writing the sequence it may well happen that
you need to quickly re-edit it while modifying a measure. If it is opened in the
Pulses workspace you can easily switch and simply reload, however it may prove
cumbersome if it is not so.

The easiest way then consist in selecting the transfer task in tree on left of the
measure edition panel, and then selecting the pulses editor that appeared in the
tabs above the task edition panel. When selecting it, the tree will disappear and
you will have access to the sequence. You can then  perform any operation you may in the
Pulses workspace (note that you can only edit the name of the external variables, as
their values should be specified in the task).

Once you are done, go back to the task edition (using the tabs on top). If you have
changed of context you may have to choose a new instrument. Or similarly provide
the values of any new external variable.

You can also save the sequence and override the old file or save it to a new
file.
