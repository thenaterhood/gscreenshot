#pylint: disable=too-many-statements
#pylint: disable=too-many-branches
'''
Gscreenshot's CLI
'''
import sys
import gettext
import typing

from gscreenshot import Gscreenshot, GscreenshotClipboardException
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError
from .args import get_args


_ = gettext.gettext


def resume(app: typing.Optional[Gscreenshot]):
    '''Resume or finish a CLI session'''
    if not app or app.session.get("error", False):
        sys.exit(1)
    sys.exit(0)


def run():
    '''Run the CLI frontend'''
    try:
        gscreenshot = Gscreenshot()
    except NoSupportedScreenshooterError as gscreenshot_error:
        print(_("No supported screenshot backend is available."))
        if gscreenshot_error.required is None:
            print(_("Please install one to use gscreenshot."))
        else:
            print(_("Please install one of the following to use gscreenshot:"))
            print(", ".join(gscreenshot_error.required))
        return None

    args = get_args()

    if args.version is not False:
        description = gscreenshot.get_program_description()
        name = gscreenshot.get_program_name()
        version = gscreenshot.get_program_version()

        print(_("Using {0} screenshot backend").format(gscreenshot.get_screenshooter_name()))
        capabilities_formatted = []
        for capability, provider in gscreenshot.get_capabilities().items():
            capabilities_formatted.append(f"{_(capability)} ({provider})")

        print(f"{name} {version}; {description}")
        print(_("Available features: {0}").format(", ".join(capabilities_formatted)))
        print(gscreenshot.get_program_website())
        print("")
        print(_("Author(s)"))
        print("\n".join(gscreenshot.get_program_authors()))
        print("")
        print(_("Licensed as {0}").format(gscreenshot.get_program_license()))
        sys.exit(0)

    if args.pointer_glyph:
        if args.pointer_glyph not in gscreenshot.get_available_cursors():
            pointer_name = gscreenshot.register_stamp_image(args.pointer_glyph)
            if pointer_name:
                args.pointer_glyph = pointer_name
            else:
                print(_("Unable to open pointer"))
                args.pointer_glyph = 'theme'

    if args.selection is not False:
        gscreenshot.screenshot_selected(
            delay=int(args.delay),
            capture_cursor=args.pointer,
            cursor_name=args.pointer_glyph
        )
    else:
        gscreenshot.screenshot_full_display(
            delay=int(args.delay),
            capture_cursor=args.pointer,
            cursor_name=args.pointer_glyph
        )

    if gscreenshot.get_last_image() is None:
        print(_("No screenshot taken."))
        gscreenshot.session["error"] = True
    else:
        if args.notify:
            if not gscreenshot.show_screenshot_notification():
                print(_("failed to show screenshot notification - is notify-send working?"))

        if args.filename is not False:
            if not gscreenshot.save_last_image(args.filename):
                print(_("Failed to save screenshot!"))
                gscreenshot.session["error"] = True
        elif args.clip is False and not args.gui:
            if not gscreenshot.save_last_image():
                print(_("Failed to save screenshot!"))
                gscreenshot.session["error"] = True

        if args.open is not False:
            gscreenshot.open_last_screenshot()

        if args.clip is not False:
            try:
                gscreenshot.copy_last_screenshot_to_clipboard()
            except GscreenshotClipboardException as error:
                tmp_file = gscreenshot.save_and_return_path()
                print(_("Could not clip image! {0} failed to run.").format(error))

                if tmp_file is not None:
                    print(_("Your screenshot was saved to {0}").format(tmp_file))
                gscreenshot.session["error"] = True

    return gscreenshot
