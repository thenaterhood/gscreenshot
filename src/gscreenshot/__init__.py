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

from datetime import datetime
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
            return True
        else:
            return False

    def get_last_save_directory(self):
        return self.last_save_directory

    def quit(self):
        """
        Exits the application and interpreter
        """
        sys.exit(0)
