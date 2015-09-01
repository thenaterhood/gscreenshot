#!/usr/bin/env python

from setuptools import setup
import sys
import os

install_requires = [
    'pillow',
    'pygtk'
    ]

test_requires = [
    'nose',
    'mock'
    ]

data_files=[
    ('bin/gscreenshot', ['dist/bin/gscreenshot'])
    ]


setup(name='gscreenshot',
    version='2.0.0',
    description='Minimalist network monitoring tool',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/heartbeat/archive/master.zip',
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='nose.collector',
    package_dir={'':'src'},
    packages=[
        'gscreenshot',
        'gscreenshot.resources'
        ],
    data_files=data_files
    )

