'''Functions for handling command line arguments'''
import argparse
import gettext
import logging
import sys

_ = gettext.gettext


def enable_gui(params) -> bool:
    '''Whether to show the GUI based on args'''

    if 'gscreenshot-cli' in sys.argv[0]:
        return False

    if len(sys.argv) == 1:
        return True

    if params.gui:
        return True

    fake_args = []
    for arg in sys.argv:
        if "--select-color" in arg:
            fake_args.append(arg)
        elif "-g" in arg or "--pointer-glyph" in arg:
            fake_args.append(arg)
        elif "--gui" in arg:
            fake_args.append(arg)
        elif "--select-border-weight" in arg:
            fake_args.append(arg)
        elif "-v" in arg:
            fake_args.append(arg)

    if len(fake_args) == len(sys.argv) - 1:
        return True

    return params.gui


def get_log_level():
    '''Get the log level from sys.argv'''
    if "-v" in sys.argv:
        return logging.INFO

    if "-vv" in sys.argv or "-vvv" in sys.argv:
        return logging.DEBUG

    return logging.WARN


def get_args(args = None):
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
    parser.add_argument(
            '--select-color',
            required=False,
            default="#cccccc99",
            help=_("Optional. The color to use for the selection box. Accepts an RGB/RGBA hex string or '' to use the underlying tool's defaults.")
    )
    parser.add_argument(
            '--select-border-weight',
            required=False,
            default=5,
            help=_("Optional. The thickness of the border of the region selection box.")
    )
    parser.add_argument(
            '-v',
            required=False,
            action='store_true',
            help=_("Verbosity. Add more v for more verbosity. -v, -vv, and -vvv are supported"),
    )

    parsed_args = parser.parse_args(args)

    parsed_args.gui = enable_gui(parsed_args)
    parsed_args.log_level = get_log_level()

    return parsed_args
