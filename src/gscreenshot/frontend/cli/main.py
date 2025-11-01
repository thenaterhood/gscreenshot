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
from gscreenshot.frontend.cli.view import GscreenshotCli
from gscreenshot.frontend.presenter import Presenter
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError
from .args import get_args


log = logging.getLogger(__name__)
_ = gettext.gettext


def resume(app: typing.Optional[Gscreenshot]):
    '''Resume or finish a CLI session'''
    if not app or app.session.get("error", False):
        sys.exit(1)
    sys.exit(0)


def main(app: typing.Optional[Gscreenshot] = None, args = None):
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
    view = GscreenshotCli(args)
    presenter = Presenter(gscreenshot, view)

    if args.version:
        presenter.on_button_about_clicked()
        sys.exit(0)

    try:
        gscreenshot.set_select_border_weight(int(args.select_border_weight))
    except ValueError:
        view.show_warning(
            f"invalid border weight '{args.select_border_weight}'",
        )
    gscreenshot.set_select_color(args.select_color)
    presenter.delay_value_changed(args.delay)
    presenter.capture_cursor_toggled(args.pointer)
    presenter.selected_cursor_changed(args.pointer_glyph)

    if args.use_region:
        presenter.on_stored_region_selected(args.use_region)
    elif args.selection is not False:
        presenter.on_button_selectarea_clicked()
        if args.save_region_as:
            presenter.on_region_save_clicked(region_name=args.save_region_as)

    else:
        presenter.on_button_all_clicked()

    screenshot = gscreenshot.get_screenshot_collection().cursor_current()

    if screenshot is None:
        log.error(_("No screenshot taken."))
        gscreenshot.session["error"] = True
    else:
        saved_screenshot = False
        if args.notify:
            if not NotifyAction().execute():
                log.warning(_("failed to show screenshot notification - is notify-send working?"))

        if args.filename is not False or (args.clip is False and not args.gui):
            saved_screenshot = presenter.on_button_saveas_clicked()
            if not saved_screenshot:
                gscreenshot.session["error"] = True

        if saved_screenshot and screenshot:
            print(screenshot.get_saved_path())

        if args.open is not False:
            presenter.on_button_open_clicked()

        if args.clip is not False:
            if not presenter.on_button_copy_clicked():
                presenter.on_button_saveas_clicked()
                tmp_file = screenshot.get_saved_path()

                if tmp_file is not None:
                    log.warning(_("Your screenshot was saved to {0}").format(tmp_file))
                gscreenshot.session["error"] = True

    return gscreenshot
