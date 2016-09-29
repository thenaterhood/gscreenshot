import io
from gi import pygtkcompat

pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')

from gi.repository import Gdk
from gi.repository import Gtk as gtk
from gscreenshot import Gscreenshot

from pkg_resources import resource_string
from time import sleep


class GscreenshotWindow(object):

    #--------------------------------------------
    # initialization
    #--------------------------------------------

    def __init__(self, application):

        self.builder = gtk.Builder()
        self.application = application

        self.builder.add_from_string(resource_string(
            'gscreenshot.resources.gui.glade', 'main.glade').decode("UTF-8"))

        self.window = self.builder.get_object('window_main')

        # show the (main) window in the center of the screen
        self.window.set_position(gtk.WIN_POS_CENTER)

        # create a signal dictionary and connect it to the handler functions
        dic = {
            "on_window_main_destroy": self.quit,
            "on_button_all_clicked": self.button_all_clicked,
            "on_button_window_clicked": self.button_select_area_or_window_clicked,
            "on_button_selectarea_clicked": self.button_select_area_or_window_clicked,
            "on_button_saveas_clicked": self.button_saveas_clicked,
            "on_button_about_clicked": self.button_about_clicked,
            "on_button_quit_clicked": self.button_quit_clicked,
            "on_button_copy_clicked": self.handle_copy_action}

        self.builder.connect_signals(dic)

        accel = gtk.AccelGroup()
        accel.connect(Gdk.keyval_from_name('S'), Gdk.ModifierType.CONTROL_MASK, 0, self.button_saveas_clicked)
        accel.connect(Gdk.keyval_from_name('C'), Gdk.ModifierType.CONTROL_MASK, 0, self.handle_copy_action)
        self.window.add_accel_group(accel)

        self.window.connect("key-press-event", self.handle_keypress)

        # create objects from selected widgets in the main window
        self.image_preview = self.builder.get_object("image1")
        self.hide_check = self.builder.get_object("checkbutton1")
        self.delay_setter = self.builder.get_object("spinbutton1")
        self.button_saveas = self.builder.get_object("button_saveas")

        screenshot = self.application.screenshot_full_display()
        self.show_preview(screenshot)

    #--------------------------------------------
    # signal handlers
    #--------------------------------------------

    def handle_keypress(self, widget=None, event=None, *args):
        """
        This method handles individual keypresses. These are
        handled separately from accelerators (which include
        modifiers).
        """
        shortcuts = {
                gtk.gdk.keyval_to_lower(gtk.gdk.keyval_from_name('Escape')): self.button_quit_clicked
                }

        if event.keyval in shortcuts:
            shortcuts[event.keyval]()

    def take_screenshot(self, hide, delay, app_method):
        if hide:
            self.window.hide()

        while gtk.events_pending():
            gtk.main_iteration()

        sleep(0.2)
        screenshot = app_method(delay)
        self.show_preview(screenshot)

        self.window.show_all()

    #
    #---- button_all_clicked  :grab a screenshot of the whole screen
    #
    def button_all_clicked(self, *args):

        self.take_screenshot(
            self.hide_check.get_active(),
            self.delay_setter.get_value(),
            self.application.screenshot_full_display
            )

    def button_select_area_or_window_clicked(self, *args):

        self.take_screenshot(
            self.hide_check.get_active(),
            self.delay_setter.get_value(),
            self.application.screenshot_selected
            )
    #
    #---- button_saveas_clicked  :save the grabbed screenshot
    #
    def button_saveas_clicked(self, *args):
        # make the main window unsensitive while saving your image
        self.window.set_sensitive(False)

        self.handle_save_action()

        self.window.set_sensitive(True)

    def handle_save_action(self):
        saved = False
        cancelled = False
        save_dialog = FileSaveDialog(self.application.get_time_filename())

        while not (saved or cancelled):
            fname = save_dialog.run()
            if fname is not None:
                saved = self.application.save_last_image(fname)
            else:
                cancelled = True

    def handle_copy_action(self, *args):
        """
        Copy the current screenshot to the clipboard
        """

        clipboard = gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        img = self.application.get_last_image()
        pixbuf = self._image_to_pixbuf(img)
        clipboard.set_image(pixbuf)
        clipboard.store()

    #
    #---- button_about_clicked  :show the "about" dialog
    #
    def button_about_clicked(self, *args):
        # make the main window unsensitive while viewing the "about"
        # information
        self.window.set_sensitive(False)

        # send the "about" dialog object a request to create it's window
        about = gtk.AboutDialog()

        authors = [
            "Nate Levesque <public@thenaterhood.com>",
            "Original Author (2006)",
            "matej.horvath <matej.horvath@gmail.com>"
        ]
        about.set_authors(authors)
        about.set_comments("A simple GUI frontend for scrot")
        about.set_website("https://github.com/thenaterhood/gscreenshot")
        about.set_website_label("github.com/thenaterhood/gscreenshot")
        about.set_program_name("gscreenshot")
        about.set_title("About gscreenshot")
        about.set_license(
            resource_string('gscreenshot.resources', 'LICENSE').decode("UTF-8"))
        about.set_logo_icon_name("gscreenshot")
        about.connect("response", self.on_about_close)

        about.show()

    def on_about_close(self, action, *args):
        action.destroy()
        self.window.set_sensitive(True)

    #
    #---- button_quit_clicked  :quit the application
    #
    def button_quit_clicked(self, widget=None):
        self.quit(widget)

    def quit(self, widget):
        self.application.quit()

    #--------------------------------------------
    # other functions
    #--------------------------------------------
    def _image_to_pixbuf(self, image):
        fd = io.BytesIO()
        image.save(fd, "ppm")
        contents = fd.getvalue()
        fd.close()
        loader = gtk.gdk.PixbufLoader("pnm")
        loader.write(contents)
        pixbuf = loader.get_pixbuf()
        loader.close()
        return pixbuf

    def show_preview(self, image):
        # create an image buffer (pixbuf) and insert the grabbed image
        previewPixbuf = self._image_to_pixbuf(image)

        allocation = self.image_preview.get_allocation()

        thumbnail = self.application.get_thumbnail(allocation.width, allocation.height, image)
        previewPixbuf = self._image_to_pixbuf(thumbnail)

        # set the image_preview widget to the preview image size (previewWidth,
        # previewHeight)
        self.image_preview.set_size_request(allocation.width, allocation.height)

        # view the previewPixbuf in the image_preview widget
        self.image_preview.set_from_pixbuf(previewPixbuf)

class FileSaveDialog(object):

    def __init__(self, default_filename=None):
        self.default_filename = default_filename

    def run(self):

        filename = self.request_file()

        return filename

    def request_file(self):
        chooser = gtk.FileChooserDialog(
                title=None,
                action=gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(
                    gtk.STOCK_CANCEL,
                    gtk.RESPONSE_CANCEL,
                    gtk.STOCK_SAVE,
                    gtk.RESPONSE_OK
                    )
                )

        if self.default_filename is not None:
            chooser.set_current_name(self.default_filename)

        chooser.set_do_overwrite_confirmation(True)

        response = chooser.run()

        if (response == gtk.RESPONSE_OK):
            return_value = chooser.get_filename()
        else:
            return_value = None

        chooser.destroy()
        return return_value

def main():
    # create the main_window object and window
    app = Gscreenshot()
    GscreenshotWindow(app)
    gtk.main()
#-------------------------------------------------------------------------

if __name__ == "__main__":
    main()
