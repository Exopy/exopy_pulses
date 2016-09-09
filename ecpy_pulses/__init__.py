# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2016 by EcpyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Extension package for the Ecpy application.

"""
from __future__ import (division, unicode_literals, print_function,
                        absolute_import)

import enaml

# HINT workaround a completely stupid bug in Py2
from ecpy_pulses.pulses.utils.normalizers import (normalize_sequence_name,
                                                  normalize_context_name,
                                                  normalize_shape_name)


def list_manifests():
    """List the manifest that should be regsitered when the main Ecpy app is
    started.

    """
    with enaml.imports():
        from .pulses.manifest import PulsesManagerManifest
        from .tasks.manifest import PulsesTasksManifest
        from .measure.manifest import PulsesMeasureManifest
    return [PulsesManagerManifest, PulsesTasksManifest, PulsesMeasureManifest]
