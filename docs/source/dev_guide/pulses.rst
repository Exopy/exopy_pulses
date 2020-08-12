.. _pulses:

.. include:: ../substitutions.sub

Pulse sequences and shapes
==========================

Synthesis of pulse sequences in Exopy is centered around the notion of sequence
and pulse. Those two elements are used describe the sequence to synthetyse,
while the actual synthesis is actually carried out by the context.

The following sections will present how to contribute new shapes for analogical
pulses, new sequences and new configuration objects for sequences. The case of
context will be treated in detail in another setion.

.. contents::

Object with evaluable fields
----------------------------

Sequence, pulses, shapes and contexts can all have formula fileds that can
be either formatted or formatted and evaluated. In those fields, variables
such as the start, stop, and duration of any pulse can be referenced in between
curly brackets.

The handling of the evaluation is automated by their common base class |HasEvaluableFields|.
All members tagged with either 'fmt' or 'feval' will be automatically formatted/formatted and
evaluated when the eval_entries method is called. In case of success, the result will be
stored in the *_cache* dictionary of the object. For formatted values, the value of the
'fmt' metadata should be either **True** or **False** depending on whether the
formatted value should be stored in the global variables avalaible to other object
when evaluating their entries or not. For feval values, the value of the 'feval'
metadata should be a |Feval| instance (which is reminiscent of the system used
for tasks). |Feval| can be subclassed to customize when to perform the evaluation
and how to check the resulting value. By default, a tuple of types can be
specified. For values which should be stored as globals, the **store_global**
member should be set to **True**.

.. note::

    Shapes and contexts cannot store values in the global namespace.

.. note::

    Even if the name is identical to the objects used for tasks, the
    Feval object sused in both cases are different. For pulses related
    object, it should be imported from *exopy_pulses.pulses.api*.


Creating a new shape
--------------------

Creating a new shape is a three step process :

- first the shape itself which holds the logic must be created.
- to allow a user to correctly parametrize the shape a dedicated widget or view
  should also be created.
- finally the shape must be declared in the manifest of the plugin contributing
  it.


Implementing the logic
^^^^^^^^^^^^^^^^^^^^^^

The shape itself should be a subclass of |AbstractShape|.

The shape parameters should be declared using the appropriate member and tagged
with 'pref' in order to be correctly saved. If the default way of
saving/restoring (repr/literal_eval) is enough simply use True as a value
otherwise you can specify the function to use to serialize/desarialize should
be passed as a tuple/list.

.. code-block:: python

    from numbers import Real

    from atom.api import Str, Int
    from exopy_pulses.pulses.api import Feval

    class MyShape(AbstractShape):
        """MyShape description.

        Use Numpy style docstrings.

        """
        #: my_int description
        my_int = Int(1).tag(pref=True)  # Integer with a default value of 1

        #: my_formula description
        my_formula = Str().tag(pref=True, feval=Feval(types=Real))

You will also need to implement one method :

- **compute** : this method should evaluate and return the shape of the pulse at the
  provided times (taking into account the unit in which the time is expressed).
  It should return an array. As mentioned before values computed by **eval_entries**
  can be found in the **_cache** dictionary.

Creating the view
^^^^^^^^^^^^^^^^^

All shape views should inherit from |AbstractShapeView| which is nothing more than
a customized SplitItem (Which it should have a single Container child). The view
will always have a reference to the shape it is used to edit under *shape* and
to the pulse using the shape *item*. From there you are free to design your UI the
way you want.


To edit member corresponding to formulas with access to the sequence variables,
note that the |QtLineCompleter| and |QtTextCompleter| widgets give
auto-completion for the sequence variables after a '{'. You need to set the
entries_updater attribute to *item.parent.get_accessible_vars*. If you do
so you may also want to use |EVALUATER_TOOLTIP| as a tool tip (tool_tip member)
so that your user get a nice explanation about what he can and cannot write in
this field. From a general point of view it is a good idea to provide
meaningful tool tips.

.. code-block:: enaml

    enamldef MyShapeView(AbstractShapeView):

        QtLineCompleter:
            text := shape.my_formula
            entries_updater = item.parent.get_accessible_vars
            tool_tip = EVALUATER_TOOLTIP


For more informations about the Enaml syntax please give a look at
the relevant section in the Exopy documentation.


At this point your shape is ready to be registered in Exopy, however writing a
bunch of unit tests for your shape making sure it works as expected and will go
on doing so is good idea. Give a look at :doc:`testing` for more details about
writing tests and checking that your tests do cover all the possible cases.


Registering your shape
^^^^^^^^^^^^^^^^^^^^^^

The last thing you need to do is to declare your shape in a plugin manifest so
that the main application can find it. To do so your plugin should contribute
an extension to 'exopy.pulses.shapes' providing |Shapes| and/or |Shape|
objects.

Let's say we need to declare a single shape named 'MyShape'. The name of our
extension package (see the glossary section in Exopy documentation) is named
'my_exopy_plugin'. Let's look at the example below:

.. code-block:: enaml

    enamldef MyPluginManifest(PluginManifest):

        id = 'my_plugin_id'

        Extension:
            point = 'exopy.pulses.shapes'

            Shapes:
                path = 'my_exopy_plugin'

                Shape:
                    shape = 'my_shape:MyShape'
                    view = 'views.my_shape:MyView'

We declare a single child for the extension a |Shapes| object. |Shapes| does
nothing by themselves they are simply container for grouping shapes
declarations. They have a single attribute:

- 'path': when declaring a shape you must specify in which module it is defined
  as a '.' sperated path. When declaring a path in a |Shapes| it will be
  prepended to any path-like declaration in all children.

We then declare our shape using a |Shape| object. A |Shape| has three attributes
but only two of them must be given non-default values :

- 'shape': this is the path ('.' separated) to the module defining the shape. The
  actual name of the shape is specified after a colon (':'). As mentioned above
  the path of all parent |Shapes| is preprended to this path.
- 'view': this identic to the shape attribute but used for the view definition.
  Once again the path of all parent |Shapes| is preprended to this path.
- 'metadata': Any additional informations about the shape. Those should be
  specified as a dictionary.

This is it. Now when starting Exopy your new shape should be listed.


Creating a new sequence
------------------------

Creating a new sequence is very similar to creating a new shape and the same
three steps exists :

- first the sequence itself which holds the logic must be created.
- to allow a user to correctly parametrize the sequence one view should also be
  created.
- finally the sequence must be declared in the manifest of the plugin
  contributing it.


Minimal methods to implement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The sequence should be a subclass either of |BaseSequence| or |AbstractSequence|.
The second case is reserved to cases where a higher level of control over the
children item is required which should be quite uncommon.

The declaration of parameters is similar to the one used for shape. If the
sequence wish to share a computed value with the other items, it should set the
value of the **linkable_vars** member.

.. code-block:: python

    from numbers import Real

    from atom.api import Str, Int
    from exopy_pulses.pulses.api import Feval

    class MySequence(BaseSequence):
        """MySequence description.

        Use Numpy style docstrings.

        """
        #: my_int description
        my_int = Int(1).tag(pref=True)  # Integer with a default value of 1

        #: my_text description
        my_val = Str().tag(pref=True, feval=Feval(store_global=True))

        linkable_vars = set_default(['my_val'])

Sequences should at least implement the following method :

- **simplify_sequence**: this method should a return a list of items that the
  context declares it can handle as declared in its **supported_sequences**
  member (pulses are implicitely handled).


Creating the view(s)
^^^^^^^^^^^^^^^^^^^^

Just like for a shape, you need to provide a widget to edit the sequence
parameters. The view should subclass either |BaseSequenceView| or |AbstractSequenceView|.
|AbstractSequenceView| is pretty muchh bare, while |BaseSequenceView| handle the display
of the child items, the edition of the local variables and the possibility to fix
the duration of the sequence. In both cases, the view is a custom Groupbox which has a
reference to the edited sequence and to the root view which itself provide access to the
core plugin and several useful methods.

.. code-block:: enaml

enamldef MySequenceView(BaseSequenceView):

    constraints << ([vbox(hbox(t_bool, cond_lab, cond_val),
                          hbox(*t_def.items), nb)]
                    if t_def.condition else
                    [vbox(hbox(t_bool, cond_lab, cond_val), nb)])

    Label: cond_lab:
        text = 'Condition'
    QtLineCompleter: cond_val:
        text := item.condition
        entries_updater = item.get_accessible_vars
        tool_tip = EVALUATER_TOOLTIP


Registering your sequence
^^^^^^^^^^^^^^^^^^^^^^^^^

Registering a sequence is quite similar to registering a shape.

Let's say we need to declare a sequence named *MySequence*. The name of our
extension package (see the glossary section in Exopy documentation) is 'my_exopy_plugin'.
Let's look at the example below:

.. code-block:: enaml

    enamldef MyPluginManifest(PluginManifest):

        id = 'my_plugin_id'

        Extension:
            point = 'exopy.pulses.sequences'

            Sequences:
                path = 'my_exopy_plugin'

                Sequence:
                    sequence = 'my_sequence:MySequence'
                    view = 'views.my_sequence:MyView'


We declare a single child for the extension a |Sequences| object. |Sequences| does
nothing by themselves they are simply container for grouping sequences declarations.
They have a single attribute:

- 'path': when declaring a sequence you must specify in which module it is defined
  as a '.' sperated path. When declaring a path in a |Sequences| it will be
  prepended to any path-like declaration in all children.

We then declare our sequence using a |Sequence| object. A |Sequence| has three attributes
but only two of them must be given non-default values :

- 'sequence': this is the path ('.' separated) to the module defining the sequence. The
  actual name of the sequence is specified after a colon (':'). As mentioned above
  the path of all parent |Sequences| is preprended to this path.
- 'view': this identic to the sequence attribute but used for the view definition.
  Once again the path of all parent |Sequences| is preprended to this path.
- 'metadata': Any additional informations about the sequence. Those should be
  specified as a dictionary.

This is it. Now when starting Exopy your new sequence should be listed.

.. _dev_tasks_new_filter:

Creating your own sequence filter
---------------------------------

As the number of sequences available in Exopy grows, finding the sequence you need might
become a bit tedious. To make searching through tasks easier Exopy can filter
the sequences from which to choose from. A number a basic filters are built-in but
one can easily add more.

To add a new filter you simply need to contribute a |SequenceFilter| to the
'exopy.pulses.filters' extension point, as in the following example :

.. code-block:: enaml

    enamldef MyPluginManifest(PluginManifest):

        id = 'my_plugin_id'

        Extension:
            point = 'exopy.pulses.filters'

            SequenceFilter:
                id = 'MySequenceFilter'
                filter_tasks => (sequences, templates):
                    return sorted(sequences)[::2]

A filter need a unique *id* (basically its name) and a method to filter through
sequences. This method receives two dictionaries: the first ones contains the known
sequences and their associated infos, the second the templates names and their
path. Here we override the *filter_tasks* method, we could also have used one of
the following specialized filters:

- |SubclassSequenceFilter|: filter the sequences (exclude the templates) looking for
  a common subclass (declared in the *subclass* attribute)
- |MetadataSequenceFilter|: filter the sequences (exclude the templates) based on the
  value of a metadata (*meta_key* is the metadata entry to look for,
  *meta_value* the value looked for).


Creating your own sequence configurer
--------------------------------------

In some cases, the default way to configure a sequence before inserting it in a
sequence hierarchy (ie simply specifying its name) is not enough. The sequence
configurers exist to make possible to customize the creation of a new sequence.
Creating one is once again similar to creating a new shape.

.. note::

    Sequence configurers are not meant to fully parametrize a sequence, the sequence view
    is already there for that purpose. It is rather meant to provide essential
    informations necessary before including the sequence in a hierarchy or
    parameters not meant to change afterwards.

.. note::

    When a sequence configurer is specified for a sequence it is by default used form
    all its subclasses too.

Minimal methods to implement
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

All sequence configurers need to inherit from |AbstractConfig|, which defines the
expected interface of all configurers. When creating a new configurer two
methods need to be overwritten :

- build_sequence : this method is supposed to return when called a new instance of
  the sequence being configured correctly initialized. The configurer holds a
  refrence to the class of the sequence it is configuring.

- check_parameters : this method should set the *ready* flag to *True* if all
  the parameters required by the configurer have been provided and *False*
  otherwise. It should be called each time the value of a parameter change
  (using a *_post_settattr_\** method).

.. code-block:: python

    class MySequenceConfig(AbstractConfig):
        """Config for MySequence.

        """
        #: My parameter description
        parameter = Int()

        def check_parameters(self):
            """Ensure that parameter is positive and task has a name.

            """
            self.ready = self.parameter

        def build_task(self):
            """Build an instance of MySequence.

            """
            return self.sequence_class(parameter=self.parameter)

        def _post_setattr_parameter(self, old, new):
            """Check parameters each time parameter is updated.

            """
            self.check_parameters()

Creating the view
^^^^^^^^^^^^^^^^^

Just like for tasks and interfaces, you need to create a custom widget to
allow the user to parametrize the configurer. Your widget should inherit from
|AbstractConfigView|. This widget is simple container with a reference to the
configurer being edited (**model**)

Declaring the configurer
^^^^^^^^^^^^^^^^^^^^^^^^

Finally you must declare the config in a manifest by contributing an
extension to the 'exopy.pulses.configs' extension point. This is identical to
how shapes are declared but relies on the |SequenceConfigs| (instead of |Shapes|) and
|SequenceConfig| (instead of |Shape|) objects. The base sequence class for which the
configurer is meant should be returned by the get_sequence_class method.
