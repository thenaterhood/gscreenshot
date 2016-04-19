#!/usr/bin/env python

#--------------------------------------------
# gscreenshot.py
# Matej Horvath <matej.horvath@gmail.com>
# 3. september 2006
#
# Adopted August 9, 2015
# Nate Levesque <public@thenaterhood.com>
# - Retrieved from Google Code
# - Updated to use modern libraries and formats
# - Further changes will be noted in release notes
#--------------------------------------------
import io
from gi import pygtkcompat

pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')

from gi.repository import Gdk
from gi.repository import Gtk as gtk
import os
from pkg_resources import resource_string
from PIL import Image
import threading
from time import sleep
import subprocess
import sys
import tempfile
from datetime import datetime


class main_window(threading.Thread):

    #--------------------------------------------
    # initialization
    #--------------------------------------------

    def __init__(self):

        self.builder = gtk.Builder()
        self.scrot = Scrot()

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

        self.scrot.grab_fullscreen()
        self.show_preview()

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

    #
    #---- button_all_clicked  :grab a screenshot of the whole screen
    #
    def button_all_clicked(self, *args):
        # check if the window should be hidden while grabbing screenshot
        if self.hide_check.get_active():
            # hide the window to grab the screenshot without it
            self.window.hide()

        # wait until the window is completely hidden
        while gtk.events_pending():
            gtk.main_iteration()

        # grab the screenshot
        sleep(0.2)
        self.scrot.grab_fullscreen(self.delay_setter.get_value())

        # show the window
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.show_all()

        # create and show a preview of the grabbed screenshot
        self.show_preview()

    def button_select_area_or_window_clicked(self, *args):
        # check if the window should be hidden while grabbing screenshot
        if self.hide_check.get_active():
            # hide the window to grab the screenshot without it
            self.window.hide()

        # wait until the window is completely hidden
        while gtk.events_pending():
            gtk.main_iteration()

        # grab the screenshot
        self.scrot.grab_selection(self.delay_setter.get_value())

        # show the window
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.show_all()

        # create and show a preview of the grabbed screenshot
        self.show_preview()

    #
    #---- button_saveas_clicked  :save the grabbed screenshot
    #
    def button_saveas_clicked(self, *args):
        # make the main window unsensitive while saving your image
        self.window.set_sensitive(False)

        im = self.scrot.get_image()

        save_handler = FileSaveHandler()
        save_handler.run(im)

        self.window.set_sensitive(True)

    def handle_copy_action(self, *args):
        """
        Copy the current screenshot to the clipboard
        """

        clipboard = gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        img = self.scrot.get_image()
        pixbuf = self._image_to_pixbuf(img)
        print(pixbuf)
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
        about.set_logo_icon_name("screenshot")
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
        sys.exit(0)

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

    def show_preview(self):
        # create an image buffer (pixbuf) and insert the grabbed image
        previewPixbuf = self._image_to_pixbuf(self.scrot.get_image())

        allocation = self.image_preview.get_allocation()
        # resolve the preview image width and height
        imageHeight = previewPixbuf.get_height()
        imageWidth = previewPixbuf.get_width()

        resize_ratio = min(allocation.height/imageHeight, allocation.width/imageWidth)

        previewHeight = imageHeight * resize_ratio
        previewWidth = imageWidth * resize_ratio

        previewHeight = max(allocation.height, previewHeight)
        # Not required on python3, but resolves a bug in python2
        previewWidth = max(allocation.width, previewWidth)

        # resize the previewPixbuf to previewWidth, previewHeight
        previewPixbuf = previewPixbuf.scale_simple(
            previewWidth, previewHeight, gtk.gdk.INTERP_BILINEAR)

        # set the image_preview widget to the preview image size (previewWidth,
        # previewHeight)
        self.image_preview.set_size_request(previewWidth, previewHeight)

        # view the previewPixbuf in the image_preview widget
        self.image_preview.set_from_pixbuf(previewPixbuf)

class Scrot(object):

    __slots__ = ('image', 'tempfile')

    def __init__(self):
        self.image = None
        self.tempfile = os.path.join(
                tempfile.gettempdir(),
                str(os.getpid()) + ".png"
                )

    def get_image(self):
        return self.image

    def grab_fullscreen(self, delay=0):
        self._call_scrot(['-d', str(delay)])

    def grab_selection(self, delay=0):
        self._call_scrot(['-d', str(delay), '-s'])

    def grab_window(self, delay=0):
        self.grab_selection(delay)

    def _call_scrot(self, params=None):

        # This is safer than passing an empty
        # list as a default value
        if params is None:
            params = []

        params = ['scrot', self.tempfile] + params
        subprocess.check_output(params)

        self.image = Image.open(self.tempfile)
        os.unlink(self.tempfile)

class FileSaveHandler(object):

    def __init__(self):
        pass

    def run(self, image):
        filename = self.request_file()

        if filename is None:
            return

        self.save_file(filename, image)

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

        chooser.set_current_name(self._build_filename())
        chooser.set_do_overwrite_confirmation(True)

        response = chooser.run()

        if (response == gtk.RESPONSE_OK):
            return_value = chooser.get_filename()
        else:
            return_value = None

        chooser.destroy()
        return return_value

    def _build_filename(self):
        d = datetime.now()
        return datetime.strftime(d, "gscreenshot_%Y-%m-%d-%H%M%S.png")

    def save_file(self, filename, im):
        actual_file_ext = os.path.splitext(filename)[1][1:].lower()

        if actual_file_ext == 'jpg':
            actual_file_ext = 'jpeg'

        supported_formats = [
            'bmp', 'eps', 'gif', 'jpeg', 'pcx', 'pdf', 'ppm', 'tiff', 'png']

        if actual_file_ext in supported_formats:
            im.save(filename, actual_file_ext.upper())

def main():
    # create the main_window object and window
    gscreenshot = main_window()
    gtk.main()
#-------------------------------------------------------------------------

if __name__ == "__main__":
    main()
