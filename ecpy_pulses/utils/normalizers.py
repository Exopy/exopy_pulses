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
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)


# TODO would be nicer with regex but I never managed to get the regex right.
def normalize_sequence_name(name):
    """Normalize names.

    For tasks, replaces '_' by spaces and add spaces between 'aA' sequences.
    For templates, only the extension file is removed.

    """
    if name.endswith('.sequence.ini'):
        name, _, _ = name.rsplit('.', 2)
        return name.capitalize()

    if name.endswith('Sequence'):
        name = name[:-8] + '\0'

    package = None
    if '.' in name:
        package, name = name.rsplit('.', 1)

    aux = ''
    n_len = len(name)
    for i, char in enumerate(name):
        if char == '_':
            aux += ' '
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
def normalize_context_name(name):
    """Normalize names.

    For tasks, replaces '_' by spaces and add spaces between 'aA' sequences.
    For templates, only the extension file is removed.

    """
    if name.endswith('.context.ini'):
        name, _, _ = name.rsplit('.', 2)
        return name.capitalize()

    if name.endswith('Context'):
        name = name[:-7] + '\0'

    package = None
    if '.' in name:
        package, name = name.rsplit('.', 1)

    aux = ''
    for i, char in enumerate(name):
        if char == '_':
            aux += ' '
            continue

        if char != '\0':
            if char.isupper() and i != 0:
                if name[i-1].islower():
                    if name[i+1].islower():
                        aux += ' ' + char.lower()
                    else:
                        aux += ' ' + char
                elif i +1 < len(name):
                    if name[i+1].islower():
                        aux += ' ' + char.lower()
                    else:
                        aux += char
            else:
                if i == 0:
                    aux += char.upper()
                else:
                    aux += char

    return package + '.' + aux if package else aux
