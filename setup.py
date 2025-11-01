#!/usr/bin/env python

from setuptools import setup, Command
import glob
import subprocess
import os

try:
    FileExistsError()
except:
    class FileExistsError(BaseException):
        pass

data_files = [
    ('share/applications', ['dist/desktop/gscreenshot.desktop']),
    ('share/pixmaps', ['dist/pixmaps/gscreenshot.png', 'dist/pixmaps/gscreenshot-10year.png']),
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
    try:
        os.makedirs("generated")
    except (OSError, FileExistsError):
        if not os.path.isdir("generated"):
            raise
    compile_locales()
    compile_manpage()
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
                except (OSError, FileExistsError):
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
        except Exception:
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


class TestCommand(Command):
    description = 'run the tests'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        command = ['coverage', 'run', '--source', 'src/gscreenshot', '-m', 'pytest', 'test']
        subprocess.check_call(command)


class CoverageCommand(Command):
    description = 'run the tests and produce a coverage report'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        command = ['coverage', 'run', '--source', 'src/gscreenshot', '-m', 'pytest', 'test']
        subprocess.check_call(command)
        command = ['coverage', 'html']
        subprocess.check_call(command)
        command = ['xdg-open', 'htmlcov/index.html']
        subprocess.check_call(command)


setup(name='gscreenshot',
    cmdclass={
        'test': TestCommand,
        'coverage': CoverageCommand,
    },
    version=pkg_version,
    data_files=build_data_files(pkg_version),
    )
