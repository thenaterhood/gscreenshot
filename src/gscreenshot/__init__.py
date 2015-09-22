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

import sys
import os
from gi import pygtkcompat
pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')

import gtk
from PIL import Image
import os.path
import string
import threading
from time import sleep

from pkg_resources import resource_string


class main_window(threading.Thread):

    #--------------------------------------------
    # initialization
    #--------------------------------------------

    def __init__(self):

        # find/create the /tmp file name
        self.imageName = self.get_temp_file_name()
        self.builder = gtk.Builder()

        # resolve the username to set the default "Save As" path
        userName = os.popen("echo $USER")
        self.defaultPath = "/home/" + userName.read().rstrip()

        self.builder.add_from_string(resource_string(
            'gscreenshot.resources.gui.glade', 'main.glade').decode("UTF-8"))

        self.window = self.builder.get_object('window_main')

        # create the main window

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
            "on_button_quit_clicked": self.button_quit_clicked}

        self.builder.connect_signals(dic)

        # create objects from selected widgets in the main window
        self.image_preview = self.builder.get_object("image1")
        self.hide_check = self.builder.get_object("checkbutton1")
        self.delay_setter = self.builder.get_object("spinbutton1")
        self.button_saveas = self.builder.get_object("button_saveas")

        self.grab_screenshot("")
        self.show_preview()

    #--------------------------------------------
    # signal handlers
    #--------------------------------------------

    #
    #---- button_all_clicked  :grab a screenshot of the whole screen
    #
    def button_all_clicked(self, widget):
        # check if the window should be hidden while grabbing screenshot
        if self.hide_check.get_active():
            # hide the window to grab the screenshot without it
            self.window.hide()

        # wait until the window is completely hidden
        while gtk.events_pending():
            gtk.main_iteration()

        # grab the screenshot
        sleep(0.2)
        self.grab_screenshot("")

        # show the window
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.show_all()

        # create and show a preview of the grabbed screenshot
        self.show_preview()

        # now, there is a screenshot, so the "save as" function can be enabled
        # (hint: line 74)
        self.button_saveas.set_sensitive(True)

    def button_select_area_or_window_clicked(self, widget):
        # check if the window should be hidden while grabbing screenshot
        if self.hide_check.get_active():
            # hide the window to grab the screenshot without it
            self.window.hide()

        # wait until the window is completely hidden
        while gtk.events_pending():
            gtk.main_iteration()

        # grab the screenshot
        self.grab_screenshot("-s")

        # show the window
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.show_all()

        # create and show a preview of the grabbed screenshot
        self.show_preview()

        # now, there is a screenshot, so the "save as" function can be enabled
        # (hint: line 74)
        self.button_saveas.set_sensitive(True)

    #
    #---- button_saveas_clicked  :save the grabbed screenshot
    #
    def button_saveas_clicked(self, widget):
        # make the main window unsensitive while saving your image
        self.window.set_sensitive(False)

        im = Image.open(self.get_temp_file_name())

        save_handler = FileSaveHandler()
        save_handler.run(im)

        self.window.set_sensitive(True)

    #
    #---- button_about_clicked  :show the "about" dialog
    #
    def button_about_clicked(self, widget):
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

    def on_about_close(self, action, parameter):
        action.destroy()
        self.window.set_sensitive(True)

    #
    #---- button_quit_clicked  :quit the application
    #
    def button_quit_clicked(self, widget):
        self.quit(widget)

    def quit(self, widget):
        try:
            os.remove(self.imageName)
        except:
            pass
        sys.exit(0)

    #--------------------------------------------
    # other functions
    #--------------------------------------------

    def get_temp_file_name(self):
        # create a unique image file name based on the application PID
        imageName = "/tmp/gscreenshot_" + str(os.getpid()) + ".png"

        # return the result
        return imageName

    def grab_screenshot(self, commandParameters):
        # remove the temporary file ( in /tmp) from the past
        try:
            os.remove(self.imageName)
        except:
            print("no temporary file deleted - nothing found")

        # resolve the delay_setter+1 sec.  delay
        # repr(delay) - converts integer to a string
        delay = self.delay_setter.get_value()

        # grab the screenshot with scrot to the /tmp directory
        os.system("scrot " + " -d " + repr(delay) + " " +
                  commandParameters + " " + self.imageName)

        # change it's permissions
        os.chmod(self.imageName, 0o600)

    def show_preview(self):
        # create an image buffer (pixbuf) and insert the grabbed image
        previewPixbuf = gtk.gdk.pixbuf_new_from_file(self.imageName)

        # resolve the preview image width and height
        previewHeight = previewPixbuf.get_height() / 4
        previewWidth = previewPixbuf.get_width() / 4

        # resize the previewPixbuf to previewWidth, previewHeight
        previewPixbuf = previewPixbuf.scale_simple(
            previewWidth, previewHeight, gtk.gdk.INTERP_BILINEAR)

        # set the image_preview widget to the preview image size (previewWidth,
        # previewHeight)
        self.image_preview.set_size_request(previewWidth, previewHeight)

        # view the previewPixbuf in the image_preview widget
        self.image_preview.set_from_pixbuf(previewPixbuf)


class FileSaveHandler():

    def __init__(self):
        pass

    def run(self, image):
        filename = self.request_file()

        if filename is None:
            return

        while os.path.isfile(filename) and not self.confirm_replace(filename):
            if (filename is None):
                return

        self.save_file(filename, image)

    def confirm_replace(self, filename):
        message = "A file named " + filename + " already exists.\n\
                Do you want to replace it?"

        confirm_dialog = gtk.MessageDialog(None,
                                           gtk.DIALOG_MODAL,
                                           gtk.MESSAGE_QUESTION,
                                           gtk.BUTTONS_NONE,
                                           message)
        confirm_dialog.add_buttons(gtk.STOCK_CANCEL, 0, gtk.STOCK_OK, 1)
        confirm_dialog.format_secondary_text(
            "The file already exists. Replacing it will overwrite its contents")
        response = confirm_dialog.run()
        confirm_dialog.destroy()

        if (response == 1):
            return True
        else:
            return False

    def request_file(self):
        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        response = chooser.run()

        if (response == gtk.RESPONSE_OK):
            return_value = chooser.get_filename()
        elif (response == gtk.RESPONSE_CANCEL):
            return_value = None

        chooser.destroy()
        return return_value

    def save_file(self, filename, im):
        actual_file_ext = os.path.splitext(filename)[1][1:]

        supported_formats = (
            'bmp', 'eps', 'gif', 'jpg', 'pcx', 'pdf', 'ppm', 'tiff', 'png')
        for i in supported_formats:
            # if it's supported convert it
            if (i == actual_file_ext.lower()):
                # if it's jpeg, change the descriptor
                if i == 'jpg':
                    i = 'jpeg'
                i = i.upper()
                im.save(filename, i)
                break


def main():
    # create the main_window object and window
    gscreenshot = main_window()
    gtk.main()
#-------------------------------------------------------------------------

if __name__ == "__main__":
    main()
