# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""
"""
from configobj import ConfigObj
from textwrap import wrap


def load_sequence_prefs(path):
    """ Load the preferences of a sequence stored in a file.

    Parameters
    ----------
        path : unicode
            Location of the template file.

    Returns
    -------
        prefs : ConfigObj
            The data needed to rebuild the tasks.

        doc : str
            The doc of the template.

    """
    config = ConfigObj(path)
    doc = ''
    if config.initial_comment:
        doc_list = [com[1:].strip() for com in config.initial_comment]
        doc = '\n'.join(doc_list)

    return config, doc


def load_sequence_prefs_dict(path):
    """ Load the preferences of a sequence stored in a file.

    Parameters
    ----------
        path : unicode
            Location of the template file.

    Returns
    -------
        dict: {config:, doc:} where prefs is the data
               needed to rebuild the task and doc
               is the doc of the template
    """
    config = ConfigObj(path)
    doc = ''
    if config.initial_comment:
        doc_list = [com[1:].strip() for com in config.initial_comment]
        doc = '\n'.join(doc_list)

    return {'config': config, 'doc': doc}


def save_sequence_prefs(path, prefs, doc=''):
    """ Save a sequence to a file

    Parameters
    ----------
        path : unicode
            Path of the file to which save the template
        prefs : dict(str : str)
            Dictionnary containing the template parameters
        doc : str
            The template doc

    """
    # Create an empty ConfigObj and set filename after so that the data are
    # not loaded. Otherwise merge might lead to corrupted data.
    config = ConfigObj(indent_type='    ')
    config.filename = path
    config.merge(prefs)
    if doc:
        config.initial_comment = wrap(doc, 79)

    config.write()
