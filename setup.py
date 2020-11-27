#!/usr/bin/env python

from setuptools import setup
import errno
import sys
import os

pkg_version='2.12.3'

install_requires = [
    'pillow',
    ]

test_requires = [
    'nose',
    'mock'
    ]

data_files = [
    ('share/applications', ['dist/desktop/gscreenshot.desktop']),
    ('share/pixmaps', ['dist/pixmaps/gscreenshot.png']),
    ('share/menu', ['dist/menu/gscreenshot'])
    ]

def build_data_files():
    '''
    This is somewhat of a workaround so that the data files that
    contain a version number end up with the correct version number
    in them since it's easy to forget to update them

    This code assumes there will only ever be one file getting installed
    at a particular path. For gscreenshot this is fine.
    '''
    files = []
    for d in data_files:
        generated_path = os.path.join('generated', d[1][0])
        try:
            with open(d[1][0], 'r') as infile:
                infile_data = infile.read()
                updated_data = infile_data.replace('%%VERSION%%', pkg_version)
                try:
                    os.makedirs(os.path.dirname(generated_path))
                except (OSError, FileExistsError) as e:
                    if not os.path.isdir(os.path.dirname(generated_path)):
                        raise

                with open(generated_path, 'w') as outfile:
                    outfile.write(updated_data)
            files.append((d[0], [generated_path]))
        except UnicodeDecodeError:
            # Just assume this is a binary file that we don't need to
            # replace anything in
            files.append((d[0], d[1]))

    return files


setup(name='gscreenshot',
    version=pkg_version,
    description='Lightweight GTK frontend to scrot',
    author='Nate Levesque',
    author_email='public@thenaterhood.com',
    url='https://github.com/thenaterhood/gscreenshot/archive/master.zip',
    install_requires=install_requires,
    tests_require=test_requires,
    entry_points={
        'gui_scripts': [
            'gscreenshot = gscreenshot.frontend:delegate'
        ],
        'console_scripts': [
            'gscreenshot-cli = gscreenshot.frontend:delegate'
        ]
    },
    test_suite='nose.collector',
    package_dir={'':'src'},
    packages=[
        'gscreenshot',
        'gscreenshot.frontend',
        'gscreenshot.screenshooter',
        'gscreenshot.selector',
        'gscreenshot.resources',
        'gscreenshot.resources.gui',
        'gscreenshot.resources.gui.glade',
        'gscreenshot.resources.pixmaps'
        ],
    data_files=build_data_files(),
    package_data={
        '': ['*.glade', 'LICENSE', '*.png']
        }
    )
