.. _context

.. include:: ../substitutions.sub

Context and pulse sequence compilation
======================================

Once a pulse sequence created it need to be uploaded on the waveform generator.
The associated compilation (ie translation) and transfer is handled by a context
object specific to each instrument (and driver). The following sections will
describe in details the responsability of the context and how to implement new
ones.

.. note::

    As all instrument specific actions are handled by the driver, the transfer
    sequence task does not rely on interfaces, implementing the context matching
    your instrument is sufficient.

.. contents::

Compilation process
-------------------

The compilation of a pulse sequence is a three step process :

- first the sequence is evaluated. In this process, all the formulas are evaluated
  which defines explicitely all the pulses parameters. As pulses can refer to pulses
  occuring later in the sequence this process can happen in multiple passes till
  all the formulas can be evaluated (or till a dead end is detected).
- then the sequence is simplified. At this step, all the sequences not explicitely
  supported by the context are inlined. For example, if the context cannot do anything
  special with any sequence this leads to the production to a flat list of pulses.
  A context may choose to special case a specific type of sequence if the hardware
  provide an effficient support for it, one example could be repeating a subsequence
  multiple times without explicitely creating a repetitive byte sequence.
- finally the list of simplified items is passed to the context along with the driver
  of the instrument on which to transfer the sequence. It is then up to the context
  to turn the list of simple items into an hardware compatible representation and
  to proceed to the transfer.

Creating a new context
----------------------

Creating a new context is as usual a three step process :

- first the context itself which holds the logic must be created.
- to allow a user to correctly parametrize the context a dedicated widget or view
  should also be created.
- finally the context must be declared in the manifest of the plugin contributing
  it.


Implementing the logic
^^^^^^^^^^^^^^^^^^^^^^

The context itself should be a subclass of |BaseContext|.

The context parameters should be declared using the appropriate member and tagged
with 'pref' in order to be correctly saved. If the default way of
saving/restoring (repr/literal_eval) is enough simply use True as a value
otherwise you can specify the function to use to serialize/desarialize should
be passed as a tuple/list.

.. code-block:: python

    from numbers import Real

    from atom.api import Unicode, Int
    from ecpy_pulses.pulses.api import Feval

    class MyContext(BaseContext):
        """MyContext description.

        Use Numpy style docstrings.

        """
        #: my_int description
        my_int = Int(1).tag(pref=True)  # Integer with a default value of 1

        #: my_formula description
        my_formula = Unicode().tag(pref=True, feval=Feval(types=Real))

You will also need to implement two methods :

# XXX
- **compile_and_transfer_sequence**: this method does the heavy work of conversion
  and transfer. When called the entries of the context have been evaluated and are
  available in the *_cache* member. The passed list of items is guaranteed to be
  composed only of object the context can handle. Note however that if a context
  declare it supports a specific sequence, the sequence items are not simplified.
  If the driver is None, the context should do its best to validate that the
  sequence can be compiled.
- **list_sequence_infos**: return a dict matching the infos returned are a successful
  compilation. Those infos can for example contain the names under which the sequence
  is stored for each channel.

Creating the view
^^^^^^^^^^^^^^^^^

All context views should inherit from |BaseContextView| which is nothing more than
a customized Container. The view will always have a reference to the context it is
used to edit under *context* and to the view of the root sequence. From there you
are free to design your UI the way you want.


To edit member corresponding to formulas with access to the sequence variables,
note that the |QtLineCompleter| and |QtTextCompleter| widgets give
auto-completion for the sequence variables after a '{'. You need to set the
entries_updater attribute to *root.item.get_accessible_vars*. If you do
so you may also want to use |EVALUATER_TOOLTIP| as a tool tip (*tool_tip* member)
so that your user get a nice explanation about what he can and cannot write in
this field. From a general point of view it is a good idea to provide
meaningful tool tips.

.. code-block:: enaml

    enamldef MyContextView(BaseContextView):

        QtLineCompleter:
            text := context.my_formula
            entries_updater = root.item.get_accessible_vars
            tool_tip = EVALUATER_TOOLTIP


For more informations about the Enaml syntax please give a look at
the relevant section in the Ecpy documentation.


At this point your context is ready to be registered in Ecpy, however writing a
bunch of unit tests for your context making sure it works as expected and will go
on doing so is good idea. Give a look at :doc:`testing` for more details about
writing tests and checking that your tests do cover all the possible cases.


Registering your context
^^^^^^^^^^^^^^^^^^^^^^

The last thing you need to do is to declare your shape in a plugin manifest so
that the main application can find it. To do so your plugin should contribute
an extension to 'ecpy.pulses.contexts' providing |Contexts| and/or |Context|
objects.

Let's say we need to declare a single context named 'MyContext'. The name of our
extension package (see the glossary in Ecpy documentation) is named 'my_ecpy_plugin'.
Let's look at the example below:

.. code-block:: enaml

    enamldef MyPluginManifest(PluginManifest):

        id = 'my_plugin_id'

        Extension:
            point = 'ecpy.pulses.contexts'

            Contexts:
                path = 'my_ecpy_plugin'

                Context:
                    context = 'my_context:MyContext'
                    view = 'views.my_context:MyContextView'

We declare a single child for the extension a |Contexts| object. |Contexts| does
nothing by themselves they are simply container for grouping shapes
declarations. They have a single attribute:

- 'path': when declaring a shape you must specify in which module it is defined
  as a '.' sperated path. When declaring a path in a |Contexts| it will be
  prepended to any path-like declaration in all children.

We then declare our shape using a |Context| object. A |COntext| has four attributes
but only three of them must be given non-default values :

- 'context': this is the path ('.' separated) to the module defining the context. The
  actual name of the context is specified after a colon (':'). As mentioned above
  the path of all parent |Contexts| is preprended to this path.
- 'view': this identic to the context attribute but used for the view definition.
  Once again the path of all parent |Contexts| is preprended to this path.
- 'instruments': list of all the driver ids supported by this context. For memory
  a driver id is of the form 'definition_package.architecture.class_name'
- 'metadata': Any additional informations about the context. Those should be
  specified as a dictionary.

This is it. Now when starting Ecpy your new context should be listed and work
with the specified drivers. Note that just for tasks, you can extend the list
of supported drivers by redeclaring a context but specifying only its id
(package_name.class_name) and the additionally supported drivers.
