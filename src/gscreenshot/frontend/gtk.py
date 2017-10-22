import io
import os
import sys
import threading
from gi import pygtkcompat

pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')

from gi.repository import Gdk
from gi.repository import Gtk
from gi.repository import GObject

from gscreenshot import Gscreenshot
from gscreenshot.frontend import SignalHandler
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError

from pkg_resources import resource_string, resource_filename
from time import sleep


class Controller(object):

    __slots__ = ('_delay', '_app', '_hide', '_window', '_preview')

    def __init__(self, application, builder):
        self._app = application
        self._window = builder.get_object('window_main')
        self._preview = builder.get_object('image1')
        self._delay = 0
        self._hide = True

        self._app.screenshot_full_display()
        self._show_preview(self._app.get_last_image())

    def _begin_take_screenshot(self, app_method):
        screenshot = app_method(self._delay)

        # Re-enable UI on the UI thread.
        GObject.idle_add(self._end_take_screenshot, screenshot)

    def _end_take_screenshot(self, screenshot):
        self._show_preview(screenshot)

        self._window.set_sensitive(True)
        self._window.set_opacity(1)
        self._window.show_all()

    def take_screenshot(self, app_method):
        self._window.set_sensitive(False)
        if self._hide:
            # We set the opacity to 0 because hiding the window is
            # subject to window closing effects, which can take long
            # enough that the window will still appear in the screenshot
            self._window.set_opacity(0)
            self._window.hide()

        while Gtk.events_pending():
            Gtk.main_iteration()

        sleep(0.2)

        # Do work in background thread.
        # Taken from here: https://wiki.gnome.org/Projects/PyGObject/Threading
        _thread = threading.Thread(target=self._begin_take_screenshot(app_method))
        _thread.daemon = True
        _thread.start()

    def handle_keypress(self, widget=None, event=None, *args):
        """
        This method handles individual keypresses. These are
        handled separately from accelerators (which include
        modifiers).
        """
        shortcuts = {
                Gtk.gdk.keyval_to_lower(Gtk.gdk.keyval_from_name('Escape')): self.on_button_quit_clicked
                }

        if event.keyval in shortcuts:
            shortcuts[event.keyval]()

    def hide_window_toggled(self, widget):
        self._hide = widget.get_active()

    def delay_value_changed(self, widget):
        self._delay = widget.get_value()

    def on_button_all_clicked(self, *args):

        self.take_screenshot(
            self._app.screenshot_full_display
            )

    def on_button_window_clicked(self, *args):
        self._button_select_area_or_window_clicked(args)

    def on_button_selectarea_clicked(self, *args):
        self._button_select_area_or_window_clicked(args)

    def _button_select_area_or_window_clicked(self, *args):

        self.take_screenshot(
            self._app.screenshot_selected
            )

    def on_button_saveas_clicked(self, *args):
        # make the main window unsensitive while saving your image
        self._window.set_sensitive(False)

        self.handle_save_action()

        self._window.set_sensitive(True)

    def handle_save_action(self):
        saved = False
        cancelled = False
        save_dialog = FileSaveDialog(
                self._app.get_time_filename(),
                self._app.get_last_save_directory(),
                self._window
                )

        while not (saved or cancelled):
            fname = save_dialog.run()
            if fname is not None:
                saved = self._app.save_last_image(fname)
            else:
                cancelled = True

    def on_button_openwith_clicked(self, *args):
        self._window.set_sensitive(False)

        self.handle_openwith_action()

        self._window.set_sensitive(True)

    def handle_openwith_action(self):
        fname = self._app.save_and_return_path()
        appchooser = OpenWithDialog()
        appchooser.run()
        appinfo = appchooser.appinfo
        appchooser.destroy()

        if (appinfo is not None):
            print(fname)
            appinfo.launch_uris(["file://"+fname], None)

    def on_button_copy_clicked(self, *args):
        """
        Copy the current screenshot to the clipboard
        """
        print(args)
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        img = self._app.get_last_image()
        pixbuf = self._image_to_pixbuf(img)
        clipboard.set_image(pixbuf)
        clipboard.store()

    def on_button_open_clicked(self, *args):
        success = self._app.open_last_screenshot()
        if (not success):
            md = Gtk.MessageDialog(self._window,
                Gtk.DIALOG_DESTROY_WITH_PARENT, Gtk.MESSAGE_WARNING,
                Gtk.BUTTONS_OK, "Please install xdg-open to open files.")
            md.run()
            md.destroy()

    def on_button_about_clicked(self, *args):
        # make the main window unsensitive while viewing the "about"
        # information
        self._window.set_sensitive(False)

        # send the "about" dialog object a request to create it's window
        about = Gtk.AboutDialog(transient_for=self._window)

        authors = self._app.get_program_authors()
        about.set_authors(authors)

        description = self._app.get_program_description()
        description += "\nCurrently using " + self._app.get_screenshooter_name()
        about.set_comments(description)

        website = self._app.get_program_website()
        about.set_website(website)
        about.set_website_label(website)

        name = self._app.get_program_name()
        about.set_program_name(name)
        about.set_title("About gscreenshot")

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
        about.connect("response", self.on_about_close)

        about.show()

    def on_about_close(self, action, *args):
        action.destroy()
        self._window.set_sensitive(True)

    def on_button_quit_clicked(self, widget=None):
        self.quit(widget)

    def on_window_main_destroy(self, widget=None):
        self.quit(widget)

    def on_window_resize(self, *kwargs):
        self._show_preview(self._app.get_last_image())

    def quit(self, widget):
        self._app.quit()

    def _image_to_pixbuf(self, image):
        fd = io.BytesIO()
        image = image.convert("RGB")
        image.save(fd, "ppm")
        contents = fd.getvalue()
        fd.close()
        loader = Gtk.gdk.PixbufLoader("pnm")
        loader.write(contents)
        pixbuf = loader.get_pixbuf()
        loader.close()
        return pixbuf

    def _show_preview(self, image):
        # create an image buffer (pixbuf) and insert the grabbed image
        if (image is None):
            image = self._app.get_app_icon()

        previewPixbuf = self._image_to_pixbuf(image)

        allocation = self._preview.get_allocation()
        window_size = self._window.get_size()

        allocation_size = (allocation.height, allocation.width)
        window_size = (window_size.height*.48, window_size.width*.98)

        window_dimension = window_size[0] * window_size[1]
        allocated_dimension = allocation_size[0] * allocation_size[1]
        height = allocation_size[0]
        width = allocation_size[1]
        if (window_dimension < allocated_dimension):
            height = window_size[0]
            width = window_size[1]

        thumbnail = self._app.get_thumbnail(width, height, image)
        previewPixbuf = self._image_to_pixbuf(thumbnail)

        # set the image_preview widget to the preview image size (previewWidth,
        # previewHeight)
        self._preview.set_size_request(width, height)

        # view the previewPixbuf in the image_preview widget
        self._preview.set_from_pixbuf(previewPixbuf)


class OpenWithDialog(Gtk.AppChooserDialog):

    def __init__(self, parent=None):

        Gtk.AppChooserDialog.__init__(self, content_type="image/png", parent=parent)
        self.set_title("Choose an Application")
        self.connect("response", self._on_response)
        self.appinfo = None

    def _on_response(self, dialog, response):
        if (response == Gtk.ResponseType.OK):
            self.appinfo = self.get_app_info()
        else:
            self.appinfo = None


class FileSaveDialog(object):

    def __init__(self, default_filename=None, default_folder=None, parent=None):
        self.default_filename = default_filename
        self.default_folder = default_folder
        self.parent = parent

    def run(self):

        filename = self.request_file()

        return filename

    def request_file(self):
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

        if (response == Gtk.RESPONSE_OK):
            return_value = chooser.get_filename()
        else:
            return_value = None

        chooser.destroy()
        return return_value


def main():
    try:
        application = Gscreenshot()
    except NoSupportedScreenshooterError:
        md = Gtk.MessageDialog(None,
            Gtk.DIALOG_DESTROY_WITH_PARENT, Gtk.MESSAGE_WARNING,
            Gtk.BUTTONS_OK, "gscreenshot couldn't run. No supported screenshot utility could be found.")
        md.run()
        md.destroy()
        sys.exit(1)


    builder = Gtk.Builder()
    builder.add_from_string(resource_string(
        'gscreenshot.resources.gui.glade', 'main.glade').decode('UTF-8'))

    window = builder.get_object('window_main')
    window.set_position(Gtk.WIN_POS_CENTER)

    handler = Controller(
            application,
            builder,
            )

    accel = Gtk.AccelGroup()
    accel.connect(Gdk.keyval_from_name('S'), Gdk.ModifierType.CONTROL_MASK, 0, handler.on_button_saveas_clicked)
    accel.connect(Gdk.keyval_from_name('C'), Gdk.ModifierType.CONTROL_MASK, 0, handler.on_button_copy_clicked)
    accel.connect(Gdk.keyval_from_name('O'), Gdk.ModifierType.CONTROL_MASK, 0, handler.on_button_open_clicked)
    window.add_accel_group(accel)
    window.connect("key-press-event", handler.handle_keypress)

    builder.connect_signals(handler)

    window.connect("check-resize", handler.on_window_resize)
    window.set_icon_from_file(resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png'))

    with SignalHandler():
        GObject.threads_init(); # Start background threads.
        window.show_all()
        Gtk.main()

if __name__ == "__main__":
    main()
