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
import os
import sys
import subprocess
import tempfile

from datetime import datetime
from pkg_resources import resource_string
from pkg_resources import require
from PIL import Image
from gscreenshot.screenshooter.scrot import Scrot


class Gscreenshot(object):
    """
    Gscreenshot application
    """

    def __init__(self, screenshooter=None):
        """
        constructor
        """

        if screenshooter is None:
            screenshooter = Scrot()

        self.screenshooter = screenshooter
        self.saved_last_image = False
        self.last_save_file = None
        self.last_save_directory = os.path.expanduser("~")

    def screenshot_full_display(self, delay=0):
        """
        Takes a screenshot of the full display with a
        given delay.

        Parameters:
            int delay: seconds to wait before taking screenshot

        Returns:
            PIL.Image
        """

        self.screenshooter.grab_fullscreen(delay)
        self.saved_last_image = False
        return self.screenshooter.image

    def screenshot_selected(self, delay=0):
        """
        Interactively takes a screenshot of a selected area
        with a given delay.

        Parameters:
            int delay: seconds to wait before taking screenshot

        Returns:
            PIL.Image
        """

        self.screenshooter.grab_selection(delay)
        self.saved_last_image = False
        return self.screenshooter.image

    def screenshot_window(self, delay=0):
        """
        Interactively takes a screenshot of a selected window
        with a given delay.

        Parameters:
            int delay: seconds to wait before taking screenshot

        Returns:
            PIL.Image
        """

        self.screenshooter.grab_window(delay)
        self.saved_last_image = False
        return self.screenshooter.image

    def get_last_image(self):
        """
        Returns the last screenshot taken

        Returns:
            PIL.Image
        """
        return self.screenshooter.image

    def get_supported_formats(self):
        """
        Returns the image formats supported for saving to

        Returns:
            array
        """
        supported_formats = [
            'bmp', 'eps', 'gif', 'jpeg', 'pcx', 'pdf', 'ppm', 'tiff', 'png'
            ]

        return supported_formats

    def get_thumbnail(self, width, height, image=None):
        if image is None:
            thumbnail = self.screenshooter.image.copy()
        else:
            thumbnail = image.copy()

        thumbnail.thumbnail((width, height), Image.ANTIALIAS)
        return thumbnail

    def get_time_filename(self):
        """
        Generates a returns a filename based on the current time

        Returns:
            str
        """
        d = datetime.now()
        return datetime.strftime(d, "gscreenshot_%Y-%m-%d-%H%M%S.png")

    def save_last_image(self, filename = None):
        """
        Saves the last screenshot taken with a given filename.
        Returns a boolean for success or fail. A supported file
        extension must be part of the filename provided.

        Parameters:
            str filename

        Returns:
            bool success
        """

        if (filename is None):
            filename = self.get_time_filename()

        image = self.screenshooter.image
        actual_file_ext = os.path.splitext(filename)[1][1:].lower()

        if actual_file_ext == 'jpg':
            actual_file_ext = 'jpeg'

        supported_formats = self.get_supported_formats()

        if actual_file_ext in supported_formats:
            self.last_save_directory = os.path.dirname(filename)
            image.save(filename, actual_file_ext.upper())
            self.saved_last_image = True
            self.last_save_file = filename
            return True
        else:
            return False

    def open_last_screenshot(self):
        """
        Calls xdg to open the screenshot in its default application

        Returns:
            bool success
        """
        screenshot_fname = os.path.join(
                tempfile.gettempdir(),
                self.get_time_filename()
                )

        if (not self.saved_last_image):
            self.save_last_image(screenshot_fname)
        else:
            screenshot_fname = self.last_save_file

        try:
            subprocess.Popen(['xdg-open', screenshot_fname])
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_last_save_directory(self):
        return self.last_save_directory

    def get_program_authors(self):
        authors = [
                "Nate Levesque <public@thenaterhood.com>",
                "Original Author (2006)",
                "matej.horvath <matej.horvath@gmail.com>"
                ]

        return authors

    def get_app_icon(self):
        return Image.open('/usr/share/pixmaps/gscreenshot.png')

    def get_program_description(self):

        return "A simple screenshot tool"

    def get_program_website(self):

        return "https://github.com/thenaterhood/gscreenshot"

    def get_program_name(self):

        return "gscreenshot"

    def get_program_license_text(self):

        return resource_string('gscreenshot.resources', 'LICENSE').decode('UTF-8')

    def get_program_license(self):

        return "GPLv2"

    def get_program_version(self):

        return require("gscreenshot")[0].version

    def quit(self):
        """
        Exits the application and interpreter
        """
        sys.exit(0)
