#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os.path
import sys

sys.path.insert(0, os.path.abspath('.'))
from exopy_pulses.version import __version__

PROJECT_NAME = 'exopy_pulses'

setup(
    name=PROJECT_NAME,
    description='ExopyPulses plugin package',
    version=__version__,
    long_description=open('README.md').read(),
    author='see AUTHORS',
    author_email='',
    url='https://github.com/exopy/exopy_pulses',
    download_url='https://github.com/exopy/exopy_pulses/tarball/master',
    keywords='experiment automation GUI',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Physics',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    zip_safe=False,
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={'': ['*.enaml']},
    requires=['exopy', 'numpy'],
    install_requires=['exopy', 'numpy'],
    entry_points={
        'exopy_package_extension':
        'exopy_pulses = %s:list_manifests' % PROJECT_NAME}
)
