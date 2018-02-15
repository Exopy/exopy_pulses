# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Utility functions to build user-friendly names from ids.

Those should be use as formatting function argument to the ids_to_unique_names
function found in exopy.utils.transformers

"""


def _normalize(name):
    """Private normalizing function.

    Replaces '_' by spaces and add spaces between 'aA' sequences.

    """
    package = None
    if '.' in name:
        package, name = name.rsplit('.', 1)

    aux = ''
    n_len = len(name)
    for i, char in enumerate(name):
        if char == '_':
            aux += ''
            continue

        if char != '\0':
            if char.isupper() and i != 0:
                if name[i-1].islower():
                    if i+1 != n_len and name[i+1].islower():
                        aux += ' ' + char.lower()
                    else:
                        aux += ' ' + char
                else:
                    if i+1 != n_len and name[i+1].islower():
                        aux += ' ' + char.lower()
                    else:
                        aux += char
            else:
                if i == 0:
                    aux += char.upper()
                else:
                    aux += char

    return package + '.' + aux if package else aux


# TODO would be nicer with regex but I never managed to get the regex right.
def normalize_sequence_name(name):
    """Normalize sequence names.

    For sequences, strip the terminal Sequence if present, replaces '_' by
    spaces and add spaces between 'aA' sequences.
    For templates, only the extension file is removed.

    """
    if name.endswith('.temp_pulse.ini'):
        name, _, _ = name.rsplit('.', 2)
        return name.capitalize()

    if name.endswith('Sequence'):
        name = name[:-8] + '\0'

    return _normalize(name)


# TODO would be nicer with regex but I never managed to get the regex right.
def normalize_context_name(name):
    """Normalize context names.

    Strip terminal Context and replaces '_' by spaces and add spaces between
    'aA' sequences.

    """
    if name.endswith('Context'):
        name = name[:-7] + '\0'

    return _normalize(name)


# TODO would be nicer with regex but I never managed to get the regex right.
def normalize_shape_name(name):
    """Normalize shape names.

    Strip terminal Shape and replaces '_' by spaces and add spaces between
    'aA' sequences.

    """
    if name.endswith('Shape'):
        name = name[:-5] + '\0'

    return _normalize(name)
