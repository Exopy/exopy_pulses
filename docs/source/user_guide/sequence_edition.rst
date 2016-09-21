.. _sequence_edition:

.. include:: ../substitutions.sub

Sequence edition
================

Once the Ecpy application started, select the Pulses workspace to
create a new sequence. The following section will guide through the
required steps and explain the principle of pulse synthesis in Ecpy.

.. contents::

Creating a sequence
-------------------

When selecting the Pulses workspace, the measure edition panels are replaced
by three panels :

- one is dedicated to the edition of a sequence
- the second, tabbed beind the first, can be used to edit the variables of the sequence
  (more on their use will be said later on).
- the thrid one is nothing else than a log panel similar to the one present in
  the measure edition workspace.

.. note::

    Currently the workspace supports only editing a single sequence at
    a time.

When starting the editor contains a blank sequence. You can either start
from there or load an existing sequence using the File menu. From the
same menu you can save the sequence (Ctrl+S can also be used).

A pulse sequence is made of two things :

- the sequence of pulses itself which can contain subsequences.
- a compilation context responsible of compiling the pulse sequence and
  transferring it to a waveform geenrator.

For simplicity sakes, we will first decribe the role of the pulses and sequences
but keep in mind that some settings can only be performed once a context is
selected.

.. note::

    The edition of the pulse sequence is concentrated in a single scrollable
    area. To avoid undesired modification of some settings it is advised to
    only scroll when the mouse is over the scrool bar.

Adding a pulse
^^^^^^^^^^^^^^

When a sequence is empty, it displays two buttons : one dedicated to the addition
of a pulse the other to the addition of a sequence. Clicking on the one
dedicated to the pulse will immediately insert a new pulse in the sequence and
the two previously diplayed buttons will disappear.

.. note::

    Just like when editing the tasks composing a measure, the button of the left
    of each item (pulse/sequence) can be used to add new items, move items or
    delete items.

The inserted pulse is blank. First you should determine its kind. A pulse can
be either **Logical** or **Analogical**. A logical pulse as its name indicates
can only take two values 0 or 1. By convention during the pulse duration its
take the value 1. By contrast an analogical pulse is arbitrary and hence
requires more settings that will be detailed later on.

Once the kind chosen, if you have selected a context, you can then specify on
which channel should the pulse be played. Depending on its kind, only the matching
channels will be proposed.

.. note::

    The contexts provide the possibility to invert the meaning of a logical channel.

One setting common to all kind of pulse is the timing of the pulse, which can be
specified in three different ways : start/stop, start/duration, or duration/stop.
In each case, the two required parameters can be specified using formulas with variables
in between \{\}.

The accessible variables, listed by the autocompletion, are the following :

- the global variables declared on the root sequence (discussed later)
- the local variables declared in a subsequence (discussed later)
- the start/stop/duration of any pulse or sequence (in the form i_start, ...)
  where i is the index of the pulse or sequence. This include the ones of
  pulses occuring after the edited pulse.

To avoid editing sequences more than necessary, it is advised to avoid hardcoding durations
but rather use variables and express the constraints between the pulses using their
timing information.

.. note::

    The pulses being indexed rather than named, one should be careful when inserting,
    moving or deleting a pulse as this will lead to a re-indexing of the pulses.

As previously mentionned, the above information are sufficient to specify a logical pulse
but not an analogical one. Analogical pulses need additional parameters provided by their
shape and an optional modulation.

The shape of a pulse can be chosen from an existing list of shapes providing different parameters.
As it is very common in some experiments to use such pulses to drives mixers, an additional
sinusoïdal modulation can be added. In such a case the output pulse will be a sinuoïdal signal
whose amplidtude is given by the shape. As can be expected one can specify the frequency
and phase of the modulation.

For simple sequences using only pulses is sufficient, however if a more complex/versatile
structure is required subsequence can be used. For example, the |ConditionalSequence|
can be used to include its child pulses on a given condition making it easy to
compile a witness sequence missing the active part.

Adding a sequence
^^^^^^^^^^^^^^^^^

Adding a sequence is very similar to a adding a task to a task hierarchy. When
clicking the button, you will be prompted to choose the kind of sequence to add
and provide some informations. Once this is done the sequence will be inserted.

Depending on the sequence you will have to adjust specific parameters but some
of them are common (and also apply to a point to the root sequence):

- should the sequence have a fixed duration ?
  This is particularly useful is a specific duty cycle should be respected. When
  activated you will have to specify the timing of the sequence just like for a
  pulse and teh context will take care to fill in any necessary blank. Note that
  the timing infos of a sequence are only accessible in the formula fields if the
  sequence as a fixed duration.

- the local variables of the sequence.
  Local variables of a sequence are only visible to its child items and can be
  used to avoid writing multiple times the same formula.

Your sequence is now ready (up to the selection of the channels) and it is
time to select a context.

Choosing a context
^^^^^^^^^^^^^^^^^^

The context is responsible for compiling the sequence and transferrring it to the
instrument. During compilation, all the formulas are evaluated and the sequence
is simplified before being transferred to the instrument.

As a context is linked to a particular instrument, it knwows the available channels.

The context can offer different parametrization, the default ones being :

- the unit used for representing the time in the sequence. By default the unit
  is the mus.

- the logical channels whose meaning should be inverted (an absence of pulse becoming
  a logical 1, a presence a 0)

.. warning::

    Currently the context does not support using arbitrary formulas.

.. note::

    Because some optimizations of the compilation may be specific to the waveform
    generator used the context can work only with specific drivers.


Using the external variables
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is often desirable to parametrize a pulse sequence, for example performing a Rabi
oscillation measurement requires to vary duration of the driving pulse. Such a parametrization
is possible through the use of the root sequence external variables. Contrary to the
local variables, the externals variables will be accessible from the task used to
transfer the sequence to the instrument.

These variables can be edited from the second tab of the workspace. Their value will
be specified mainly through the transfer task but are needed here too to allow to
check that the sequence can be compiled as explained in the next section.


Checking that the sequence compile
----------------------------------

Once your sequence written and saved, it may be a good idea to check that it can be
compiled. To check it, click on the compile button at the bottom right corner. This
will open a dialog,

From this dialog, you can edit the external variables and attempt to compile the sequence.
If the compilation succeed the compilation duration will appear in green, if not in
red and the compilations errors will be visible in the errors tabs.

.. note::

    At the moment it is not possible to transfer a pulse sequence directly from the
    pulse sequence edition workspace.
