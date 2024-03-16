#!/usr/bin/env python
import pygtkcompat
pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')

from time import sleep
from gi.repository import Gtk, Gdk
from gscreenshot.cursor_locator import CursorLocator
import typing


class GtkCursorLocator(CursorLocator):

    __utilityname__: str = "gscreenshot"

    def get_cursor_position(self) -> typing.Optional[typing.Tuple[int, int]]:
        """
        Gets the current position of the mouse cursor, if able.
        Returns (x, y) or None.
        """
        locator = GtkCursorLocatorWindow()
        locator.show_all()
        Gtk.main()
        while Gtk.events_pending():
            Gtk.main_iteration()

        return locator.position
    @staticmethod
    def can_run() -> bool:
        return True


class GtkCursorLocatorWindow(Gtk.Window):
    def __init__(self):
        super(GtkCursorLocatorWindow, self).__init__()
        self.set_title("gscreenshot")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.fullscreen()
        self.set_opacity(.25)
        self.screen = self.get_screen()

        box: Gtk.Grid = Gtk.Grid(vexpand=False, halign = Gtk.Align.CENTER, valign = Gtk.Align.CENTER)

        help_text = Gtk.Label()
        help_text.set_text("Move your cursor to the desired position then click to capture")
        help_subtext = Gtk.Label()
        help_subtext.set_text("This extra step is required on Wayland due to enhanced security. On X11, install Xlib to skip this.")
        box.attach(help_text, 0, 0, 1, 1)
        box.attach(help_subtext, 0, 1, 1, 1)
        self.add(box)
        #self.connect("motion_notify_event", self.on_mouse_move)
        self.connect("button_press_event", self.on_button_press)

        self.set_events(Gdk.POINTER_MOTION_MASK 
                        | Gdk.BUTTON_PRESS_MASK)

    def on_mouse_move(self, widget, event):
        print(f"Mouse moved to {(int(event.x), int(event.y))}")

    def on_button_press(self, widget, event):
        self.position = (int(event.x), int(event.y))
        self.destroy()
        Gtk.main_quit()

