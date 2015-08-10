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


        # set the glade file
        self.gladefile = "gscreenshot_main/gscreenshot_main.glade"
        self.builder.add_from_file(self.gladefile)

        self.window = self.builder.get_object('window_main')

        # create the main window

        # show the (main) window in the center of the screen
        self.window.set_position(gtk.WIN_POS_CENTER)

        # create a signal dictionary and connect it to the handler functions
        dic = {"on_window_main_destroy": self.quit, "on_button_all_clicked": self.button_all_clicked, "on_button_window_clicked": self.button_window_clicked, "on_button_selectarea_clicked":
               self.button_select_area_clicked, "on_button_saveas_clicked": self.button_saveas_clicked, "on_button_about_clicked": self.button_about_clicked, "on_button_quit_clicked": self.button_quit_clicked}

        self.builder.connect_signals(dic)

        # create objects from selected widgets in the main window
        self.image_preview = self.builder.get_object("image1")
        self.hide_check = self.builder.get_object("checkbutton1")
        self.delay_setter = self.builder.get_object("spinbutton1")
        self.button_saveas = self.builder.get_object("button_saveas")

        self.grab_screenshot("")
        self.show_preview()

        # create the "about" dialog object
        self.about = about_dialog()

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

    #
    #---- button_window_clicked  :grab a screenshot of a selected window
    #
    def button_window_clicked(self, widget):
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
    #---- button_select_area_clicked  :grab a screenshot of a selected area
    #
    def button_select_area_clicked(self, widget):
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

        chooser = gtk.FileChooserDialog(title=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))

        response = chooser.run()

        if (response == gtk.RESPONSE_OK):
            self.save_file_handler(chooser)
        elif (response == gtk.RESPONSE_CANCEL):
            pass

        chooser.destroy()
        self.window.set_sensitive(True)

        # send the "save as" dialog object a request to create it's window
        # self.save_as_dialog.create()

        # set the last path in the "save as" dialog
        # (very useful if you want to grab more screenshots into the same directory -
        # - you don't need to there from $HOME again and again)
        # self.save_as_dialog.window.set_current_folder(self.defaultPath)

        # place the "save as" dialog into the center of the screen
        # self.save_as_dialog.window.set_position(gtk.WIN_POS_CENTER)

    #
    #---- button_about_clicked  :show the "about" dialog
    #
    def button_about_clicked(self, widget):
        # make the main window unsensitive while viewing the "about"
        # information
        gscreenshot.window.set_sensitive(False)

        # send the "about" dialog object a request to create it's window
        self.about.create()

        # place the "about" dialog into the center of the screen
        self.about.window.set_position(gtk.WIN_POS_CENTER)

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

    def save_file_handler(self, chooser):

        # save the last path into the defaultPath variable
        gscreenshot.defaultPath = chooser.get_current_folder()

        # resolve a selected file and it's extension
        self.actualFile = chooser.get_filename()

        # if there's a file selected, save (copy) the temporary screenshot into the selected directory
        # with the selected file name
        if self.actualFile != None:

            self.actualSplit = os.path.split(self.actualFile)[1]
            self.actualDir = os.path.basename(chooser.get_current_folder())

            if os.path.isfile(self.actualFile):
                # if the file exists ask the user using the replace dialog if
                # to replace the image
                chooser.set_sensitive(False)

                # create the replace dialog object and run it
                replace_dialog_instance = replace_dialog(
                    self.actualSplit, self.actualDir)
                result = replace_dialog_instance.dialog.run()

                chooser.set_sensitive(True)

                # destroy the dialog window and delete the
                # replace_dialog_instance object
                replace_dialog_instance.dialog.destroy()
                del replace_dialog_instance

            if not os.path.isfile(self.actualFile) or result == 1:
                # if the file doesn't exist or it's allowed to replace it, save
                # it

                self.save_file(self.actualFile)
                # make the "main" window sensitive

    def save_file(self, actual_file):

        actual_file_ext = os.path.splitext(actual_file)[1][1:]
        im = Image.open(gscreenshot.get_temp_file_name())

        if (actual_file_ext.lower()) == 'png':
            # if it is .png just copy it
            os.system(
                "cp " + gscreenshot.get_temp_file_name() + " " + actual_file)
        else:
            supported_formats = (
                'bmp', 'eps', 'gif', 'jpg', 'pcx', 'pdf', 'ppm', 'tiff')
            for i in supported_formats:
                # if it's supported convert it
                if (i == actual_file_ext.lower()):
                    # if it's jpeg, change the descriptor
                    if i == 'jpg':
                        i = 'jpeg'
                    i = string.upper(i)
                    im.save(actual_file, i)
                    break
        print(actual_file)


class about_dialog:

    def create(self):
        # set the glade file
        self.builder = gtk.Builder()

        self.gladefile = "gscreenshot_about/gscreenshot_about.glade"
        self.builder.add_from_file(self.gladefile)

        # create the "about" window
        self.window = self.builder.get_object("window_about")
        self.window.set_name("gscreenshot")
        self.window.connect("response", lambda d, r: self.close())

    def close(self):
        # while closing the "about" dialog, make the main window sensitive
        gscreenshot.window.set_sensitive(True)
        self.window.destroy()


class replace_dialog(threading.Thread):
    #
    #---- create the "replace" dialog window and make the main and "save as" window unsensitive
    #

    def __init__(self, file_name, dir_name):
        buttons = gtk.BUTTONS_CANCEL, 0, "Replace", 1
        message = "A file named \"" + file_name + \
            "\" already exists.  Do you\nwant to replace it?"
        self.dialog = gtk.MessageDialog(None,
                                        gtk.DIALOG_MODAL,
                                        gtk.MESSAGE_QUESTION,
                                        gtk.BUTTONS_NONE,
                                        message)
        self.dialog.add_buttons(gtk.STOCK_CANCEL, 0, gtk.STOCK_OK, 1)
        self.dialog.format_secondary_text(
            "The file already exists in \"" + dir_name + "\".  Replacing it will overwrite its contents.")
        self.dialog.show_all()


#-------------------------------------------------------------------------

if __name__ == "__main__":

    # create the main_window object (and window)
    gscreenshot = main_window()
    gtk.main()
