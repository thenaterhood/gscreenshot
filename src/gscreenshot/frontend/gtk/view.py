#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
#pylint: disable=too-many-statements
'''
View class for the GTK frontend
'''

import gettext
import io
import threading
from time import sleep
import typing
from gscreenshot.compat import get_resource_file
from gscreenshot.screenshot import ScreenshotCollection
from gscreenshot.util import GSCapabilities

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gdk # type: ignore
from gi.repository import Gtk # type: ignore
from gi.repository import GdkPixbuf # type: ignore

i18n = gettext.gettext


class View(object):
    '''View class for the GTK frontend'''

    def __init__(self, window, builder, capabilities):
        self._builder = builder
        self._window = window
        self._window_is_fullscreen:bool = False
        self._was_maximized:bool = False

        self.hide()

        self._capabilities = capabilities
        self._last_window_dimensions = self._window.get_size()
        self._header_bar = builder.get_object('header_bar')
        self._preview:Gtk.Image = builder.get_object('image1')
        self._preview_event_box:Gtk.EventBox = builder.get_object('preview_event_box')
        self._control_grid:Gtk.Box = builder.get_object('control_box')
        self._cursor_selection_items:Gtk.ListStore = \
            builder.get_object('cursor_selection_items')
        self._cursor_selection_dropdown:Gtk.ComboBox = \
            builder.get_object('pointer_selection_dropdown')
        self._cursor_selection_label:Gtk.Label = \
            builder.get_object('pointer_selection_label')
        self._actions_menu:Gtk.Menu = builder.get_object('menu_saveas_additional_actions')
        self._status_icon:Gtk.Image = builder.get_object('status_icon')
        self._preview_overlay:Gtk.Overlay = builder.get_object('image_overlay')

        self._preview_event_box.drag_source_set(
            Gdk.ModifierType.BUTTON1_MASK,
            [],
            Gdk.DragAction.COPY | Gdk.DragAction.LINK
        )
        self._preview_event_box.drag_source_add_uri_targets()
        self._preview_event_box.drag_source_add_image_targets()

        self._prev_btn:Gtk.Button = Gtk.Button.new_from_stock(Gtk.STOCK_GO_BACK)
        self._prev_btn.set_size_request(20, 20)
        self._prev_btn.set_opacity(0)

        self._next_btn:Gtk.Button = Gtk.Button.new_from_stock(Gtk.STOCK_GO_FORWARD)
        self._next_btn.set_size_request(20, 20)
        self._next_btn.set_opacity(0)

        self._gallery_position:Gtk.Label = Gtk.Label()
        self._gallery_position.set_size_request(1, 20)
        self._gallery_position.set_opacity(0)
        self._gallery_position.modify_bg(0, Gdk.color_parse('#ffff00'))

        self._preview_control:Gtk.ButtonBox = Gtk.ButtonBox()
        self._preview_control.set_hexpand(False)
        self._preview_control.set_vexpand(False)
        self._preview_control.set_halign(Gtk.Align.CENTER)
        self._preview_control.set_valign(Gtk.Align.END)
        self._preview_control.add(self._prev_btn)
        self._preview_control.add(self._gallery_position)
        self._preview_control.add(self._next_btn)

        self._preview_overlay.add_overlay(self._preview_control)

        self._edit_popover:Gtk.Menu= Gtk.Menu()
        self._edit_popover.append(Gtk.CheckMenuItem("potato"))

        if GSCapabilities.ALTERNATE_CURSOR in self._capabilities:
            self._init_cursor_combobox()

        if GSCapabilities.WINDOW_SELECTION not in self._capabilities:
            window_select_button = builder.get_object('button_window')
            self._disable_and_hide(window_select_button)

        if GSCapabilities.REGION_SELECTION not in self._capabilities:
            region_select_button = builder.get_object('button_selectarea')
            self._disable_and_hide(region_select_button)

        if GSCapabilities.CURSOR_CAPTURE not in self._capabilities:
            checkbox_capture_cursor = builder.get_object('checkbox_capture_cursor')
            self._disable_and_hide(checkbox_capture_cursor)

        if GSCapabilities.REUSE_REGION not in self._capabilities:
            reuse_region_dropdown = builder.get_object('selection_actions_btn')
            selectarea_gtkbox = builder.get_object('select_area_gtkbox')
            self._disable_and_hide(reuse_region_dropdown)
            selectarea_gtkbox.remove(reuse_region_dropdown)

        self._window.set_opacity(.3)

    def _disable_and_hide(self, widget):
        '''disables and hides a widget'''
        widget.set_opacity(0)
        widget.set_sensitive(0)

    def _enable_and_show(self, widget):
        '''enables and shows a widget'''
        widget.set_opacity(1)
        widget.set_sensitive(1)

    def _hover_effect(self, widget, *_):
        '''
        applies a higher opacity to the widget when the cursor hovers
        '''
        widget.set_opacity(.9)

    def _unhover_effect(self, widget, *_):
        '''
        applies a lighter opacity to the widget when the cursor leaves
        '''
        widget.set_opacity(.4)

    def update_gallery_controls(self, screenshots:ScreenshotCollection):
        '''
        updates the preview controls to match the current state
        '''
        while Gtk.events_pending():
            Gtk.main_iteration()

        if len(screenshots) > 1:
            current = screenshots.cursor_current()
            unsaved_marker = ""

            if current is not None and not current.saved():
                unsaved_marker = "*"

            self._gallery_position.set_text(
                f"{screenshots.cursor()+1}{unsaved_marker}/{len(screenshots)}")
            self._gallery_position.modify_bg(
                Gtk.STATE_NORMAL,
                self._window.get_style_context()
                    .get_background_color(Gtk.STATE_NORMAL)
                    .to_color())
            self._gallery_position.set_opacity(.5)

        else:
            self._gallery_position.set_text("")
            self._gallery_position.set_opacity(0)

        if screenshots.has_next() and self._next_btn.get_opacity() <= 0:
            self._next_btn.set_opacity(.5)
            self._next_btn.connect('enter', self._hover_effect)
            self._next_btn.connect('leave', self._unhover_effect)
        elif not screenshots.has_next() and self._next_btn.get_opacity() > 0:
            self._next_btn.set_opacity(0)
            self._next_btn.disconnect_by_func(self._hover_effect)
            self._next_btn.disconnect_by_func(self._unhover_effect)

        if screenshots.has_previous() and self._prev_btn.get_opacity() <= 0:
            self._prev_btn.set_opacity(.5)
            self._prev_btn.connect('enter', self._hover_effect)
            self._prev_btn.connect('leave', self._unhover_effect)
        elif not screenshots.has_previous() and self._prev_btn.get_opacity() > 0:
            self._prev_btn.set_opacity(0)
            self._prev_btn.disconnect_by_func(self._hover_effect)
            self._prev_btn.disconnect_by_func(self._unhover_effect)

    def connect_signals(self, presenter):
        '''
        connects signals
        '''
        self._builder.connect_signals(presenter)

        self._window.connect("check-resize", presenter.on_window_resize)
        self._window.connect("window-state-event", presenter.window_state_event_handler)

        png = get_resource_file("gscreenshot.resources.pixmaps", "gscreenshot.png")
        self._window.set_icon_from_file(str(png))

        if self._prev_btn is not None:
            self._prev_btn.connect('clicked', presenter.on_preview_prev_clicked)

        if self._next_btn is not None:
            self._next_btn.connect('clicked', presenter.on_preview_next_clicked)

    def flash_status_icon(self, stock_name: str="emblem-ok"):
        """
        Shows the status/confirmation icon in the UI after an action
        for a second.

        By default this will show the "ok" icon but another one can be
        passed also.

        This is non-blocking.
        """

        self._status_icon.set_from_icon_name(stock_name, Gtk.IconSize.BUTTON)
        self._enable_and_show(self._status_icon)

        while Gtk.events_pending():
            Gtk.main_iteration()

        _thread = threading.Thread(target=self._finish_flash_status_icon)
        _thread.daemon = True
        _thread.start()

    def _finish_flash_status_icon(self):
        """
        Lets the status icon be visible for a second, then hides the widget
        by setting its opacity to 0.
        """
        sleep(1)
        self._disable_and_hide(self._status_icon)

    def set_busy(self):
        """
        Sets the window as busy with visual indicators
        """
        cursor = Gdk.Cursor.new(Gdk.CursorType.WATCH)
        self._window.get_window().set_cursor(cursor)
        while Gtk.events_pending():
            Gtk.main_iteration()

    def set_ready(self):
        """
        Sets the window as ready with visual indicators
        """
        self._window.get_window().set_cursor(None)
        while Gtk.events_pending():
            Gtk.main_iteration()

    def _init_cursor_combobox(self):
        combo = self._cursor_selection_dropdown
        renderer = Gtk.CellRendererPixbuf()
        combo.pack_start(renderer, False)
        combo.add_attribute(renderer, "pixbuf", 0)

        renderer = Gtk.CellRendererText()
        combo.pack_start(renderer, True)
        combo.add_attribute(renderer, "text", 1)

    def show_cursor_options(self, show: bool):
        '''
        Toggle the cursor combobox and label hidden/visible
        '''
        if show and GSCapabilities.ALTERNATE_CURSOR in self._capabilities:
            self._enable_and_show(self._cursor_selection_dropdown)
            self._enable_and_show(self._cursor_selection_label)
            if self._cursor_selection_dropdown.get_active() < 0:
                self._cursor_selection_dropdown.set_active(0)
        else:
            self._disable_and_hide(self._cursor_selection_dropdown)
            self._disable_and_hide(self._cursor_selection_label)

    def update_available_cursors(self, cursors: dict, selected: typing.Optional[str] = None):
        '''
        Update the available cursor selection in the combolist
        Params: self, {name: PIL.Image}
        '''
        self._cursor_selection_items.clear()
        selected_idx = 0
        current_idx = 0
        for cursor_name in cursors:
            if cursors[cursor_name] is not None:
                current_idx += 1
                descriptor = io.BytesIO()
                image = cursors[cursor_name].copy()
                image.thumbnail((
                    self._cursor_selection_dropdown.get_allocation().height*.42,
                    self._cursor_selection_dropdown.get_allocation().width*.42
                ))
                image.save(descriptor, "png")
                contents = descriptor.getvalue()
                descriptor.close()
                loader = GdkPixbuf.PixbufLoader.new_with_type("png")
                loader.write(contents)
                pixbuf = loader.get_pixbuf()
                loader.close()

                i18n_name = i18n(f"cursor-{cursor_name}")
                if i18n_name == f"cursor-{cursor_name}":
                    i18n_name = cursor_name

                self._cursor_selection_items.append(
                    [pixbuf, i18n_name, cursor_name]
                )
                if cursor_name == selected:
                    selected_idx = current_idx
            else:
                self._cursor_selection_items.append(
                    [None, i18n(f"cursor-{cursor_name}"), cursor_name]
                )

            if selected is not None and selected in cursors:
                self._cursor_selection_dropdown.set_active(
                    selected_idx-1
                )
            elif cursor_name == "theme":
                self._cursor_selection_dropdown.set_active(
                    0
                )

    def run(self):
        '''Run the view'''
        self._window.set_position(Gtk.WindowPosition.CENTER)
        # Set the initial size of the window
        active_window = Gdk.get_default_root_window()
        while active_window is None:
            # There appears to be a race condition with getting the active window,
            # so we'll keep trying until we have it
            active_window = Gdk.get_default_root_window()

        initial_screen = self._window.get_screen().get_monitor_at_window(active_window)
        geometry = self._window.get_screen().get_monitor_geometry(initial_screen)

        if self._header_bar is not None:
            height_x = .6
        else:
            height_x = .48

        gscreenshot_height = geometry.height * height_x
        gscreenshot_width = gscreenshot_height * .9

        if geometry.height > geometry.width:
            gscreenshot_width = geometry.width * height_x
            gscreenshot_height = gscreenshot_width * .9

        self._window.set_size_request(gscreenshot_width, gscreenshot_height)

        self._window.show_all()

    def show_actions_menu(self):
        '''
        Show the actions/saveas menu at the pointer
        '''
        self._actions_menu.popup_at_pointer()

    def get_window(self):
        '''Returns the associated window'''
        return self._window

    def toggle_fullscreen(self):
        '''Toggle the window to full screen'''
        if self._window_is_fullscreen:
            self._window.unfullscreen()
        else:
            self._window.fullscreen()

        self._window_is_fullscreen = not self._window_is_fullscreen

    def handle_state_event(self, _, event):
        '''Handles a window state event'''
        self._was_maximized = bool(event.new_window_state & Gdk.WindowState.MAXIMIZED)
        self._window_is_fullscreen = bool(
                            Gdk.WindowState.FULLSCREEN & event.new_window_state)

    def hide(self):
        '''Hide the view'''
        geometry = Gdk.Geometry()
        geometry.min_width = -1
        geometry.min_height = -1

        self._window.set_geometry_hints(None, geometry, Gdk.WindowHints(2))
        # We set the opacity to 0 because hiding the window is
        # subject to window closing effects, which can take long
        # enough that the window will still appear in the screenshot
        self._window.set_opacity(0)

        # This extra step allows the window to be unmaximized after it
        # reappears. Otherwise, the hide() call clears the previous
        # state and the window is stuck maximized. We restore the
        # maximization when we unhide the window.
        if self._was_maximized:
            self._window.unmaximize()

        self._window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        sleep(0.2)

    def unhide(self):
        '''Unhide the view'''
        self._window.set_sensitive(True)
        self._window.set_opacity(1)

        original_window_size = self._window.get_size()
        geometry = Gdk.Geometry()
        geometry.min_width = original_window_size.width
        geometry.min_height = original_window_size.height
        self._window.set_geometry_hints(
            None,
            geometry,
            Gdk.WindowHints(2)
        )

        if self._was_maximized:
            self._window.maximize()

        self._window.show_all()

    def resize(self):
        '''Resize the display'''
        current_window_size = self._window.get_size()
        if self._last_window_dimensions is None:
            self._last_window_dimensions = current_window_size

        if (self._last_window_dimensions.width != current_window_size.width
                or self._last_window_dimensions.height != current_window_size.height):

            self._last_window_dimensions = current_window_size

    def get_preview_dimensions(self):
        '''Get the current dimensions of the preview widget'''
        window_size = self._window.get_size()
        control_size = self._control_grid.get_allocation()

        header_height = 0
        if self._header_bar is not None:
            header_height = self._header_bar.get_allocation().height

        width_x = .8 if self._header_bar is not None else .98

        preview_size = (
            (window_size.height-control_size.height-(.6*header_height))*.98,
            window_size.width*width_x
        )

        height = preview_size[0]
        width = preview_size[1]

        return height, width

    def update_preview(self, pixbuf):
        '''
        Update the preview widget with a new image.

        This assumes the pixbuf has already been resized appropriately.
        '''
        # view the previewPixbuf in the image_preview widget
        self._preview.set_from_pixbuf(pixbuf)

    def copy_to_clipboard(self, pixbuf):
        """
        Copy the provided image to the screen's clipboard,
        if it supports persistence
        """
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        display = Gdk.Display.get_default()

        if display.supports_clipboard_persistence():
            clipboard.set_image(pixbuf)
            clipboard.store()
            return True

        return False

    def run_dialog(self, dialog):
        '''Run a dialog window and return the outcome'''
        self._window.set_sensitive(False)
        result = dialog.run()
        self._window.set_sensitive(True)

        try:
            dialog.destroy()
        except AttributeError:
            # This process is wonky, and due to incorrect polymorphism
            pass

        return result
