.. _sequence_edition:

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

- the sequence of of pulses itself which can contain subsequences
- a compilation context responsible of compiling the pulse sequence and
  transferring it to a waveform geenrator.

For simplicity sakes, we will first decribe the role of the pulses and sequences
but keep in mind that some settings can only be performed once a context is
selected.

.. note::

    The edition of the pulse sequence is concentrated in a single scrollable
    area. To avoid undesired modification of some settings it is advised to
    only scroll when the mouse is over the scrool bar area.

Adding a pulse
^^^^^^^^^^^^^^


Adding a sequence
^^^^^^^^^^^^^^^^^


Choosing a context
^^^^^^^^^^^^^^^^^^


Checking that the sequence compile
----------------------------------
