#pylint: disable=unused-argument
#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
#pylint: disable=too-many-lines
'''
Classes for the GTK gscreenshot frontend
'''
import gettext
import io
import sys
import threading
import typing
from time import sleep
from pkg_resources import resource_string, resource_filename
import pygtkcompat
from gscreenshot import Gscreenshot
from gscreenshot.util import GSCapabilities
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError

pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

i18n = gettext.gettext


class View(object):
    '''View class for the GTK frontend'''

    def __init__(self, window, builder, capabilities):
        self._builder = builder
        self._window = window
        self._window_is_fullscreen:bool = False
        self._was_maximized:bool = False
        self._capabilities = capabilities
        self._last_window_dimensions = self._window.get_size()
        self._header_bar = builder.get_object('header_bar')
        self._preview:Gtk.Image = builder.get_object('image1')
        self._control_grid:Gtk.Box = builder.get_object('control_box')
        self._cursor_selection_items:Gtk.ListStore = \
            builder.get_object('cursor_selection_items')
        self._cursor_selection_dropdown:Gtk.ComboBox = \
            builder.get_object('pointer_selection_dropdown')
        self._cursor_selection_label:Gtk.Label = \
            builder.get_object('pointer_selection_label')
        self._multishot_count:Gtk.SpinButton = builder.get_object('multishot_count')
        self._multishot_label:Gtk.Label = builder.get_object('multishot_count_label')
        self._actions_menu:Gtk.Menu = builder.get_object('menu_saveas_additional_actions')
        self._status_icon:Gtk.Image = builder.get_object('status_icon')
        self._preview_overlay:Gtk.Overlay = builder.get_object('image_overlay')

        self._prev_btn:Gtk.Button = Gtk.Button.new_from_stock(Gtk.STOCK_GO_BACK)
        self._prev_btn.set_size_request(20, 20)
        self._prev_btn.set_opacity(0)

        self._next_btn:Gtk.Button = Gtk.Button.new_from_stock(Gtk.STOCK_GO_FORWARD)
        self._next_btn.set_size_request(20, 20)
        self._next_btn.set_opacity(0)

        self._preview_control:Gtk.ButtonBox = Gtk.ButtonBox()
        self._preview_control.set_hexpand(False)
        self._preview_control.set_vexpand(False)
        self._preview_control.set_halign(Gtk.Align.CENTER)
        self._preview_control.set_valign(Gtk.Align.END)
        self._preview_control.add(self._prev_btn)
        self._preview_control.add(self._next_btn)

        self._preview_overlay.add_overlay(self._preview_control)

        self.update_gallery_controls(False, False)

        self._disable_and_hide(self._multishot_count)
        self._disable_and_hide(self._multishot_label)

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

    def show_multishot_count(self, enable):
        '''
        enable and show the multishot controls
        '''
        if not enable:
            self._disable_and_hide(self._multishot_count)
            self._disable_and_hide(self._multishot_label)
        else:
            self._enable_and_show(self._multishot_count)
            self._enable_and_show(self._multishot_label)

    def update_gallery_controls(self, show_next=True, show_previous=True):
        '''
        updates the preview controls to match the current state
        '''
        while Gtk.events_pending():
            Gtk.main_iteration()

        if show_next and self._next_btn.get_opacity() <= 0:
            self._next_btn.set_opacity(.5)
            self._next_btn.connect('enter', self._hover_effect)
            self._next_btn.connect('leave', self._unhover_effect)
        elif not show_next and self._next_btn.get_opacity() > 0:
            self._next_btn.set_opacity(0)
            self._next_btn.disconnect_by_func(self._hover_effect)
            self._next_btn.disconnect_by_func(self._unhover_effect)

        if show_previous and self._prev_btn.get_opacity() <= 0:
            self._prev_btn.set_opacity(.5)
            self._prev_btn.connect('enter', self._hover_effect)
            self._prev_btn.connect('leave', self._unhover_effect)
        elif not show_previous and self._prev_btn.get_opacity() > 0:
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
        self._window.set_icon_from_file(
            resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png')
        )

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

        self._status_icon.set_opacity(1)
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
        self._status_icon.set_opacity(0)

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
            self._cursor_selection_dropdown.set_opacity(1)
            self._cursor_selection_label.set_opacity(1)
            self._cursor_selection_dropdown.set_sensitive(1)
        else:
            self._cursor_selection_dropdown.set_opacity(0)
            self._cursor_selection_label.set_opacity(0)
            self._cursor_selection_dropdown.set_sensitive(0)

    def update_available_cursors(self, cursors: dict):
        '''
        Update the available cursor selection in the combolist
        Params: self, {name: PIL.Image}
        '''
        self._cursor_selection_items.clear()
        for cursor_name in cursors:
            if cursors[cursor_name] is not None:
                descriptor = io.BytesIO()
                image = cursors[cursor_name]
                image.thumbnail((
                    self._cursor_selection_dropdown.get_allocation().height*.42,
                    self._cursor_selection_dropdown.get_allocation().width*.42
                ))
                image.save(descriptor, "png")
                contents = descriptor.getvalue()
                descriptor.close()
                loader = Gtk.gdk.PixbufLoader("png")
                loader.write(contents)
                pixbuf = loader.get_pixbuf()
                loader.close()

                self._cursor_selection_items.append(
                    [pixbuf, i18n('cursor-' + cursor_name), cursor_name]
                )
            else:
                self._cursor_selection_items.append(
                    [None, i18n('cursor-' + cursor_name), cursor_name]
                )

            if cursor_name == "theme":
                self._cursor_selection_dropdown.set_active(
                    len(self._cursor_selection_items)-1
                )

    def run(self):
        '''Run the view'''
        self._window.set_position(Gtk.WIN_POS_CENTER)
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

    def handle_state_event(self, widget, event):
        '''Handles a window state event'''
        widget = None
        self._was_maximized = bool(event.new_window_state & Gtk.gdk.WINDOW_STATE_MAXIMIZED)
        self._window_is_fullscreen = bool(
                            Gtk.gdk.WINDOW_STATE_FULLSCREEN & event.new_window_state)

    def hide(self):
        '''Hide the view'''
        self._window.set_geometry_hints(None, min_width=-1, min_height=-1)
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
        self._window.set_geometry_hints(
            None,
            min_width=original_window_size.width,
            min_height=original_window_size.height
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


class Presenter(object):
    '''Presenter class for the GTK frontend'''

    __slots__ = ('_delay', '_app', '_hide', '_can_resize',
            '_pixbuf', '_view', '_keymappings', '_capture_cursor',
            '_cursor_selection', '_multishot_mode', '_multishot_count')

    _delay: int
    _app: Gscreenshot
    _hide: bool
    _can_resize: bool
    _pixbuf: Gdk.PixbufLoader
    _view: View
    _keymappings: dict
    _capture_cursor: bool
    _cursor_selection: str
    _multishot_mode: bool
    _multishot_count: int

    def __init__(self, application: Gscreenshot, view: View):
        self._app = application
        self._view = view
        self._can_resize = True
        self._delay = 0
        self._hide = True
        self._capture_cursor = False
        self._multishot_mode = False
        self._multishot_count = 1
        self._show_preview()
        self._view.show_cursor_options(self._capture_cursor)
        self._keymappings = {}

        cursors = self._app.get_available_cursors()
        self._cursor_selection = 'theme'

        self._view.update_available_cursors(
                cursors
                )

    def _begin_take_screenshot(self, app_method):
        if self._multishot_mode:
            count = self._multishot_count
        else:
            count = 1

        app_method(delay=self._delay,
            capture_cursor=self._capture_cursor,
            cursor_name=self._cursor_selection,
            multishot=self._multishot_mode,
            count=count)

        # Re-enable UI on the UI thread.
        GLib.idle_add(self._end_take_screenshot)

    def _end_take_screenshot(self):
        self._show_preview()
        screenshot_collection = self._app.get_screenshot_collection()
        self._view.update_gallery_controls(
            show_next=screenshot_collection.has_next(),
            show_previous=screenshot_collection.has_previous()
        )

        self._view.unhide()
        self._view.set_ready()

    def set_keymappings(self, keymappings: dict):
        '''Set the keymappings'''
        self._keymappings = keymappings

    def window_state_event_handler(self, widget, event, *_):
        '''Handle window state events'''
        self._view.handle_state_event(widget, event)

    def take_screenshot(self, app_method: typing.Callable):
        '''Take a screenshot using the passed app method'''
        self._view.set_busy()

        if self._hide:
            self._view.hide()

        # Do work in background thread.
        # Taken from here: https://wiki.gnome.org/Projects/PyGObject/Threading
        _thread = threading.Thread(target=self._begin_take_screenshot(app_method))
        _thread.daemon = True
        _thread.start()

    def handle_keypress(self, widget, event, *args):
        """
        This method handles individual keypresses. These are
        handled separately from accelerators (which include
        modifiers).
        """
        if event.keyval in self._keymappings:
            self._keymappings[event.keyval]()

    def handle_preview_click_event(self, widget, event, *args):
        '''
        Handle a click on the screenshot preview widget
        '''
        # 3 is right click
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3:
            self._view.show_actions_menu()

    def hide_window_toggled(self, widget):
        '''Toggle the window to hidden'''
        self._hide = widget.get_active()

    def capture_cursor_toggled(self, widget):
        '''Toggle capturing cursor'''
        self._capture_cursor = widget.get_active()
        self._view.show_cursor_options(self._capture_cursor)

    def delay_value_changed(self, widget):
        '''Handle a change with the screenshot delay input'''
        self._delay = widget.get_value()

    def multishot_value_changed(self, widget):
        '''Handle a change with the multishot count input'''
        self._multishot_count = int(widget.get_value())

    def multishot_toggled(self, widget):
        '''Toggle multishot'''
        self._multishot_mode = widget.get_active()
        # This is intended to support an auto-multishot mode, like
        # a low-framerate screen recording. Disabled for now as I'm
        # not sure this is a feature gscreenshot needs.
        #self._view.show_multishot_count(self._multishot_mode)

    def selected_cursor_changed(self, widget):
        '''Handle a change to the selected cursor'''
        self._cursor_selection = widget.get_model()[widget.get_active()][2]

    def on_button_all_clicked(self, *_):
        '''Take a screenshot of the full screen'''
        self.take_screenshot(
            self._app.screenshot_full_display
            )

    def on_button_window_clicked(self, *args):
        '''Take a screenshot of a window'''
        self._button_select_area_or_window_clicked(args)

    def on_button_selectarea_clicked(self, *args):
        '''Take a screenshot of an area'''
        self._button_select_area_or_window_clicked(args)

    def _button_select_area_or_window_clicked(self, *_):
        '''Take a screenshot of an area or window'''
        self.take_screenshot(
            self._app.screenshot_selected
            )

    def on_preview_prev_clicked(self, *_):
        '''Handle a click of the "previous" button on the preview'''
        screenshot_collection = self._app.get_screenshot_collection()
        screenshot_collection.cursor_prev()
        self._show_preview()
        self._view.update_gallery_controls(
            show_next=screenshot_collection.has_next(),
            show_previous=screenshot_collection.has_previous()
        )

    def on_preview_next_clicked(self, *_):
        '''Handle a click of the "next" button on the preview'''
        screenshot_collection = self._app.get_screenshot_collection()
        screenshot_collection.cursor_next()
        self._show_preview()
        self._view.update_gallery_controls(
            show_next=screenshot_collection.has_next(),
            show_previous=screenshot_collection.has_previous()
        )

    def on_button_saveall_clicked(self, *_):
        '''Handle the "save all" button'''
        saved = False
        cancelled = False
        save_dialog = FileSaveDialog(
            self._app.get_time_foldername(),
            self._app.get_last_save_directory(),
            self._view.get_window()
        )

        while not (saved or cancelled):
            fname = self._view.run_dialog(save_dialog)
            if fname is not None:
                self._view.set_busy()
                saved = self._app.save_screenshot_collection(fname)
                self._view.set_ready()
            else:
                cancelled = True

        if saved:
            self._view.flash_status_icon("document-save")

    def on_button_saveas_clicked(self, *_):
        '''Handle the saveas button'''
        saved = False
        cancelled = False

        if self._multishot_mode:

            save_dialog = FileSaveDialog(
                self._app.get_time_foldername(),
                self._app.get_last_save_directory(),
                self._view.get_window()
            )

            while not (saved or cancelled):
                fname = self._view.run_dialog(save_dialog)
                if fname is not None:
                    self._view.set_busy()
                    saved = self._app.save_screenshot_collection(fname)
                    self._view.set_ready()
                else:
                    cancelled = True

        else:
            save_dialog = FileSaveDialog(
                    self._app.get_time_filename(),
                    self._app.get_last_save_directory(),
                    self._view.get_window()
                    )

            while not (saved or cancelled):
                fname = self._view.run_dialog(save_dialog)
                if fname is not None:
                    saved = self._app.save_last_image(fname)
                else:
                    cancelled = True

        if saved:
            self._view.flash_status_icon("document-save")

    def on_button_openwith_clicked(self, *_):
        '''Handle the "open with" button'''
        self._view.flash_status_icon(Gtk.STOCK_EXECUTE)
        fname = self._app.save_and_return_path()

        if fname is None:
            return

        appchooser = OpenWithDialog()

        self._view.run_dialog(appchooser)

        appinfo = appchooser.appinfo

        if appinfo is not None:
            if appinfo.launch_uris(["file://"+fname], None):

                if self._multishot_mode:
                    screenshots = self._app.get_screenshot_collection()
                    current = screenshots.cursor_current()
                    if current is not None:
                        screenshots.remove(current)

                    current = screenshots.cursor_current()
                    if current is not None:
                        self._view.update_gallery_controls(
                            show_next=screenshots.has_next(),
                            show_previous=screenshots.has_previous()
                        )
                        self._show_preview()

                        return
                self.quit(None)

    def on_button_copy_clicked(self, *_):
        """
        Copy the current screenshot to the clipboard
        """
        img = self._app.get_last_image()

        if img is None:
            return False

        pixbuf = self._image_to_pixbuf(img)

        if not self._view.copy_to_clipboard(pixbuf):
            if not self._app.copy_last_screenshot_to_clipboard():
                warning_dialog = WarningDialog(
                    i18n("Your clipboard doesn't support persistence and xclip isn't available."),
                    self._view.get_window())
                self._view.run_dialog(warning_dialog)
                return False

        self._view.flash_status_icon("edit-copy")
        return True

    def on_button_copy_and_close_clicked(self, *_):
        """
        Copy the current screenshot to the clipboard and
        close gscreenshot
        """
        if self.on_button_copy_clicked():
            if self._multishot_mode:
                screenshots = self._app.get_screenshot_collection()
                current = screenshots.cursor_current()
                if current is not None:
                    screenshots.remove(current)

                current = screenshots.cursor_current()
                if current is not None:
                    self._view.update_gallery_controls(
                        show_next=screenshots.has_next(),
                        show_previous=screenshots.has_previous()
                    )
                    self._show_preview()

                    return

            self.quit(None)

    def on_button_open_clicked(self, *_):
        '''Handle the open button'''
        success = self._app.open_last_screenshot()
        if not success:
            dialog = WarningDialog(
                i18n("Please install xdg-open to open files."),
                self._view.get_window())
            self._view.run_dialog(dialog)
        else:
            self._view.flash_status_icon("document-open")
            if self._multishot_mode:
                screenshots = self._app.get_screenshot_collection()
                current = screenshots.cursor_current()
                if current is not None:
                    screenshots.remove(current)

                current = screenshots.cursor_current()
                if current is not None:
                    self._view.update_gallery_controls(
                        show_next=screenshots.has_next(),
                        show_previous=screenshots.has_previous()
                    )
                    self._show_preview()

                    return
            self.quit(None)

    def on_button_about_clicked(self, *_):
        '''Handle the about button'''
        about = Gtk.AboutDialog(transient_for=self._view.get_window())

        authors = self._app.get_program_authors()
        about.set_authors(authors)

        description = i18n(self._app.get_program_description())
        description += "\n" + i18n("Using {0} screenshot backend").format(
            self._app.get_screenshooter_name()
        )
        description += "\n" + i18n("Available features: {0}").format(
            ", ".join(self._app.get_capabilities())
        )

        about.set_comments(i18n(description))

        website = self._app.get_program_website()
        about.set_website(website)
        about.set_website_label(website)

        name = self._app.get_program_name()
        about.set_program_name(name)
        about.set_title(i18n("About"))

        license_text = self._app.get_program_license_text()
        about.set_license(license_text)

        version = self._app.get_program_version()
        about.set_version(version)

        about.set_logo(
                Gtk.gdk.pixbuf_new_from_file(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'gscreenshot.png'
                        )
                    )
                )

        self._view.run_dialog(about)

    def on_fullscreen_toggle(self):
        '''Handle the window getting toggled to fullscreen'''
        self._view.toggle_fullscreen()

    def on_button_quit_clicked(self, widget=None):
        '''Handle the quit button'''
        self.quit(widget)

    def on_window_main_destroy(self, widget=None):
        '''Handle the titlebar close button'''
        self.quit(widget)

    def on_window_resize(self, *_):
        '''Handle window resizes'''
        if self._can_resize:
            self._view.resize()
            self._show_preview()

    def quit(self, *_):
        '''Exit the app'''
        self._app.quit()

    def _image_to_pixbuf(self, image):
        descriptor = io.BytesIO()
        image = image.convert("RGB")
        image.save(descriptor, "ppm")
        contents = descriptor.getvalue()
        descriptor.close()
        loader = Gtk.gdk.PixbufLoader("pnm")
        loader.write(contents)
        pixbuf = loader.get_pixbuf()
        try:
            loader.close()
        except GLib.GError:
            pass
        return pixbuf

    def _show_preview(self):
        height, width = self._view.get_preview_dimensions()

        preview_img = self._app.get_thumbnail(width, height)

        self._view.update_preview(self._image_to_pixbuf(preview_img))


class OpenWithDialog(Gtk.AppChooserDialog):
    '''The "Open With" dialog'''

    def __init__(self, parent=None):

        Gtk.AppChooserDialog.__init__(self, content_type="image/png", parent=parent)
        self.set_title(i18n("Choose an Application"))
        self.connect("response", self._on_response)
        self.appinfo = None

    def _on_response(self, dialog, response):
        if response == Gtk.ResponseType.OK:
            self.appinfo = self.get_app_info()
        else:
            self.appinfo = None


class FileSaveDialog(object):
    '''The 'save as' dialog'''
    def __init__(self, default_filename=None, default_folder=None, parent=None):
        self.default_filename = default_filename
        self.default_folder = default_folder
        self.parent = parent

    def run(self):
        ''' Run the dialog'''
        filename = self.request_file()

        return filename

    def request_file(self):
        '''Run the file selection dialog'''
        chooser = Gtk.FileChooserDialog(
                transient_for=self.parent,
                title=None,
                action=Gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(
                    Gtk.STOCK_CANCEL,
                    Gtk.RESPONSE_CANCEL,
                    Gtk.STOCK_SAVE,
                    Gtk.RESPONSE_OK
                    )
                )

        if self.default_filename is not None:
            chooser.set_current_name(self.default_filename)

        if self.default_folder is not None:
            chooser.set_current_folder(self.default_folder)

        chooser.set_do_overwrite_confirmation(True)

        response = chooser.run()

        if response == Gtk.RESPONSE_OK:
            return_value = chooser.get_filename()
        else:
            return_value = None

        chooser.destroy()
        return return_value


class WarningDialog():
    '''A warning dialog'''

    def __init__(self, message, parent=None):
        self.parent = parent
        self.message_dialog = Gtk.MessageDialog(
                parent,
                None,
                Gtk.MESSAGE_WARNING,
                Gtk.BUTTONS_OK,
                message
                )

    def run(self):
        '''Run the warning dialog'''
        if self.parent is not None:
            self.parent.set_sensitive(False)

        self.message_dialog.run()
        self.message_dialog.destroy()

        if self.parent is not None:
            self.parent.set_sensitive(True)


def main():
    '''The main function for the GTK frontend'''

    try:
        application = Gscreenshot()
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

    # Improves startup performance by kicking off a screenshot
    # as early as we can in the background.
    screenshot_thread = threading.Thread(
        target=application.screenshot_full_display
    )
    screenshot_thread.daemon = True
    screenshot_thread.start()

    builder = Gtk.Builder()
    builder.set_translation_domain('gscreenshot')
    builder.add_from_string(resource_string(
        'gscreenshot.resources.gui.glade', 'main.glade').decode('UTF-8'))

    window = builder.get_object('window_main')

    waited = 0
    while application.get_last_image() is None and waited < 8:
        sleep(.01)
        waited += .1

    capabilities = application.get_capabilities()
    view = View(window, builder, capabilities)

    presenter = Presenter(
            application,
            view
            )

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

    keymappings = {
        Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('Escape')):
            presenter.on_button_quit_clicked,
        Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('F11')):
            presenter.on_fullscreen_toggle
    }
    presenter.set_keymappings(keymappings)

    view.connect_signals(presenter)
    view.run()

    GObject.threads_init() # Start background threads.
    Gtk.main()

if __name__ == "__main__":
    main()
