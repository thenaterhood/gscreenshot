from gscreenshot import Gscreenshot
from gscreenshot.frontend import SignalHandler

import argparse
import sys

def run():

    gscreenshot = Gscreenshot()
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
        help="Where to store the screenshot file. Defaults to gscreenshot_<time>.png."
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

    if (args.version is not False):
        authors = gscreenshot.get_program_authors()
        website = gscreenshot.get_program_website()
        description = gscreenshot.get_program_description()
        license = gscreenshot.get_program_license()
        name = gscreenshot.get_program_name()
        version = gscreenshot.get_program_version()

        print("{0} {1}; {2}".format(name, version, description))
        print(website)
        print("")
        print("Author(s)")
        print("\n".join(authors))
        print("")
        print("Licensed as {0}".format(license))
        sys.exit(0)

    if (args.selection is not False):
        gscreenshot.screenshot_selected(args.delay)
    else:
        gscreenshot.screenshot_full_display(args.delay)

    if (args.filename is not False):
        gscreenshot.save_last_image(args.filename)
    else:
        gscreenshot.save_last_image()

def main():
    with SignalHandler():
        run()
