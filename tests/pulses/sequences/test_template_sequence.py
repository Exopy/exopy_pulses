# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Test the templates sequences functionalities.

"""
import pytest

from exopy_pulses.pulses.sequences.base_sequences import RootSequence
from exopy_pulses.pulses.sequences.template_sequence import TemplateSequence

from exopy_pulses.testing.context import TestContext

pytestmark = pytest.mark.skipif('True')


@pytest.fixture
def template_preferences(pulses_plugin, template_sequence):
    """Preferences corresponding to the template sequence.

    """
    infos = pulses_plugin.get_item_infos(template_sequence)
    return infos.metadata['template-config']


@pytest.fixture
def template_depependencies(pulses_plugin, template_preferences):
    """Collect the build dependency of the template_sequence.

    """
    workbench = pulses_plugin.workbench
    core = workbench.get_plugin('enaml.workbench.core')
    cmd = 'exopy.app.dependencies.analyse'
    dep_analysis = core.invoke_command(cmd, {'obj': template_preferences})
    cmd = 'exopy.app.dependencies.collect'
    dep = core.invoke_command(cmd, {'kind': 'build',
                                    'dependencies': dep_analysis.dependencies})
    dep = dep.dependencies
    dep[''] = {'': template_preferences}
    return dep


def root_with_template(template_sequence, template_dependencies):
    """Build a root using the template sequence.

    """
    root = RootSequence()
    root.context = TestContext(sampling=0.5)

    conf = {'template_id': template_sequence, 'name': 'Template',
            'template_vars': "{'b': '19'}"}
    seq = TemplateSequence.build_from_config(conf, template_dependencies)
    seq.context.channel_mapping = {'A': 'Ch1_L', 'B': 'Ch2_L',
                                   'Ch1': 'Ch2_A', 'Ch2': 'Ch1_A'}
    seq.def_1 = '1.0'
    seq.def_2 = '20.0'

    root.add_child_item(0, seq)
    return root


def test_build_from_config1(template_sequence, template_dependencies):
    """ Test building a template sequence from only the template file.

    No information is knwon about channel mapping of template_vars values

    """
    conf = {'template_id': template_sequence, 'name': 'Template',
            'template_vars': "{'b': '19', 'c': ''}"}
    seq = TemplateSequence.build_from_config(conf, template_dependencies)

    assert seq.name == 'Template'
    assert seq.template_id == template_sequence
    assert seq.template_vars == dict(b='19')
    assert seq.local_vars == dict(a='1.5')
    assert len(seq.items) == 4
    assert seq.items[3].index == 5
    assert seq.docs == 'Basic user comment\nff'

    context = seq.context
    assert context.template is seq
    assert context.logical_channels == ['A', 'B']
    assert context.analogical_channels == ['Ch1', 'Ch2']
    assert context.channel_mapping == {'A': '', 'B': '', 'Ch1': '',
                                       'Ch2': ''}


def test_build_from_config2(template_sequence, template_dependencies):
    """ Test rebuilding a sequence including a template sequence.

    Channel mapping of template_vars values are known.

    """
    conf = {'template_id': 'test', 'name': 'Template',
            'template_vars': "{'b': '25'}"}
    seq = TemplateSequence.build_from_config(conf, template_dependencies)
    seq.context.channel_mapping = {'A': 'Ch1_L', 'B': 'Ch2_L',
                                   'Ch1': 'Ch2_A', 'Ch2': 'Ch1_A'}
    root = RootSequence()
    context = TestContext(sampling=0.5)
    root.context = context
    root.add_child_item(0, seq)
    pref = root.preferences_from_members()

    new = RootSequence.build_from_config(pref, template_dependencies)
    assert new.items[0].index == 1

    seq = new.items[0]
    assert seq.name == 'Template'
    assert seq.template_id == template_sequence
    assert seq.template_vars == dict(b='25')
    assert seq.local_vars == dict(a='1.5')
    assert len(seq.items) == 4
    assert seq.items[3].index == 5
    assert seq.docs == 'Basic user comment\nff'

    context = seq.context
    assert context.template is seq
    assert context.logical_channels == ['A', 'B']
    assert context.analogical_channels == ['Ch1', 'Ch2']
    assert context.channel_mapping == {'A': 'Ch1_L', 'B': 'Ch2_L',
                                       'Ch1': 'Ch2_A', 'Ch2': 'Ch1_A'}


def test_build_from_config3(template_sequence, template_dependencies):
    """Test rebuilding a sequence including twice the same template sequence

    """
    conf = {'template_id': template_sequence, 'name': 'Template',
            'template_vars': "{'b': '19'}"}
    seq = TemplateSequence.build_from_config(conf, template_dependencies)
    seq.context.channel_mapping = {'A': 'Ch1_L', 'B': 'Ch2_L',
                                   'Ch1': 'Ch2_A', 'Ch2': 'Ch1_A'}

    conf = {'template_id': 'test', 'name': 'Template',
            'template_vars': "{'b': '12'}"}
    seq2 = TemplateSequence.build_from_config(conf, template_dependencies)
    seq2.context.channel_mapping = {'A': 'Ch1_L', 'B': 'Ch2_L',
                                    'Ch1': 'Ch1_A', 'Ch2': 'Ch2_A'}

    root = RootSequence()
    context = TestContext(sampling=0.5)
    root.context = context
    root.add_child_item(0, seq)
    root.add_child_item(0, seq2)
    pref = root.preferences_from_members()

    new = RootSequence.build_from_config(pref, template_dependencies)
    assert new.items[0].index == 1

    seq = new.items[0]
    assert seq.name == 'Template'
    assert seq.template_id == template_sequence
    assert seq.template_vars == dict(b='19')
    assert seq.local_vars == dict(a='1.5')
    assert len(seq.items) == 4
    assert seq.items[3].index == 5
    assert seq.docs == 'Basic user comment\nff'

    context = seq.context
    assert context.template == seq
    assert context.logical_channels == ['A', 'B']
    assert context.analogical_channel == ['Ch1', 'Ch2']
    assert context.channel_mapping == {'A': 'Ch1_L', 'B': 'Ch2_L',
                                       'Ch1': 'Ch2_A', 'Ch2': 'Ch1_A'}

    assert new.items[1].index == 2

    seq = new.items[1]
    assert seq.name == 'Template'
    assert seq.template_id == 'test'
    assert seq.template_vars == dict(b='12')
    assert seq.local_vars == dict(a='1.5')
    assert len(seq.items) == 4
    assert seq.items[3].index == 5
    assert seq.docs == 'Basic user comment\nff'

    context = seq.context
    assert context.template == seq
    assert context.logical_channels == ['A', 'B']
    assert context.analogical_channels == ['Ch1', 'Ch2']
    assert context.channel_mapping == {'A': 'Ch1_L', 'B': 'Ch2_L',
                                       'Ch1': 'Ch1_A', 'Ch2': 'Ch2_A'}


def test_sequence_compilation1(root_with_template):
    """Test evaluating and simplifying  a template when everything is ok.

    """
    res, missings, errors = root_with_template.evaluate_sequence()
    pulses = root_with_template.simplify_sequence()

    assert res, errors
    assert len(pulses) == 4

    pulse = pulses[0]
    assert pulse.index == 1
    assert pulse.start == 2.0
    assert pulse.stop == 2.5
    assert pulse.duration == 0.5
    assert pulse.channel == 'Ch1_L'

    pulse = pulses[1]
    assert pulse.index == 2
    assert pulse.start == 3.5
    assert pulse.stop == 4
    assert pulse.duration == 0.5
    assert pulse.channel == 'Ch2_L'

    pulse = pulses[2]
    assert pulse.index == 4
    assert pulse.start == 4.5
    assert pulse.stop == 20
    assert pulse.duration == 15.5
    assert pulse.channel == 'Ch1_A'

    pulse = pulses[3]
    assert pulse.index == 5
    assert pulse.start == 4.5
    assert pulse.stop == 20
    assert pulse.duration == 15.5
    assert pulse.channel == 'Ch2_A'


def test_sequence_compilation2(root_with_template):
    """Test compiling a template : issue in context, incomplete mapping.

    """
    template = root_with_template.items[0]
    template.context.channel_mapping = {'A': 'Ch1_L', 'B': 'Ch2_L',
                                        'Ch1': 'Ch2_A'}

    res, miss, errors = root_with_template.evaluate_sequence()

    assert not res
    assert not miss
    assert 'Template-context' in errors
    assert 'Ch2' in errors['Template-context']


def test_sequence_compilation3(root_with_template):
    """Test compiling a template : issue in context, erroneous mapping.

    """
    template = root_with_template.items[0]
    template.context.channel_mapping = {'A': 'Ch1_L', 'B': 'Ch2_L',
                                        'Ch1': 'Ch2_A', 'Ch2': 'A'}

    res, miss, errors = root_with_template.evaluate_sequence()

    assert not res
    assert not miss
    assert 'Template-context' in errors
    assert 'Ch2' in errors['Template-context']


def test_sequence_compilation3bis(root_with_template):
    """Test compiling a template : pulse as umapped channel.

    """
    template = root_with_template.items[0]
    template.items[0].channel = '__'
    res, miss, errors = root_with_template.evaluate_sequence(False)

    assert not res
    assert not miss
    assert 'Template-channels' in errors
    assert '__' in errors['Template-channels']


def test_sequence_compilation4(root_with_template):
    """Test compiling a template : issue in defs.

    """
    template = root_with_template.items[0]
    template.def_1 = 'r*'

    res, miss, errors = root_with_template.evaluate_sequence()

    assert not res
    assert not miss
    assert '1_start' in errors


def test_sequence_compilation5(root_with_template):
    """Test compiling a template : issue in template_vars.

    """
    template = root_with_template.items[0]
    template.template_vars = {'b': '*1'}

    res, miss, errors = root_with_template.compile_sequence(False)

    assert not res
    assert '1_b' in errors


def test_sequence_compilation6(root_with_template):
    """Test compiling a template : issue in local_vars.

    """
    template = root_with_template.items[0]
    template.local_vars = {'a': '*1'}

    res, miss, errors = root_with_template.evaluate_sequence()

    assert not res
    assert '1_a' in errors


def test_sequence_compilation7(root_with_template):
    """Test compiling a template : issue in stop time.

    """
    template = root_with_template.items[0]
    template.items[0].def_2 = '200'

    res, miss, errors = root_with_template.compile_sequence(False)

    assert not res
    assert 'Template-stop' in errors
