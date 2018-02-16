# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright 2015-2018 by ExopyPulses Authors, see AUTHORS for more details.
#
# Distributed under the terms of the BSD license.
#
# The full license is in the file LICENCE, distributed with this software.
# -----------------------------------------------------------------------------
"""Extension package for the Exopy application.

"""


def list_manifests():
    """List the manifest that should be regsitered when the main Exopy app is
    started.

    """
    import enaml
    with enaml.imports():
        from .pulses.manifest import PulsesManagerManifest
        from .tasks.manifest import PulsesTasksManifest
        from .measurement.manifest import PulsesMeasurementManifest
    return [PulsesManagerManifest, PulsesTasksManifest,
            PulsesMeasurementManifest]
