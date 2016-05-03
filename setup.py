#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os.path
import sys

sys.path.insert(0, os.path.abspath('.'))
from ecpy_ext_demo.version import __version__

PROJECT_NAME = 'ecpy_pulses'

setup(
    name=PROJECT_NAME,
    description='Ecpy pulses package',
    version=__version__,
    long_description=open('README').read(),
    author='see AUTHORS',
    author_email='',
    url='',  # URL of the git repository
    download_url='',  # URL of the zip or tar.gz master branch
    keywords='experiment automation GUI',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Physics',
        'Programming Language :: Python :: 2.7',
        ],
    zip_safe=False,
    packages=find_packages(exclude=['tests', 'tests.*']),
    package_data={'': ['*.enaml']},
    requires=['ecpy'],
    install_requires=['ecpy'],
    entry_points={
        'ecpy_package_extension':
        'ecpy_ext_demo = %s:list_manifests' % PROJECT_NAME}
)