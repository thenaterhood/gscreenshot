'''
Classes for capturing the cursor position using Gtk
'''
#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
import typing

from gi import require_version
require_version('Gtk', '3.0')

from gi.repository import Gtk  # type: ignore
from .cursor_locator import CursorLocator


class GtkCursorLocator(CursorLocator):
    '''
    Interactive cursor locator driving class
    '''

    __utilityname__: str = "gscreenshot"

    def get_cursor_position(self) -> typing.Optional[typing.Tuple[int, int]]:
        """
        Gets the current position of the mouse cursor, if able.
        Returns (x, y) or None.
        """
        locator = GtkCursorLocatorWindow()
        Gtk.main()
        while Gtk.events_pending():
            Gtk.main_iteration()

        return locator.cursor_position

    @staticmethod
    def can_run() -> bool:
        return True


class GtkCursorLocatorWindow(Gtk.Window):
    '''
    GTK window for capturing the cursor position
    '''
    def __init__(self):
        super().__init__()
        self.cursor_position = None
        self.set_title("gscreenshot")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.fullscreen()
        self.set_opacity(.65)
        self.screen = self.get_screen()

        box: Gtk.Grid = Gtk.Grid(
            vexpand=False,
            halign = Gtk.Align.CENTER,
            valign = Gtk.Align.CENTER
        )

        help_text = Gtk.Label()
        help_text.set_text(
            "Move your cursor to the desired position then click to capture"
        )
        help_subtext = Gtk.Label()
        help_subtext.set_text(
            "This extra step is required on Wayland. On X11, install Xlib to skip this."
        )
        box.attach(help_text, 0, 0, 1, 1)
        box.attach(help_subtext, 0, 1, 1, 1)
        self.add(box)

        self.connect("button_press_event", self.on_button_press)
        self.connect("key-press-event", self.on_keypress)
        self.connect("destroy", Gtk.main_quit)

        self.show_all()

    def on_button_press(self, _widget, event):
        '''handle button press'''
        self.cursor_position = (int(event.x), int(event.y))
        self.destroy()

    def on_keypress(self, _widget, _event):
        '''handle keypress'''
        self.destroy()
