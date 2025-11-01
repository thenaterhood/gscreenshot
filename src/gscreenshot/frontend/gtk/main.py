#pylint: disable=unused-argument
#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
#pylint: disable=too-many-statements
'''
Main method for the GTK frontend
'''
import gettext
import sys
import typing
from time import sleep
from gscreenshot import Gscreenshot
from gscreenshot.compat import get_resource_string
from gscreenshot.frontend.presenter import Presenter
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError
from .dialogs import WarningDialog
from .view import View

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gdk # type: ignore
from gi.repository import Gtk # type: ignore

i18n = gettext.gettext


def main(app: typing.Optional[Gscreenshot] = None):
    '''The main function for the GTK frontend'''

    try:
        application = app or Gscreenshot()
    except NoSupportedScreenshooterError as gscreenshot_error:
        warning = WarningDialog(
            i18n("No supported screenshot backend is available."),
            None
            )

        if gscreenshot_error.required is not None:
            warning = WarningDialog(
                    i18n("Please install one of the following to use gscreenshot:")
                    + ", ".join(gscreenshot_error.required),
                    None
                )

        warning.run()
        sys.exit(1)

    builder = Gtk.Builder()
    builder.set_translation_domain('gscreenshot')

    builder.add_from_string(
        get_resource_string(
            "gscreenshot.resources.gui.glade", "main.glade"
        )
    )
    window = builder.get_object('window_main')

    capabilities = application.get_capabilities()
    view = View(window, builder, capabilities)

    presenter = Presenter(
            application,
            view
            )

    if not application.get_screenshot_collection().cursor_current():
        # Lucky 13 to give a tiny bit more time for the desktop environment
        # to settle down and hide the window before we take our initial
        # screenshot.
        sleep(0.13)
        presenter.on_button_all_clicked()

    accel = Gtk.AccelGroup()
    accel.connect(Gdk.keyval_from_name('S'), Gdk.ModifierType.CONTROL_MASK,
            0, presenter.on_button_saveas_clicked)
    accel.connect(Gdk.keyval_from_name('C'), Gdk.ModifierType.CONTROL_MASK,
            0, presenter.on_button_copy_clicked)
    accel.connect(Gdk.keyval_from_name('O'), Gdk.ModifierType.CONTROL_MASK,
            0, presenter.on_button_open_clicked)
    accel.connect(Gdk.keyval_from_name('O'),
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
            0,
            presenter.on_button_openwith_clicked)
    accel.connect(Gdk.keyval_from_name('C'),
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
            0,
            presenter.on_button_copy_and_close_clicked)
    # These are set up in glade, so adding them here is redundant.
    # We'll keep the code for reference.
    #window.add_accel_group(accel)

    window.connect("key-press-event", presenter.handle_keypress)
    window.connect("delete-event", presenter.on_button_quit_clicked)

    keymappings = {
        Gdk.keyval_to_lower(Gdk.keyval_from_name('Escape')):
            presenter.on_button_quit_clicked,
        Gdk.keyval_to_lower(Gdk.keyval_from_name('F11')):
            presenter.on_fullscreen_toggle,
        Gdk.keyval_to_lower(Gdk.keyval_from_name('Right')):
            presenter.on_preview_next_clicked,
        Gdk.keyval_to_lower(Gdk.keyval_from_name('Left')):
            presenter.on_preview_prev_clicked,
        Gdk.keyval_to_lower(Gdk.keyval_from_name('Delete')):
            presenter.on_delete,
        # Handled in Glade - just here for reference
        #Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('Insert')):
        #    presenter.overwrite_mode_toggled
    }
    presenter.set_keymappings(keymappings)

    view.connect_signals(presenter)
    view.run()

    Gtk.main()

if __name__ == "__main__":
    main()
