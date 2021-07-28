#!/usr/bin/env python
'''
 gscreenshot.py
 Matej Horvath <matej.horvath@gmail.com>
 3. september 2006

 Adopted August 9, 2015
 Nate Levesque <public@thenaterhood.com>
 - Retrieved from Google Code
 - Updated to use modern libraries and formats
 - Further changes will be noted in release notes
'''
import gettext
import io
import json
import locale
import os
import sys
import subprocess
import tempfile

from datetime import datetime
from pkg_resources import resource_string, require, resource_filename
from PIL import Image
from gscreenshot.screenshooter.factory import ScreenshooterFactory
from gscreenshot.util import session_is_wayland

_ = gettext.gettext


class Gscreenshot(object):
    """
    Gscreenshot application
    """

    # generated using piexif
    EXIF_TEMPLATE = b'Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x02\x011\x00\x02\x00\x00\x00\x15\x00\x00\x00&\x87i\x00\x04\x00\x00\x00\x01\x00\x00\x00;\x00\x00\x00\x00gscreenshot [[VERSION]]\x00\x00\x01\x90\x03\x00\x02\x00\x00\x00\x14\x00\x00\x00I[[CREATE_DATE]]\x00' #pylint: disable=line-too-long

    def __init__(self, screenshooter=None):
        """
        constructor
        """
        locale_path = resource_filename('gscreenshot.resources', 'locale')
        locale.setlocale(locale.LC_ALL, '')
        # I don't know what's going on with this. This call appears to exist,
        # works fine, and seems required for glade localization to work.
        #pylint: disable=no-member
        locale.bindtextdomain('gscreenshot', locale_path)
        gettext.bindtextdomain('gscreenshot', locale_path)
        gettext.textdomain('gscreenshot')

        self.screenshooter_factory = ScreenshooterFactory(screenshooter)
        self.screenshooter = self.screenshooter_factory.create()

        self.saved_last_image = False
        self.last_save_file = None
        self.cache = {"last_save_dir": os.path.expanduser("~")}
        if os.path.isfile(self.get_cache_file()):
            with open(self.get_cache_file(), "r") as cachefile:
                try:
                    self.cache = json.load(cachefile)
                except json.JSONDecodeError:
                    self.cache = {"last_save_dir": os.path.expanduser("~")}
                    self.save_cache()
        else:
            self.save_cache()

    def get_available_cursors(self):
        '''
        Get the alternate pointer pixmaps gscreenshot can use
        Returns [(name, PIL.Image)]
        '''
        return {
                'theme': None,
                'adwaita': Image.open(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'cursor-adwaita.png'
                    )
                ),
                'prohibit': Image.open(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'cursor-prohibit.png'
                    )
                ),
                'allow': Image.open(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'cursor-allow.png'
                    )
                )
            }

    def show_screenshot_notification(self):
        '''
        Show a notification that a screenshot was taken.
        This method is a "fire-and-forget" and won't
        return a status as to whether it succeeded.
        '''
        try:
            #pylint: disable=fixme
            # TODO: when dropping python2 support, switch to using with here
            #pylint: disable=consider-using-with
            subprocess.Popen([
                'notify-send',
                'gscreenshot',
                _('a screenshot was taken from a script or terminal'),
                '--icon',
                'gscreenshot'
            ])
        except OSError:
            print(_("failed to show screenshot notification - is notify-send working?"))
            return

    def run_display_mismatch_warning(self):
        '''
        Send a notification if the screenshot was taken from a
        non-X11 or wayland session.
        '''
        if 'XDG_SESSION_ID' not in os.environ:
            return

        if 'XDG_SESSION_TYPE' not in os.environ:
            self.show_screenshot_notification()

        session_type = os.environ['XDG_SESSION_TYPE']
        if session_type.lower() not in ('x11', 'mir', 'wayland'):
            self.show_screenshot_notification()

    def get_cache_file(self):
        """
        Find the gscreenshot cache file and return its path
        """
        if 'XDG_CACHE_HOME' in os.environ:
            return os.environ['XDG_CACHE_HOME'] + "/gscreenshot"
        else:
            return os.path.expanduser("~/.gscreenshot")

    def save_cache(self):
        """Writes the cache to disk"""
        try:
            with open(self.get_cache_file(), "w") as cachefile:
                json.dump(self.cache, cachefile)
        except FileNotFoundError:
            print(_("unable to save cache file"))

    def get_screenshooter_name(self):
        """Gets the name of the current screenshooter"""
        return self.screenshooter.__class__.__name__

    def screenshot_full_display(self, delay=0, capture_cursor=False, cursor_name='theme'):
        """
        Takes a screenshot of the full display with a
        given delay.

        Parameters:
            int delay: seconds to wait before taking screenshot

        Returns:
            PIL.Image
        """

        if not capture_cursor:
            use_cursor = None
        else:
            use_cursor = self.get_available_cursors()[cursor_name]

        self.screenshooter._grab_fullscreen(
            delay,
            capture_cursor,
            use_cursor=use_cursor
        )
        self.run_display_mismatch_warning()
        self.saved_last_image = False
        return self.screenshooter.image

    def screenshot_selected(self, delay=0, capture_cursor=False, cursor_name='theme'):
        """
        Interactively takes a screenshot of a selected area
        with a given delay.

        Parameters:
            int delay: seconds to wait before taking screenshot

        Returns:
            PIL.Image
        """

        if not capture_cursor:
            use_cursor = None
        else:
            use_cursor = self.get_available_cursors()[cursor_name]

        self.screenshooter._grab_selection(
            delay,
            capture_cursor,
            use_cursor=use_cursor
        )
        self.run_display_mismatch_warning()
        self.saved_last_image = False
        return self.screenshooter.image

    def screenshot_window(self, delay=0, capture_cursor=False, cursor_name='theme'):
        """
        Interactively takes a screenshot of a selected window
        with a given delay.

        Parameters:
            int delay: seconds to wait before taking screenshot

        Returns:
            PIL.Image
        """

        if not capture_cursor:
            use_cursor = None
        else:
            use_cursor = self.get_available_cursors()[cursor_name]

        self.screenshooter._grab_window(
            delay,
            capture_cursor,
            use_cursor=use_cursor
        )
        self.run_display_mismatch_warning()
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
        """
        Gets a thumbnail of either the current image, or a passed one

        Params:
            width: int
            height: int
            image: Image|None

        Returns:
            Image
        """
        thumbnail = None

        if image is None and self.screenshooter.image is not None:
            thumbnail = self.screenshooter.image.copy()
        elif image is not None:
            thumbnail = image.copy()

        if thumbnail is not None:
            thumbnail.thumbnail((width, height), Image.ANTIALIAS)
            return thumbnail

        return self.get_app_icon()

    def get_time_filename(self):
        """
        Generates a returns a filename based on the current time

        Returns:
            str
        """
        now = datetime.now()
        return datetime.strftime(now, "gscreenshot_%Y-%m-%d-%H%M%S.png")

    def save_and_return_path(self):
        """
        Saves the last screenshot to /tmp if it hasn't been saved
        and returns the path to it.

        Returns:
            str
        """
        screenshot_fname = os.path.join(
                tempfile.gettempdir(),
                self.get_time_filename()
                )

        if not self.saved_last_image:
            self.save_last_image(screenshot_fname)
        else:
            screenshot_fname = self.last_save_file

        return screenshot_fname

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

        if filename is None:
            filename = self.get_time_filename()

        image = self.screenshooter.image
        actual_file_ext = os.path.splitext(filename)[1][1:].lower()

        if actual_file_ext == "":
            # If we don't have any file extension, assume
            # we were given a directory; create the tree
            # if it doesn't exist, then store the screenshot
            # there with a time-based filename.
            try:
                os.makedirs(filename)
            except (IOError, OSError):
                # Likely the directory already exists, so
                # we'll throw the exception away.
                # If we fail to save, we'll return a status
                # saying so, so we'll be okay.
                pass

            filename = os.path.join(
                    filename,
                    self.get_time_filename()
                    )
            actual_file_ext = 'png'

        if actual_file_ext == 'jpg':
            actual_file_ext = 'jpeg'

        supported_formats = self.get_supported_formats()

        if actual_file_ext in supported_formats:
            self.cache["last_save_dir"] = os.path.dirname(filename)
            self.save_cache()
            try:
                # add exif data. This is sketchy but we don't need to
                # dynamically generate it, just find and replace.
                # This avoids needing an external library for such a simple
                # thing.
                exif_data = self.EXIF_TEMPLATE.replace(
                    '[[VERSION]]'.encode(),
                    self.get_program_version(True).encode()
                )
                exif_data = exif_data.replace(
                    '[[CREATE_DATE]]'.encode(),
                    datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode()
                )

                image.save(filename, actual_file_ext.upper(), exif=exif_data)

                self.saved_last_image = True
                self.last_save_file = filename
                return True
            except IOError:
                self.saved_last_image = False
                return False
        else:
            return False

    def open_last_screenshot(self):
        """
        Calls xdg to open the screenshot in its default application

        Returns:
            bool success
        """
        screenshot_fname = self.save_and_return_path()

        try:
            #pylint: disable=fixme
            # TODO: when dropping python2 support, switch to using with here
            #pylint: disable=consider-using-with
            subprocess.Popen(['xdg-open', screenshot_fname])
            return True
        except (subprocess.CalledProcessError, IOError):
            return False

    def copy_last_screenshot_to_clipboard(self):
        """
        Copies the last screenshot to the clipboard with
        xclip, if available. Most frontends should try to
        use native methods (e.g. Gdk.Clipboard) if possible.

        Returns:
            bool success
        """
        image = self.screenshooter.image

        if image is None:
            return False

        params = [
            'xclip',
            '-selection',
            'clipboard',
            '-t',
            'image/png'
            ]

        if session_is_wayland():
            params = [
                    'wl-copy',
                    '-t',
                    'image/png'
                ]

        with io.BytesIO() as png_data:
            image.save(png_data, "PNG")

            try:
                #pylint: disable=fixme
                # TODO: when dropping python2 support, switch to using with here
                #pylint: disable=consider-using-with
                clip = subprocess.Popen(
                    params,
                    close_fds=True,
                    stdin=subprocess.PIPE,
                    stdout=None,
                    stderr=None)
                clip.communicate(input=png_data.getvalue())
                return True
            except (subprocess.CalledProcessError, OSError):
                return False

    def get_last_save_directory(self):
        """Returns the path of the last save directory"""
        return self.cache["last_save_dir"]

    def get_program_authors(self):
        """
        Returns the list of authors

        Returns:
            string[]
        """
        authors = [
                "Nate Levesque <public@thenaterhood.com>",
                "Original Author (2006)",
                "matej.horvath <matej.horvath@gmail.com>"
                ]

        return authors

    def get_app_icon(self):
        """Returns the application icon"""
        return Image.open(
                resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png')
                )

    def get_program_description(self):
        """Returns the program description"""
        return "A simple screenshot tool supporting multiple backends."

    def get_program_website(self):
        """Returns the URL of the program website"""
        return "https://github.com/thenaterhood/gscreenshot"

    def get_program_name(self):
        """Returns the program name"""
        return "gscreenshot"

    def get_program_license_text(self):
        """Returns the license text"""
        return resource_string('gscreenshot.resources', 'LICENSE').decode('UTF-8')

    def get_program_license(self):
        """Returns the license name"""
        return "GPLv2"

    def get_program_version(self, padded = False):
        """Returns the program version"""
        if not padded:
            return require("gscreenshot")[0].version
        else:
            version = require("gscreenshot")[0].version.split(".")
            padded_version = [v.rjust(2, "0") for v in version]
            return ".".join(padded_version)

    def quit(self):
        """
        Exits the application and interpreter
        """
        sys.exit(0)
