# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test of the functionality of items, shapes and contexts declarators.

"""
import pytest
import enaml
from atom.api import Atom, Dict, List

from exopy_pulses.pulses.infos import (SequenceInfos, ShapeInfos,
                                       ContextInfos)
from exopy_pulses.pulses.declarations import (Sequences, Sequence,
                                              Shapes, Shape,
                                              SequenceConfigs, SequenceConfig,
                                              Contexts, Context)


class _DummyCollector(Atom):

    contributions = Dict()

    _delayed = List()


@pytest.fixture
def collector():
    return _DummyCollector()


# =============================================================================
# --- Test sequences ----------------------------------------------------------
# =============================================================================

@pytest.fixture
def sequence_decl():
    root = 'exopy_pulses.pulses.sequences.'
    return Sequence(sequence=root + 'base_sequences:BaseSequence',
                    view=root + 'views.base_sequences_views:BaseSequenceView')


def test_register_sequence_decl1(collector, sequence_decl):
    """Test registering the base sequence.

    """
    parent = Sequences(group='test', path='exopy_pulses.pulses.sequences')
    parent.insert_children(None, [sequence_decl])
    sequence_decl.sequence = 'base_sequences:BaseSequence'
    sequence_decl.view = 'views.base_sequences_views:BaseSequenceView'
    parent.register(collector, {})
    infos = collector.contributions['exopy_pulses.BaseSequence']
    from exopy_pulses.pulses.sequences.base_sequences import BaseSequence
    with enaml.imports():
        from exopy_pulses.pulses.sequences.views.base_sequences_views\
            import BaseSequenceView
    assert infos.cls is BaseSequence
    assert infos.view is BaseSequenceView
    assert infos.metadata['group'] == 'test'


def test_register_sequence_decl_extend1(collector, sequence_decl):
    """Test extending a sequence.

    """
    collector.contributions['exopy_pulses.Sequence'] = SequenceInfos()
    sequence_decl.sequence = 'exopy_pulses.Sequence'
    sequence_decl.metadata = {'test': True}
    sequence_decl.register(collector, {})
    infos = collector.contributions['exopy_pulses.Sequence']
    assert 'test' in infos.metadata


def test_register_sequence_decl_extend2(collector, sequence_decl):
    """Test extending a yet to be defined sequence.

    """
    sequence_decl.sequence = 'exopy_pulses.Sequence'
    sequence_decl.register(collector, {})
    assert collector._delayed == [sequence_decl]


def test_register_sequence_decl_path_1(collector, sequence_decl):
    """Test handling wrong path : missing ':'.

    Such an errors can't be detected till the pass on the delayed and the
    dead-end is detected.

    """
    tb = {}
    sequence_decl.sequence = 'exopy_pulses.sequence'
    sequence_decl.register(collector, tb)
    assert sequence_decl in collector._delayed


def test_register_sequence_decl_path2(collector, sequence_decl):
    """Test handling wrong path : too many ':'.

    """
    tb = {}
    sequence_decl.view = 'exopy_pulses.sequences:sequences:Sequence'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.BaseSequence' in tb


def test_register_sequence_decl_duplicate1(collector, sequence_decl):
    """Test handling duplicate : in collector.

    """
    collector.contributions['exopy_pulses.BaseSequence'] = None
    tb = {}
    sequence_decl.sequence = 'exopy_pulses.pulses:BaseSequence'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.BaseSequence_duplicate1' in tb


def test_register_sequence_decl_duplicate2(collector, sequence_decl):
    """Test handling duplicate : in traceback.

    """
    tb = {'exopy_pulses.BaseSequence': 'rr'}
    sequence_decl.sequence = 'exopy_pulses.pulses:BaseSequence'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.BaseSequence_duplicate1' in tb


def test_register_sequence_decl_cls1(collector, sequence_decl):
    """Test handling sequence class issues : failed import no such module.

    """
    tb = {}
    sequence_decl.sequence = 'exopy_pulses.foo:BaseSequence'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.BaseSequence' in tb
    assert 'import' in tb['exopy_pulses.BaseSequence']


def test_register_sequence_decl_cls1_bis(collector, sequence_decl):
    """Test handling sequence class issues : failed import error while
    importing.

    """
    tb = {}
    sequence_decl.sequence = 'exopy.testing.broken_module:Sequence'
    sequence_decl.register(collector, tb)
    assert 'exopy.Sequence' in tb and 'NameError' in tb['exopy.Sequence']


def test_register_sequence_decl_cls2(collector, sequence_decl):
    """Test handling sequence class issues : undefined in module.

    """
    tb = {}
    sequence_decl.sequence =\
        'exopy_pulses.pulses.sequences.base_sequences:Task'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.Task' in tb and 'attribute' in tb['exopy_pulses.Task']


def test_register_sequence_decl_cls3(collector, sequence_decl):
    """Test handling sequence class issues : wrong type.

    """
    tb = {}
    sequence_decl.sequence = 'exopy.tasks.tasks.database:TaskDatabase'
    sequence_decl.register(collector, tb)
    assert ('exopy.TaskDatabase' in tb and
            'subclass' in tb['exopy.TaskDatabase'])


def test_register_sequence_decl_view1(collector, sequence_decl):
    """Test handling view issues : failed import no such module.

    """
    tb = {}
    sequence_decl.view = 'exopy.tasks.foo:Task'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.BaseSequence' in tb
    assert'import' in tb['exopy_pulses.BaseSequence']


def test_register_sequence_decl_view1_bis(collector, sequence_decl):
    """Test handling view issues : failed import error while importing.

    """
    tb = {}
    sequence_decl.view = 'exopy.testing.broken_enaml:Task'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.BaseSequence' in tb
    assert ('AttributeError' in tb['exopy_pulses.BaseSequence'] or
            'NameError' in tb['exopy_pulses.BaseSequence'])


def test_register_sequence_decl_view2(collector, sequence_decl):
    """Test handling view issues : undefined in module.

    """
    tb = {}
    sequence_decl.view = 'exopy.tasks.tasks.base_views:Task'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.BaseSequence' in tb
    assert 'import' in tb['exopy_pulses.BaseSequence']


def test_register_sequence_decl_view3(collector, sequence_decl):
    """Test handling view issues : wrong type.

    """
    tb = {}
    sequence_decl.view = 'exopy.tasks.tasks.database:TaskDatabase'
    sequence_decl.register(collector, tb)
    assert 'exopy_pulses.BaseSequence' in tb
    assert 'subclass' in tb['exopy_pulses.BaseSequence']


def test_unregister_sequence_decl1(collector, sequence_decl):
    """Test unregistering a sequence.

    """
    sequence_decl.register(collector, {})
    sequence_decl.unregister(collector)
    assert not collector.contributions


def test_unregister_sequence_decl2(collector, sequence_decl):
    """Test unregistering a sequence which already disappeared.

    """
    sequence_decl.register(collector, {})
    collector.contributions = {}
    sequence_decl.unregister(collector)
    # Would raise an error if the error was not properly catched.


def test_unregister_sequence_decl3(collector, sequence_decl):
    """Test unregistering a sequence extending an existing one.

    """
    collector.contributions['exopy_pulses.BaseSequence'] = SequenceInfos()
    sequence_decl.sequence = 'exopy_pulses.BaseSequence'
    sequence_decl.metadata = {'test': True}
    sequence_decl.register(collector, {})
    sequence_decl.unregister(collector)
    assert not collector.contributions['exopy_pulses.BaseSequence'].metadata


def test_str_sequence(sequence_decl):
    """Test string representation.

    """
    str(sequence_decl)


# =============================================================================
# --- Test shapes ------------------------------------------------------------
# =============================================================================

@pytest.fixture
def shape_decl():
    root = 'exopy_pulses.pulses.shapes.'
    return Shape(shape=root + 'square_shape:SquareShape',
                 view=root + 'views.square_shape_view:SquareShapeView')


def test_register_shape_decl1(collector, shape_decl):
    """Test registering the base sequence.

    """
    parent = Shapes(group='test', path='exopy_pulses.pulses.shapes')
    parent.insert_children(None, [shape_decl])
    shape_decl.shape = 'square_shape:SquareShape'
    shape_decl.view = 'views.square_shape_view:SquareShapeView'
    parent.register(collector, {})
    infos = collector.contributions['exopy_pulses.SquareShape']
    from exopy_pulses.pulses.shapes.square_shape import SquareShape
    with enaml.imports():
        from exopy_pulses.pulses.shapes.views.square_shape_view\
            import SquareShapeView
    assert infos.cls is SquareShape
    assert infos.view is SquareShapeView
    assert infos.metadata['group'] == 'test'


def test_register_shape_decl_extend1(collector, shape_decl):
    """Test extending a sequence.

    """
    collector.contributions['exopy_pulses.Shape'] = ShapeInfos()
    shape_decl.shape = 'exopy_pulses.Shape'
    shape_decl.metadata = {'test': True}
    shape_decl.register(collector, {})
    infos = collector.contributions['exopy_pulses.Shape']
    assert 'test' in infos.metadata


def test_register_shape_decl_extend2(collector, shape_decl):
    """Test extending a yet to be defined sequence.

    """
    shape_decl.shape = 'exopy_pulses.Shape'
    shape_decl.register(collector, {})
    assert collector._delayed == [shape_decl]


def test_register_shape_decl_path_1(collector, shape_decl):
    """Test handling wrong path : missing ':'.

    Such an errors can't be detected till the pass on the delayed and the
    dead-end is detected.

    """
    tb = {}
    shape_decl.shape = 'exopy_pulses.shape'
    shape_decl.register(collector, tb)
    assert shape_decl in collector._delayed


def test_register_shape_decl_path2(collector, shape_decl):
    """Test handling wrong path : too many ':'.

    """
    tb = {}
    shape_decl.view = 'exopy_pulses.shapes:shapes:Shape'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.SquareShape' in tb


def test_register_shape_decl_duplicate1(collector, shape_decl):
    """Test handling duplicate : in collector.

    """
    collector.contributions['exopy_pulses.SquareShape'] = None
    tb = {}
    shape_decl.shape = 'exopy_pulses.pulses:SquareShape'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.SquareShape_duplicate1' in tb


def test_register_shape_decl_duplicate2(collector, shape_decl):
    """Test handling duplicate : in traceback.

    """
    tb = {'exopy_pulses.SquareShape': 'rr'}
    shape_decl.shape = 'exopy_pulses.pulses:SquareShape'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.SquareShape_duplicate1' in tb


def test_register_shape_decl_cls1(collector, shape_decl):
    """Test handling sequence class issues : failed import no such module.

    """
    tb = {}
    shape_decl.shape = 'exopy_pulses.foo:SquareShape'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.SquareShape' in tb
    assert 'import' in tb['exopy_pulses.SquareShape']


def test_register_shape_decl_cls1_bis(collector, shape_decl):
    """Test handling sequence class issues : failed import error while
    importing.

    """
    tb = {}
    shape_decl.shape = 'exopy.testing.broken_module:SquareShape'
    shape_decl.register(collector, tb)
    assert 'exopy.SquareShape' in tb and 'NameError' in tb['exopy.SquareShape']


def test_register_shape_decl_cls2(collector, shape_decl):
    """Test handling sequence class issues : undefined in module.

    """
    tb = {}
    shape_decl.shape = 'exopy_pulses.pulses.shapes.base_shape:Task'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.Task' in tb and 'attribute' in tb['exopy_pulses.Task']


def test_register_shape_decl_cls3(collector, shape_decl):
    """Test handling sequence class issues : wrong type.

    """
    tb = {}
    shape_decl.shape = 'exopy.tasks.tasks.database:TaskDatabase'
    shape_decl.register(collector, tb)
    assert ('exopy.TaskDatabase' in tb and
            'subclass' in tb['exopy.TaskDatabase'])


def test_register_shape_decl_view1(collector, shape_decl):
    """Test handling view issues : failed import no such module.

    """
    tb = {}
    shape_decl.view = 'exopy.tasks.foo:Task'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.SquareShape' in tb
    assert'import' in tb['exopy_pulses.SquareShape']


def test_register_shape_decl_view1_bis(collector, shape_decl):
    """Test handling view issues : failed import error while importing.

    """
    tb = {}
    shape_decl.view = 'exopy.testing.broken_enaml:Task'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.SquareShape' in tb
    assert ('AttributeError' in tb['exopy_pulses.SquareShape'] or
            'NameError' in tb['exopy_pulses.SquareShape'])


def test_register_shape_decl_view2(collector, shape_decl):
    """Test handling view issues : undefined in module.

    """
    tb = {}
    shape_decl.view = 'exopy.tasks.tasks.base_views:Task'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.SquareShape' in tb
    assert 'import' in tb['exopy_pulses.SquareShape']


def test_register_shape_decl_view3(collector, shape_decl):
    """Test handling view issues : wrong type.

    """
    tb = {}
    shape_decl.view = 'exopy.tasks.tasks.database:TaskDatabase'
    shape_decl.register(collector, tb)
    assert 'exopy_pulses.SquareShape' in tb
    assert 'subclass' in tb['exopy_pulses.SquareShape']


def test_unregister_shape_decl1(collector, shape_decl):
    """Test unregistering a sequence.

    """
    shape_decl.register(collector, {})
    shape_decl.unregister(collector)
    assert not collector.contributions


def test_unregister_shape_decl2(collector, shape_decl):
    """Test unregistering a sequence which already disappeared.

    """
    shape_decl.register(collector, {})
    collector.contributions = {}
    shape_decl.unregister(collector)
    # Would raise an error if the error was not properly catched.


def test_unregister_shape_decl3(collector, shape_decl):
    """Test unregistering a sequence extending an existing one.

    """
    collector.contributions['exopy_pulses.SquareShape'] = ShapeInfos()
    shape_decl.shape = 'exopy_pulses.SquareShape'
    shape_decl.metadata = {'test': True}
    shape_decl.register(collector, {})
    shape_decl.unregister(collector)
    assert not collector.contributions['exopy_pulses.SquareShape'].metadata


def test_str_shape(shape_decl):
    """Test string representation.

    """
    str(shape_decl)


# =============================================================================
# --- Test contexts -----------------------------------------------------------
# =============================================================================

@pytest.fixture
def context_decl():
    root = 'exopy_pulses.pulses.contexts.'
    return Context(context=root + 'base_context:BaseContext',
                   view=root + 'views.base_context_view:BaseContextView')


def test_register_context_decl1(collector, context_decl):
    """Test registering the base context.

    """
    parent = Contexts(group='test', path='exopy_pulses.pulses.contexts')
    parent.insert_children(None, [context_decl])
    context_decl.context = 'base_context:BaseContext'
    context_decl.view = 'views.base_context_view:BaseContextView'
    context_decl.metadata = {'test': True}
    context_decl.instruments = ['exopy.Legacy.TektronixAWG5014B']
    parent.register(collector, {})
    infos = collector.contributions['exopy_pulses.BaseContext']
    from exopy_pulses.pulses.contexts.base_context import BaseContext
    with enaml.imports():
        from exopy_pulses.pulses.contexts.views.base_context_view\
            import BaseContextView
    assert infos.cls is BaseContext
    assert infos.view is BaseContextView
    assert infos.metadata['group'] == 'test'
    assert infos.instruments


def test_register_context_decl_extend1(collector, context_decl):
    """Test extending a context.

    """
    infos = ContextInfos(metadata={'test2': False},
                         instruments=['exopy.Legacy.TektronixAWG5014B'])
    collector.contributions['exopy_pulses.Context'] = infos
    context_decl.context = 'exopy_pulses.Context'
    context_decl.metadata = {'test': True}
    context_decl.instruments = ['exopy.i3py.TektronixAWG5014B']
    context_decl.register(collector, {})
    infos = collector.contributions['exopy_pulses.Context']
    assert len(infos.metadata) == 2
    assert 'test' in infos.metadata
    assert len(infos.instruments) == 2


def test_register_context_decl_extend2(collector, context_decl):
    """Test extending a yet to be defined context.

    """
    context_decl.context = 'exopy_pulses.Context'
    context_decl.register(collector, {})
    assert collector._delayed == [context_decl]


def test_register_context_decl_path_1(collector, context_decl):
    """Test handling wrong path : missing ':'.

    Such an errors can't be detected till the pass on the delayed and the
    dead-end is detected.

    """
    tb = {}
    context_decl.context = 'exopy_pulses.context'
    context_decl.register(collector, tb)
    assert context_decl in collector._delayed


def test_register_context_decl_path2(collector, context_decl):
    """Test handling wrong path : too many ':'.

    """
    tb = {}
    context_decl.view = 'exopy_pulses.sequences:sequences:Context'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.BaseContext' in tb


def test_register_context_decl_duplicate1(collector, context_decl):
    """Test handling duplicate : in collector.

    """
    collector.contributions['exopy_pulses.BaseContext'] = None
    tb = {}
    context_decl.context = 'exopy_pulses.pulses:BaseContext'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.BaseContext_duplicate1' in tb


def test_register_context_decl_duplicate2(collector, context_decl):
    """Test handling duplicate : in traceback.

    """
    tb = {'exopy_pulses.BaseContext': 'rr'}
    context_decl.context = 'exopy_pulses.pulses:BaseContext'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.BaseContext_duplicate1' in tb


def test_register_context_decl_cls1(collector, context_decl):
    """Test handling context class issues : failed import no such module.

    """
    tb = {}
    context_decl.context = 'exopy_pulses.foo:BaseContext'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.BaseContext' in tb
    assert 'import' in tb['exopy_pulses.BaseContext']


def test_register_context_decl_cls1_bis(collector, context_decl):
    """Test handling context class issues : failed import error while
    importing.

    """
    tb = {}
    context_decl.context = 'exopy.testing.broken_module:Context'
    context_decl.register(collector, tb)
    assert 'exopy.Context' in tb and 'NameError' in tb['exopy.Context']


def test_register_context_decl_cls2(collector, context_decl):
    """Test handling context class issues : undefined in module.

    """
    tb = {}
    context_decl.context = 'exopy_pulses.pulses.sequences.base_sequences:Task'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.Task' in tb and 'attribute' in tb['exopy_pulses.Task']


def test_register_context_decl_cls3(collector, context_decl):
    """Test handling context class issues : wrong type.

    """
    tb = {}
    context_decl.context = 'exopy.tasks.tasks.database:TaskDatabase'
    context_decl.register(collector, tb)
    assert ('exopy.TaskDatabase' in tb and
            'subclass' in tb['exopy.TaskDatabase'])


def test_register_context_decl_view1(collector, context_decl):
    """Test handling view issues : failed import no such module.

    """
    tb = {}
    context_decl.view = 'exopy.tasks.foo:Task'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.BaseContext' in tb
    assert'import' in tb['exopy_pulses.BaseContext']


def test_register_context_decl_view1_bis(collector, context_decl):
    """Test handling view issues : failed import error while importing.

    """
    tb = {}
    context_decl.view = 'exopy.testing.broken_enaml:Task'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.BaseContext' in tb
    assert ('AttributeError' in tb['exopy_pulses.BaseContext'] or
            'NameError' in tb['exopy_pulses.BaseContext'])


def test_register_context_decl_view2(collector, context_decl):
    """Test handling view issues : undefined in module.

    """
    tb = {}
    context_decl.view = 'exopy.tasks.tasks.base_views:Task'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.BaseContext' in tb
    assert 'import' in tb['exopy_pulses.BaseContext']


def test_register_context_decl_view3(collector, context_decl):
    """Test handling view issues : wrong type.

    """
    tb = {}
    context_decl.view = 'exopy.tasks.tasks.database:TaskDatabase'
    context_decl.register(collector, tb)
    assert 'exopy_pulses.BaseContext' in tb
    assert 'subclass' in tb['exopy_pulses.BaseContext']


def test_unregister_context_decl1(collector, context_decl):
    """Test unregistering a context.

    """
    context_decl.register(collector, {})
    context_decl.unregister(collector)
    assert not collector.contributions


def test_unregister_context_decl2(collector, context_decl):
    """Test unregistering a context which already disappeared.

    """
    context_decl.register(collector, {})
    collector.contributions = {}
    context_decl.unregister(collector)
    # Would raise an error if the error was not properly catched.


def test_unregister_context_decl3(collector, context_decl):
    """Test unregistering a context extending an existing one.

    """
    collector.contributions['exopy_pulses.BaseContext'] = ContextInfos()
    context_decl.context = 'exopy_pulses.BaseContext'
    context_decl.metadata = {'test': True}
    context_decl.instruments = ['exopy.i3py.TektronixAWG5014B']
    context_decl.register(collector, {})
    context_decl.unregister(collector)
    assert not collector.contributions['exopy_pulses.BaseContext'].metadata
    assert not collector.contributions['exopy_pulses.BaseContext'].instruments


def test_str_context(context_decl):
    """Test string representation.

    """
    str(context_decl)


# =============================================================================
# --- Test configs ------------------------------------------------------------
# =============================================================================

@pytest.fixture
def config_decl():
    class Config(SequenceConfig):
        def get_sequence_class(self):
            from exopy_pulses.pulses.sequences.base_sequences\
                import BaseSequence
            return BaseSequence

    root = 'exopy_pulses.pulses.configs.'

    return Config(
        config=root + 'base_config:SequenceConfig',
        view=root + 'base_config_views:SequenceConfigView')


def test_register_config_decl(collector, config_decl):
    """Test registering the sequence config.

    """
    parent = SequenceConfigs(group='test', path='exopy_pulses.pulses.configs')
    parent.insert_children(None, [config_decl])
    config_decl.config = 'base_config:SequenceConfig'
    config_decl.view = 'base_config_views:SequenceConfigView'
    errors = {}
    parent.register(collector, errors)
    from exopy_pulses.pulses.sequences.base_sequences import BaseSequence
    infos = collector.contributions[BaseSequence]
    from exopy_pulses.pulses.configs.base_config import SequenceConfig
    with enaml.imports():
        from exopy_pulses.pulses.configs.base_config_views \
            import SequenceConfigView
    assert infos.cls is SequenceConfig
    assert infos.view is SequenceConfigView


def test_register_config_fail_to_get_sequence(collector, config_decl):
    """Test handling wrong path : missing ':'.

    """
    tb = {}

    def dummy(self):
        raise Exception()
    type(config_decl).get_sequence_class = dummy
    config_decl.register(collector, tb)
    assert 'exopy_pulses.SequenceConfig' in tb


def test_register_config_decl_path_1(collector, config_decl):
    """Test handling wrong path : missing ':'.

    """
    tb = {}
    config_decl.config = 'exopy.tasks'
    config_decl.register(collector, tb)
    assert 'exopy.tasks' in tb


def test_register_config_decl_path2(collector, config_decl):
    """Test handling wrong path : too many ':'.

    """
    tb = {}
    config_decl.view = 'exopy.tasks:tasks:Task'
    config_decl.register(collector, tb)
    assert 'exopy_pulses.SequenceConfig' in tb


def test_register_config_decl_duplicate1(collector, config_decl):
    """Test handling duplicate config for a task.

    """
    from exopy_pulses.pulses.sequences.base_sequences import BaseSequence
    collector.contributions[BaseSequence] = None
    tb = {}
    config_decl.register(collector, tb)
    assert 'exopy_pulses.SequenceConfig' in tb


def test_register_config_decl_duplicate2(collector, config_decl):
    """Test handling duplicate : in traceback.

    """
    tb = {'exopy_pulses.SequenceConfig': 'rr'}
    config_decl.register(collector, tb)
    assert 'exopy_pulses.SequenceConfig_duplicate1' in tb


def test_register_config_decl_cls1(collector, config_decl):
    """Test handling task class issues : failed import wrong path.

    """
    tb = {}
    config_decl.config = 'exopy.tasks.foo:Task'
    config_decl.register(collector, tb)
    assert 'exopy.Task' in tb and 'import' in tb['exopy.Task']


def test_register_config_decl_cls1_bis(collector, config_decl):
    """Test handling task class issues : failed import NameError.

    """
    tb = {}
    config_decl.config = 'exopy.testing.broken_module:Task'
    config_decl.register(collector, tb)
    assert 'exopy.Task' in tb and 'NameError' in tb['exopy.Task']


def test_register_config_decl_cls2(collector, config_decl):
    """Test handling task class issues : undefined in module.

    """
    tb = {}
    config_decl.config = 'exopy.tasks.tasks.base_tasks:Task'
    config_decl.register(collector, tb)
    assert 'exopy.Task' in tb and 'attribute' in tb['exopy.Task']


def test_register_config_decl_cls3(collector, config_decl):
    """Test handling task class issues : wrong type.

    """
    tb = {}
    config_decl.config = 'exopy.tasks.tasks.database:TaskDatabase'
    config_decl.register(collector, tb)
    assert ('exopy.TaskDatabase' in tb and
            'subclass' in tb['exopy.TaskDatabase'])


def test_register_config_decl_view1(collector, config_decl):
    """Test handling view issues : failed import wrong path.

    """
    tb = {}
    config_decl.view = 'exopy.tasks.foo:Task'
    config_decl.register(collector, tb)
    assert 'exopy_pulses.SequenceConfig' in tb
    assert 'import' in tb['exopy_pulses.SequenceConfig']


def test_register_config_decl_view1bis(collector, config_decl):
    """Test handling view issues : failed import NameError.

    """
    tb = {}
    config_decl.view = 'exopy.testing.broken_module:Task'
    config_decl.register(collector, tb)
    assert 'exopy_pulses.SequenceConfig' in tb
    assert 'NameError' in tb['exopy_pulses.SequenceConfig']


def test_register_config_decl_view2(collector, config_decl):
    """Test handling view issues : undefined in module.

    """
    tb = {}
    config_decl.view = 'exopy.tasks.tasks.base_views:Task'
    config_decl.register(collector, tb)
    assert 'exopy_pulses.SequenceConfig' in tb
    assert 'import' in tb['exopy_pulses.SequenceConfig']


def test_register_config_decl_view3(collector, config_decl):
    """Test handling view issues : wrong type.

    """
    tb = {}
    config_decl.view = 'exopy.tasks.tasks.database:TaskDatabase'
    config_decl.register(collector, tb)
    assert 'exopy_pulses.SequenceConfig' in tb
    assert 'subclass' in tb['exopy_pulses.SequenceConfig']


def test_unregister_config_decl1(collector, config_decl):
    """Test unregistering a task.

    """
    config_decl.register(collector, {})
    config_decl.unregister(collector)
    assert not collector.contributions


def test_unregister_config_decl2(collector, config_decl):
    """Test unregistering a task which already disappeared.

    """
    config_decl.register(collector, {})
    collector.contributions = {}
    config_decl.unregister(collector)
    # Would raise an error if the error was not properly catched.


def test_str_config(config_decl):
    """Test string representation.

    """
    str(config_decl)
