#pylint: disable=too-many-statements
#pylint: disable=too-many-branches
'''
Gscreenshot's CLI
'''
import logging
import sys
import gettext
import typing

from gscreenshot import Gscreenshot
from gscreenshot.actions import NotifyAction
from gscreenshot.meta import (
    get_program_authors,
    get_program_description,
    get_program_license,
    get_program_name,
    get_program_version,
    get_program_website,
)
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError
from gscreenshot.screenshot.actions import (
    CopyAction,
    ScreenshotActionError,
    SaveAction,
    SaveTmpfileAction,
    XdgOpenAction,
)
from .args import get_args


log = logging.getLogger(__name__)
_ = gettext.gettext


def resume(app: typing.Optional[Gscreenshot]):
    '''Resume or finish a CLI session'''
    if not app or app.session.get("error", False):
        sys.exit(1)
    sys.exit(0)


def run(app: typing.Optional[Gscreenshot] = None, args = None):
    '''Run the CLI frontend'''
    try:
        gscreenshot = app or Gscreenshot()
    except NoSupportedScreenshooterError as gscreenshot_error:
        log.error(_("No supported screenshot backend is available."))
        if gscreenshot_error.required is None:
            log.error(_("Please install one to use gscreenshot."))
        else:
            log.error(_("Please install one of the following to use gscreenshot:"))
            log.error(", ".join(gscreenshot_error.required))
        return None

    if not args:
        args = get_args()

    logging.basicConfig(level=args.log_level)

    if args.version is not False:
        description = get_program_description()
        name = get_program_name()
        version = get_program_version()

        print(_("Using {0} screenshot backend").format(gscreenshot.get_screenshooter_name()))
        capabilities_formatted = []
        for capability, provider in gscreenshot.get_capabilities().items():
            capabilities_formatted.append(f"{_(capability)} ({provider})")

        print(f"{name} {version}; {description}")
        print(_("Available features: {0}").format(", ".join(capabilities_formatted)))
        print(get_program_website())
        print("")
        print(_("Author(s)"))
        print("\n".join(get_program_authors()))
        print("")
        print(_("Licensed as {0}").format(get_program_license()))
        sys.exit(0)

    if args.select_color:
        gscreenshot.set_select_color(args.select_color)

    if args.select_border_weight:
        try:
            gscreenshot.set_select_border_weight(int(args.select_border_weight))
        except ValueError:
            log.warning(
                "invalid border weight, unable to make an integer out of '%s'",
                args.select_border_weight
            )

    if args.pointer_glyph:
        if args.pointer_glyph not in gscreenshot.get_available_cursors():
            pointer_name = gscreenshot.register_stamp_image(args.pointer_glyph)
            if pointer_name:
                args.pointer_glyph = pointer_name
            else:
                log.warning(_("Unable to open pointer"))
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

    screenshot = gscreenshot.get_screenshot_collection().cursor_current()

    if screenshot is None:
        log.error(_("No screenshot taken."))
        gscreenshot.session["error"] = True
    else:
        saved_screenshot = False
        if args.notify:
            if not NotifyAction().execute():
                log.warning(_("failed to show screenshot notification - is notify-send working?"))

        if args.filename is not False:
            if not SaveAction(filename=args.filename).execute(screenshot):
                log.warning(_("Failed to save screenshot!"))
                gscreenshot.session["error"] = True
            else:
                saved_screenshot = True
        elif args.clip is False and not args.gui:
            if not SaveAction().execute(screenshot):
                log.warning(_("Failed to save screenshot!"))
                gscreenshot.session["error"] = True
            else:
                saved_screenshot = True

        if saved_screenshot and screenshot:
            print(screenshot.get_saved_path())

        if args.open is not False:
            try:
                XdgOpenAction().execute(screenshot)
            except ScreenshotActionError:
                log.warning(_("Failed to open screenshot!"))

        if args.clip is not False:
            try:
                CopyAction().execute(screenshot)
            except ScreenshotActionError as error:
                log.warning(_("Could not clip image! {0} failed to run.").format(error))

                tmp_file = None
                try:
                    tmp_file = SaveTmpfileAction().execute(screenshot)
                except ScreenshotActionError:
                    pass

                if tmp_file is not None:
                    log.warning(_("Your screenshot was saved to {0}").format(tmp_file))
                gscreenshot.session["error"] = True

    return gscreenshot
