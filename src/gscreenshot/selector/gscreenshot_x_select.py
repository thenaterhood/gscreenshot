'''
Super jank homebrew selector using a transparent X window
'''
import typing
from time import sleep

from gscreenshot.util import GSCapabilities

#pylint: disable=wrong-import-position,wrong-import-order
from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk # type: ignore # noqa: E402

from .region_selector import RegionSelector


class GscreenshotXSelect(RegionSelector):

    """
    All methods return a tuple of; the x, y coordinates
    of both corners of the selection.
    """

    __utilityname__: str = "gscreenshot"

    def __init__(self):
        """
        constructor
        """
        RegionSelector.__init__(self)

    def get_capabilities(self) -> typing.Dict[str, str]:
        """
        Get the features this selector supports
        """
        return {
            GSCapabilities.REGION_SELECTION: self.__utilityname__,
            GSCapabilities.REUSE_REGION: self.__utilityname__
        }

    def region_select(self, selection_box_rgba: typing.Optional[str]=None,
                      selection_border_weight: typing.Optional[int]=None):
        """
        Select an arbitrary region of the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        if selection_box_rgba:
            color = RegionSelector._rgba_hex_to_decimals(selection_box_rgba)
        else:
            color = (0, 0, 0, .3)

        return self._get_boundary_interactive([color])

    def window_select(self,
                      selection_box_rgba: typing.Optional[str]=None,
                      selection_border_weight: typing.Optional[int]=None):
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        if selection_box_rgba:
            color = RegionSelector._rgba_hex_to_decimals(selection_box_rgba)
        else:
            color = (0, 0, 0, .3)

        return self._get_boundary_interactive([color])

    def _get_boundary_interactive(self, _params):
        selection_tool = SelectionTool(color=_params[0])
        Gtk.main()
        while Gtk.events_pending():
            Gtk.main_iteration()
        sleep(.3)

        return self._parse_selection_output([selection_tool.region])

    @staticmethod
    def can_run() -> bool:
        """Whether this is available"""
        return True


class SelectionTool(Gtk.Window):
    """SelectionTool"""
    def __init__(self, color = (0, 0, 0, .3)):
        super().__init__()
        self.set_title("Resize to surround your selection")
        self.color = color
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_border_width(40)
        self.set_default_size(600, 450)
        self.screen = self.get_screen()
        self.visual = self.screen.get_rgba_visual()
        if self.visual is not None and self.screen.is_composited():
            self.set_visual(self.visual)

        self.region = ""

        box: Gtk.Grid = Gtk.Grid(vexpand=False, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)

        btn1 = Gtk.Button(label="Click to Capture")
        btn1.connect('clicked', self.get_region)
        # widget, column, row, width, height
        box.attach(btn1, 0, 0, 1, 1)

        cancel_btn = Gtk.Button(label="Cancel")
        cancel_btn.connect('clicked', self.handle_cancel_btn)
        box.attach(cancel_btn, 0, 1, 1, 1)

        self.add(box)

        self.set_app_paintable(True)
        self.connect("draw", self.area_draw)
        self.connect("destroy", Gtk.main_quit)

        self.show_all()

    def area_draw(self, _widget, canvas):
        """draws the transparent area of the window"""
        canvas.set_source_rgba(*self.color)
        canvas.paint()

    def get_region(self, _widget):
        """gets the region"""
        coords = self.get_position()
        size = self.get_allocation()

        geometry = Gdk.Geometry()
        geometry.min_width = -1
        geometry.min_height = -1

        self.set_geometry_hints(None, geometry, Gdk.WindowHints(2))
        self.set_opacity(0)

        self.region = f"X={coords.root_x},Y={coords.root_y},W={size.width},H={size.height}"
        self.destroy()

    def handle_cancel_btn(self, _):
        """handle the cancel button"""
        self.destroy()
