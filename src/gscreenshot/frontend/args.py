'''Functions for handling command line arguments'''
import argparse
import gettext

_ = gettext.gettext


def get_args():
    '''Get the parsed command line arguments'''
    parser = argparse.ArgumentParser()

    #pylint: disable=line-too-long
    parser.add_argument(
            '-d',
            '--delay',
            required=False,
            default=0,
            help=_("How many seconds to wait before taking the screenshot. Defaults to 0.")
            )
    parser.add_argument(
            '-f',
            '--filename',
            required=False,
            default=False,
            help=_("Where to store the screenshot file. Defaults to gscreenshot_<time>.png. This can be paired with -c to save and copy. If you specify a filename without a file extension, it will be treated as a directory (creating the tree if needed) and screenshots will be saved there with the default filename scheme.")
            )
    parser.add_argument(
            '-c',
            '--clip',
            required=False,
            action='store_true',
            help=_("Copy the image to the clipboard. Requires xclip to be installed. This can be paired with -f to save and copy together.")
            )
    parser.add_argument(
            '-o',
            '--open',
            required=False,
            action='store_true',
            help=_("Open the screenshot in your default viewer.")
            )
    parser.add_argument(
            '-s',
            '--selection',
            required=False,
            action='store_true',
            help=_("Choose a window or select a region to screenshot.")
            )
    parser.add_argument(
            '-V',
            '--version',
            required=False,
            action='store_true',
            help=_("Show information about gscreenshot")
            )
    parser.add_argument(
            '-n',
            '--notify',
            required=False,
            action='store_true',
            help=_("Show a notification when the screenshot is taken. Gscreenshot will automatically show a notification if a screenshot is taken from a different session, so some situations may not need this option.")
    )
    parser.add_argument(
            '-p',
            '--pointer',
            required=False,
            action='store_true',
            help=_("Capture the cursor.")
    )
    parser.add_argument(
            '-g',
            '--pointer-glyph',
            required=False,
            help=_("The name of a custom cursor glyph ('adwaita', 'prohibit', 'allow') or path to an image.")
    )
    parser.add_argument(
            '--gui',
            required=False,
            action='store_true',
            help=_("Open the gscreenshot GUI. This is the default if no parameters are provided.")
    )

    return parser.parse_args()
