#pylint: disable=unused-argument
#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
#pylint: disable=too-many-statements
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
from gscreenshot.frontend.gtk.dialogs import OpenWithDialog, WarningDialog, FileSaveDialog, FileOpenDialog
from gscreenshot.frontend.gtk.view import View
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError
from gscreenshot.screenshot.effects.crop import CropEffect

pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')
from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject
from gi.repository import GLib

i18n = gettext.gettext


class Presenter(object):
    '''Presenter class for the GTK frontend'''

    __slots__ = ('_delay', '_app', '_hide',
            '_view', '_keymappings', '_capture_cursor',
            '_cursor_selection', '_overwrite_mode')

    _delay: int
    _app: Gscreenshot
    _hide: bool
    _view: View
    _keymappings: dict
    _capture_cursor: bool
    _overwrite_mode: bool
    _cursor_selection: str

    def __init__(self, application: Gscreenshot, view: View):
        self._app = application
        self._view = view
        self._delay = 0
        self._hide = True
        self._capture_cursor = False
        self._show_preview()
        self._view.show_cursor_options(self._capture_cursor)
        self._keymappings = {}
        self._overwrite_mode = True

        cursors = self._app.get_available_cursors()
        cursors[i18n("custom")] = None

        self._cursor_selection = 'theme'

        self._view.update_available_cursors(
                cursors
                )

    def _begin_take_screenshot(self, app_method, **args):
        app_method(delay=self._delay,
            capture_cursor=self._capture_cursor,
            cursor_name=self._cursor_selection,
            overwrite=self._overwrite_mode,
            **args)

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

    def take_screenshot(self, app_method: typing.Callable, **args):
        '''Take a screenshot using the passed app method'''
        self._view.set_busy()

        if self._hide:
            self._view.hide()

        # Do work in background thread.
        # Taken from here: https://wiki.gnome.org/Projects/PyGObject/Threading
        _thread = threading.Thread(target=self._begin_take_screenshot(app_method, **args))
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

    def overwrite_mode_toggled(self, widget):
        '''Toggle overwrite or multishot mode'''
        self._overwrite_mode = widget.get_active()

    def delay_value_changed(self, widget):
        '''Handle a change with the screenshot delay input'''
        self._delay = widget.get_value()

    def selected_cursor_changed(self, widget):
        '''Handle a change to the selected cursor'''
        try:
            cursor_selection = widget.get_model()[widget.get_active()][2]
        except IndexError:
            return

        if cursor_selection == "custom":

            filter:Gtk.FileFilter = Gtk.FileFilter()
            supported_formats = self._app.get_supported_formats()
            [filter.add_mime_type(
                f"image/{format}") for format in supported_formats
                if format not in ["pdf"]
            ]

            chooser = FileOpenDialog(
                filter=filter
            )
            chosen = None
            cancelled = False
            while not (chosen or cancelled):
                chosen = self._view.run_dialog(chooser)
                if chosen is None:
                    cancelled = True

            if chosen:
                try:
                    cursor_name = self._app.register_stamp_image(chosen)
                except Exception as e:
                    warning = WarningDialog(f"Unable to open {chosen}")
                    self._view.run_dialog(warning)
                    return

                cursors = self._app.get_available_cursors()
                cursors[i18n("custom")] = None

                self._view.update_available_cursors(
                    cursors,
                    cursor_name
                )
                if cursor_name:
                    cursor_selection = cursor_name

        self._cursor_selection = cursor_selection

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

    def on_use_last_region_clicked(self, *_):
        '''
        Take a screenshot with the same region as the
        screenshot under the cursor, if applicable
        '''
        last_screenshot = self._app.get_screenshot_collection().cursor_current()
        region = None

        if last_screenshot is not None:
            effects = last_screenshot.get_effects()
            crop_effect = next((i for i in effects if isinstance(i, CropEffect)), None)
            if crop_effect and "region" in crop_effect.meta:
                region = crop_effect.meta["region"]

        self.take_screenshot(
            self._app.screenshot_selected,
            region=region
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

    def effect_checkbox_handler(self, widget, effect):
        '''
        Handles toggling effects on and off
        '''
        screenshot = self._app.get_screenshot_collection().cursor_current()
        if screenshot is None:
            return

        if widget.get_active():
            effect.enable()
        else:
            effect.disable()

        self._show_preview()

    def on_button_saveas_clicked(self, *_):
        '''Handle the saveas button'''
        saved = False
        cancelled = False

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

    def on_button_save_all_clicked(self, *_):
        '''Handle the "save all" button'''
        saved = False
        cancelled = False
        save_dialog = FileSaveDialog(
            self._app.get_time_foldername(),
            self._app.get_last_save_directory(),
            self._view.get_window(),
            choose_directory=True
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

        capabilities_formatted = []
        for capability, provider in self._app.get_capabilities().items():
            capabilities_formatted.append(f"{i18n(capability)} ({provider})")
        description += "\n" + i18n("Available features: {0}").format(
            "\n ".join(capabilities_formatted)
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

        preview_img = self._app.get_thumbnail(width, height, with_border=True)

        self._view.update_preview(self._image_to_pixbuf(preview_img))


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

    builder = Gtk.Builder()
    builder.set_translation_domain('gscreenshot')
    builder.add_from_string(resource_string(
        'gscreenshot.resources.gui.glade', 'main.glade').decode('UTF-8'))

    window = builder.get_object('window_main')

    capabilities = application.get_capabilities()
    view = View(window, builder, capabilities)

    presenter = Presenter(
            application,
            view
            )

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

    keymappings = {
        Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('Escape')):
            presenter.on_button_quit_clicked,
        Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('F11')):
            presenter.on_fullscreen_toggle,
        Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('Right')):
            presenter.on_preview_next_clicked,
        Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('Left')):
            presenter.on_preview_prev_clicked
        # here for reference - this is configured in Glade
        #Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('INSERT')):
        #    presenter.overwrite_mode_toggled
    }
    presenter.set_keymappings(keymappings)

    view.connect_signals(presenter)
    view.run()

    GObject.threads_init() # Start background threads.
    Gtk.main()

if __name__ == "__main__":
    main()
