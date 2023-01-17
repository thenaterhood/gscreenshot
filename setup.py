#!/usr/bin/env python

from setuptools import setup
import errno
import glob
import subprocess
import sys
import os

try:
    FileExistsError()
except:
    class FileExistsError(BaseException):
        pass

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
    ('share/menu', ['dist/menu/gscreenshot']),
    ('share/man/man1', ['generated/gscreenshot.1.gz']),
    ('share/zsh/site-functions', ['dist/completions/zsh/_gscreenshot']),
    ('share/bash-completion/completions', ['dist/completions/bash/gscreenshot'])
    ]

def print_warning(warning:str):
    print("\n\n\n\n")
    print("===> WARNING ====> " + warning)
    print("\n\n\n\n")

def get_version_from_specfile() -> str:
    '''
    Gets the version from the RPM specfile in specs/

    This is a hackaround because I always forget to update it
    '''
    version = None
    with open('specs/gscreenshot.spec', 'r') as specfile:
        for line in specfile:
            if '%define version' in line:
                version = line.split(' ')[2].strip()
                break

    if version is None:
        raise Exception("Failed to get version")

    return version


def build_data_files(version):
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
            if not os.path.exists(d[1][0]):
                print("WARNING: missing intermediate file " + d[1][0])
                continue
            with open(d[1][0], 'r') as infile:
                infile_data = infile.read()
                updated_data = infile_data.replace('%%VERSION%%', version)
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


def compile_locales():
    print('=> Compiling locales...')

    locale_po = glob.glob('src/gscreenshot/resources/locale/*/LC_MESSAGES/*.po')

    for po in locale_po:
        dirname = os.path.dirname(po)
        basename = os.path.basename(po)
        outname = os.path.splitext(basename)[0] + ".mo"
        original_dir = os.path.abspath(os.path.curdir)
        print('===> Compiling ' + po)
        os.chdir(dirname)
        try:
            subprocess.check_output(['msgfmt', basename, '-o', outname])
        except:
            print_warning("Failed to compile " + po)
        os.chdir(original_dir)


def compile_manpage():
    print('=> Compiling manpage...')

    success = False

    man_converters = [
        [
            'pandoc',
            '--standalone',
            '--to',
            'man',
            'README.md',
            '-o',
            'generated/gscreenshot.1'
        ],
        [
            'go-md2man',
            '--in',
            'README.md',
            '--out',
            'generated/gscreenshot.1'
        ]
    ]

    for converter in man_converters:
        try:
            subprocess.check_output(converter)
            success = True
            break
        except Exception as e:
            continue

    if not success:
        print_warning("Non-fatal. Failed to compile manpage. Install pandoc or md2man (sometimes go-md2man).")
        return

    try:
        subprocess.check_output([
            'gzip',
            '-f',
            'generated/gscreenshot.1',
        ])
    except:
        print_warning("Failed to compress manpage")
        return


pkg_version = get_version_from_specfile()


try:
    os.makedirs("generated")
except (OSError, FileExistsError) as e:
    if not os.path.isdir("generated"):
        raise
compile_locales()
compile_manpage()

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
        'gscreenshot.frontend.gtk',
        'gscreenshot.screenshooter',
        'gscreenshot.screenshot',
        'gscreenshot.screenshot.effects',
        'gscreenshot.selector',
        'gscreenshot.resources',
        'gscreenshot.resources.gui',
        'gscreenshot.resources.gui.glade',
        'gscreenshot.resources.locale.en.LC_MESSAGES',
        'gscreenshot.resources.locale.es.LC_MESSAGES',
        'gscreenshot.resources.pixmaps'
        ],
    data_files=build_data_files(pkg_version),
    package_data={
        '': ['*.glade', 'LICENSE', '*.png', '*.mo',
            'gscreenshot.1.gz', '_gscreenshot', 'gscreenshot']
        },
    include_package_data=True
    )
