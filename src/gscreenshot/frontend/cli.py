from gscreenshot import Gscreenshot
from gscreenshot.frontend import SignalHandler
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError

import argparse
import sys
import os
import tempfile
import subprocess

def xclip_image_file(imagefname):
    params = [
            'xclip',
            '-i',
            imagefname,
            '-selection',
            'clipboard',
            '-t',
            'image/png'
            ]
    try:
        subprocess.Popen(params, close_fds=True, stdin=None, stdout=None, stderr=None)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def run():

    parser = argparse.ArgumentParser()

    parser.add_argument(
            '-d',
            '--delay',
            required=False,
            default=0,
            help="How many seconds to wait before taking the screenshot. Defaults to 0."
            )
    parser.add_argument(
            '-f',
            '--filename',
            required=False,
            default=False,
            help="Where to store the screenshot file. Defaults to gscreenshot_<time>.png. This can be paired with -c to save and copy."
            )
    parser.add_argument(
            '-c',
            '--clip',
            required=False,
            action='store_true',
            help="Copy the image to the clipboard. Requires xclip to be installed. This can be paired with -f to save and copy together."
            )
    parser.add_argument(
            '-o',
            '--open',
            required=False,
            action='store_true',
            help="Open the screenshot in your default viewer."
            )
    parser.add_argument(
            '-s',
            '--selection',
            required=False,
            action='store_true',
            help="Choose a window or select a region to screenshot."
            )
    parser.add_argument(
            '-V',
            '--version',
            required=False,
            action='store_true',
            help="Show information about gscreenshot"
            )

    args = parser.parse_args()

    try:
        gscreenshot = Gscreenshot()
    except NoSupportedScreenshooterError:
        print("No supported screenshot backend is available.")
        print("Please install one to use gscreenshot.")
        sys.exit(1)

    if (args.version is not False):
        authors = gscreenshot.get_program_authors()
        website = gscreenshot.get_program_website()
        description = gscreenshot.get_program_description()
        license_name = gscreenshot.get_program_license()
        name = gscreenshot.get_program_name()
        version = gscreenshot.get_program_version()

        print("Using " + gscreenshot.get_screenshooter_name() + " screenshot backend")
        print("{0} {1}; {2}".format(name, version, description))
        print(website)
        print("")
        print("Author(s)")
        print("\n".join(authors))
        print("")
        print("Licensed as {0}".format(license_name))
        sys.exit(0)

    if (args.selection is not False):
        gscreenshot.screenshot_selected(args.delay)
    else:
        gscreenshot.screenshot_full_display(args.delay)

    if (gscreenshot.get_last_image() is None):
        pass
    else:
        if (args.filename is not False):
            gscreenshot.save_last_image(args.filename)
        elif (args.clip is False):
            gscreenshot.save_last_image()

        if (args.open is not False):
            gscreenshot.open_last_screenshot()

        if (args.clip is not False):
            tmp_file = os.path.join(
                    tempfile.gettempdir(),
                    'gscreenshot-cli-clip.png'
                    )
            gscreenshot.save_last_image(tmp_file)
            successful_clip = xclip_image_file(tmp_file)

            if (not successful_clip):
                print("Could not clip image! Xclip failed to run - is it installed?")
                print("Your screenshot was saved to " + tmp_file)

def main():
    with SignalHandler():
        run()
