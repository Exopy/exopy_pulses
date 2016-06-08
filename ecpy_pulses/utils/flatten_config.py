# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Function taken from HQCMeas/utils/configobj_ops.py

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


from collections import defaultdict


def flatten_config(config, entries):
    """ Gather entries from a configbj in sets.

    Parameters
    ----------
    config : Section
        Section from which the values of some entries should be extracted.

    entries : list(str)
        The list of entries to look for in the configobj.

    Returns
    -------
    results : dict(str: set)
        Dict containing the values of the entries as sets. This dict can then
        be used to gather function and or classes needed when rebuilding.

    """
    results = defaultdict(set)
    for entry in entries:
        # Make sure that all entries exists in the dict.
        if entry in config.scalars:
            results[entry].add(config[entry])

    for section in config.sections:
        aux = flatten_config(config[section], entries)
        for key in aux:
            results[key].update(aux[key])

    return results
