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
import platform
import sys
import subprocess
import tempfile
import typing

from datetime import datetime
from pkg_resources import resource_string, require, resource_filename
from PIL import Image
from gscreenshot.screenshot import Screenshot, ScreenshotCollection
from gscreenshot.screenshooter import Screenshooter
from gscreenshot.screenshooter.factory import ScreenshooterFactory
from gscreenshot.util import session_is_wayland

_ = gettext.gettext


class Gscreenshot(object):
    """
    Gscreenshot application
    """

    __slots__ = ['screenshooter', 'cache', '_screenshots', '_stamps']

    screenshooter: Screenshooter
    cache: typing.Dict[str, str]
    _screenshots: ScreenshotCollection
    _stamps: typing.Dict[str, Image.Image]

    # generated using piexif
    EXIF_TEMPLATE = b'Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x02\x011\x00\x02\x00\x00\x00\x15\x00\x00\x00&\x87i\x00\x04\x00\x00\x00\x01\x00\x00\x00;\x00\x00\x00\x00gscreenshot [[VERSION]]\x00\x00\x01\x90\x03\x00\x02\x00\x00\x00\x14\x00\x00\x00I[[CREATE_DATE]]\x00' #pylint: disable=line-too-long

    def __init__(self, screenshooter=None):
        """
        constructor
        """
        try:
            locale_path = resource_filename('gscreenshot.resources', 'locale')
            locale.setlocale(locale.LC_ALL, '')
            # I don't know what's going on with this. This call appears to exist,
            # works fine, and seems required for glade localization to work.
            #pylint: disable=no-member
            locale.bindtextdomain('gscreenshot', locale_path)
            gettext.bindtextdomain('gscreenshot', locale_path)
            gettext.textdomain('gscreenshot')
        except locale.Error:
            # gscreenshot will fall back to english instead
            # of crashing if there's a locale issue.
            pass

        screenshooter_factory = ScreenshooterFactory(screenshooter)
        self.screenshooter = screenshooter_factory.create()
        self._screenshots = ScreenshotCollection()

        self._stamps = {}

        self.cache = {"last_save_dir": os.path.expanduser("~")}
        if os.path.isfile(self.get_cache_file()):
            with open(self.get_cache_file(), "r", encoding="UTF-8") as cachefile:
                try:
                    self.cache = json.load(cachefile)
                except json.JSONDecodeError:
                    self.cache = {"last_save_dir": os.path.expanduser("~")}
                    self.save_cache()
        else:
            self.save_cache()

    def get_capabilities(self) -> typing.Dict[str, str]:
        '''
        Get the features supported in the current setup
        '''
        return self.screenshooter.get_capabilities_()

    def register_stamp_image(self, fname: str,
        name: typing.Optional[str]=None
    ) -> typing.Optional[str]:
        '''
        Adds a new stamp image from a file path
        '''
        if not os.path.exists(fname):
            return None

        glyph = Image.open(fname).convert("RGBA")
        if name is None:
            name = os.path.basename(fname)

        if len(name) > 9:
            name = f"{name[0:8]}..."

        self._stamps[name] = glyph

        return name

    def get_available_cursors(self) -> typing.Dict[str, typing.Optional[Image.Image]]:
        '''
        Get the alternate pointer pixmaps gscreenshot can use
        Returns {name: PIL.Image}
        '''
        available = {
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

        available.update(self._stamps)
        return available

    def show_screenshot_notification(self) -> bool:
        '''
        Show a notification that a screenshot was taken.
        This method is a "fire-and-forget" and won't
        return a status as to whether it succeeded.
        '''
        try:
            # This has a timeout in case the notification
            # daemon is hanging - don't lock up gscreenshot too
            subprocess.run([
                'notify-send',
                'gscreenshot',
                _('a screenshot was taken from a script or terminal'),
                '--icon',
                'gscreenshot'
            ], check=True, timeout=2)
            return True
        except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
            return False

    def run_display_mismatch_warning(self):
        '''
        Send a notification if the screenshot was taken from a
        non-X11 or wayland session.
        '''
        if 'XDG_SESSION_ID' not in os.environ:
            return

        if 'XDG_SESSION_TYPE' not in os.environ:
            self.show_screenshot_notification()
            return

        session_type = os.environ['XDG_SESSION_TYPE']
        if session_type.lower() not in ('x11', 'mir', 'wayland'):
            self.show_screenshot_notification()

    def get_cache_file(self) -> str:
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
            with open(self.get_cache_file(), "w", encoding="UTF-8") as cachefile:
                json.dump(self.cache, cachefile)
        except FileNotFoundError:
            print(_("unable to save cache file"))

    def get_screenshooter_name(self) -> str:
        """Gets the name of the current screenshooter"""
        if hasattr(self.screenshooter, '__utilityname__'):
            if self.screenshooter.__utilityname__ is not None:
                return self.screenshooter.__utilityname__

        return self.screenshooter.__class__.__name__

    #pylint: disable=too-many-arguments
    def screenshot_full_display(self, delay: int=0, capture_cursor: bool=False,
                                cursor_name: str='theme', overwrite: bool=False, count: int=1
                                ) -> typing.Optional[Image.Image]:
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

        for _ in range(0, count):
            self.screenshooter.grab_fullscreen_(
                delay,
                capture_cursor,
                use_cursor=use_cursor
            )

            if self.screenshooter.screenshot is not None:
                if overwrite:
                    self._screenshots.replace(self.screenshooter.screenshot)
                else:
                    self._screenshots.append(self.screenshooter.screenshot)

        self.run_display_mismatch_warning()

        if not overwrite:
            self._screenshots.cursor_to_end()

        return self.get_last_image()

    #pylint: disable=too-many-arguments
    def screenshot_selected(self, delay: int=0, capture_cursor: bool=False,
                            cursor_name: str='theme', overwrite: bool=False, count: int=1,
                            region: typing.Optional[typing.Tuple[int, int, int, int]]=None
                            ) -> typing.Optional[Image.Image]:
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

        for _ in range(0, count):
            self.screenshooter.grab_selection_(
                delay,
                capture_cursor,
                use_cursor=use_cursor,
                region=region
            )

            if self.screenshooter.screenshot is not None:
                if overwrite:
                    self._screenshots.replace(self.screenshooter.screenshot)
                else:
                    self._screenshots.append(self.screenshooter.screenshot)

        self.run_display_mismatch_warning()

        if not overwrite:
            self._screenshots.cursor_to_end()

        return self.get_last_image()

    #pylint: disable=too-many-arguments
    def screenshot_window(self, delay: int=0, capture_cursor: bool=False,
                          cursor_name: str='theme', overwrite: bool=False, count: int=1
                          ) -> typing.Optional[Image.Image]:
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

        for _ in range(0, count):
            self.screenshooter.grab_window_(
                delay,
                capture_cursor,
                use_cursor=use_cursor
            )

            if self.screenshooter.screenshot is not None:
                if overwrite:
                    self._screenshots.replace(self.screenshooter.screenshot)
                else:
                    self._screenshots.append(self.screenshooter.screenshot)

        self.run_display_mismatch_warning()

        if not overwrite:
            self._screenshots.cursor_to_end()

        return self.get_last_image()

    def get_last_image(self) -> typing.Optional[Image.Image]:
        """
        Returns the last screenshot taken

        Returns:
            PIL.Image
        """
        try:
            screenshot = self._screenshots.cursor_current()
            if screenshot is not None:
                return screenshot.get_image()
        except IndexError:
            pass

        return None

    def get_screenshot_collection(self) -> ScreenshotCollection:
        '''Returns the screenshot collection'''
        return self._screenshots

    def get_supported_formats(self) -> typing.List[str]:
        """
        Returns the image formats supported for saving to

        Returns:
            array
        """
        supported_formats = [
            'bmp', 'eps', 'gif', 'jpeg', 'pcx',
            'pdf', 'ppm', 'tiff', 'png', 'webp',
            ]

        return supported_formats

    def get_thumbnail(self, width: int, height: int, with_border: bool=False
                      ) -> Image.Image:
        """
        Gets a thumbnail of either the current image, or a passed one
        Params:
            width: int
            height: int
            image: Image|None
        Returns:
            Image
        """
        screenshot = self._screenshots.cursor_current()

        if screenshot is not None:
            return screenshot.get_preview(width, height, with_border) or self.get_app_icon()

        return self.get_app_icon()

    def get_time_filename(self) -> str:
        """
        Generates a returns a filename based on the current time

        Returns:
            str
        """
        return self.interpolate_filename("gscreenshot_%Y-%m-%d-%H%M%S.png")

    def interpolate_filename(self, filename:str) -> str:
        '''
        Does interpolation of a filename, as the following:
           $$   a literal '$'
           $a   system hostname
           $h   image's height in pixels
           $p   image's size in pixels
           $w   image's width in pixels

           Format operators starting with "%" are
           run through strftime.
        '''
        if "$" not in filename and "%" not in filename:
            return filename

        general_replacements:typing.Dict[str, str] = {
            '$$': '$',
            '$a': platform.node()
        }

        image = self.get_last_image()
        if image is not None:
            general_replacements.update({
                '$h': str(image.height),
                '$p': str(image.height * image.width),
                '$w': str(image.width)
            })

        for fmt, replacement in general_replacements.items():
            filename = filename.replace(fmt, replacement)

        now = datetime.now()
        filename = now.strftime(filename)

        return filename

    def get_time_foldername(self) -> str:
        '''Generates a time-based folder name'''
        return self.interpolate_filename("gscreenshot_%Y-%m-%d-%H%M%S")

    def save_and_return_path(self) -> typing.Optional[str]:
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

        screenshot = self._screenshots.cursor_current()
        if screenshot is None:
            return None

        if not screenshot.saved():
            self.save_last_image(screenshot_fname)
            screenshot.set_saved_path(screenshot_fname)
        else:
            return screenshot.get_saved_path()

        return screenshot_fname

    def _save_image(self, image: Image.Image, filename: typing.Optional[str]=None,
                    overwrite: bool=True) -> bool:
        '''
        Internal method for saving an image to a file
        '''
        if filename is None:
            filename = self.get_time_filename()
        else:
            filename = self.interpolate_filename(filename)

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

        if not overwrite and os.path.exists(filename):
            return False

        if actual_file_ext == 'jpg':
            actual_file_ext = 'jpeg'

        supported_formats = self.get_supported_formats()

        if actual_file_ext in supported_formats:
            self.cache["last_save_dir"] = os.path.dirname(filename)
            self.save_cache()

            screenshot = self._screenshots.cursor_current()

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

                if screenshot is not None:
                    screenshot.set_saved_path(filename)
                return True
            except IOError:

                if screenshot is not None:
                    screenshot.set_saved_path(None)
                return False
        else:
            return False

    def save_screenshot_collection(self, foldername: typing.Optional[str]=None) -> bool:
        '''
        Saves every image in the current screenshot collection
        '''

        if foldername is None:
            foldername = self.get_time_foldername()
        else:
            foldername = self.interpolate_filename(foldername)

        if not os.path.exists(foldername):
            os.makedirs(foldername)

        i = 0
        for screenshot in self._screenshots:
            i += 1
            fname = os.path.join(foldername, f"gscreenshot-{i}.png")
            if not self._save_image(screenshot.get_image(), fname, False):
                return False

            screenshot.set_saved_path(fname)

        return True

    def save_last_image(self, filename: typing.Optional[str]= None) -> bool:
        """
        Saves the last screenshot taken with a given filename.
        Returns a boolean for success or fail. A supported file
        extension must be part of the filename provided.

        Parameters:
            str filename

        Returns:
            bool success
        """

        image = self.get_last_image()

        if image is None:
            return False

        if self._save_image(image, filename):
            screenshot = self._screenshots.cursor_current()
            if screenshot is not None:
                screenshot.set_saved_path(filename)

            return True

        return False

    def open_last_screenshot(self) -> bool:
        """
        Calls xdg to open the screenshot in its default application

        Returns:
            bool success
        """
        screenshot_fname = self.save_and_return_path()
        if screenshot_fname is None:
            return False

        try:
            subprocess.run(['xdg-open', screenshot_fname], check=True)
            return True
        except (subprocess.CalledProcessError, IOError, OSError):
            return False

    def copy_last_screenshot_to_clipboard(self) -> bool:
        """
        Copies the last screenshot to the clipboard with
        xclip, if available. Most frontends should try to
        use native methods (e.g. Gdk.Clipboard) if possible.

        Returns:
            bool success
        """
        image = self.get_last_image()

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
                with subprocess.Popen(
                    params,
                    close_fds=True,
                    stdin=subprocess.PIPE,
                    stdout=None,
                    stderr=None) as xclip:

                    xclip.communicate(input=png_data.getvalue())
                    return True
            except (OSError, subprocess.CalledProcessError):
                return False

    def get_last_save_directory(self) -> str:
        """Returns the path of the last save directory"""
        return self.cache["last_save_dir"]

    def get_program_authors(self) -> typing.List[str]:
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

    def get_app_icon(self) -> Image.Image:
        """Returns the application icon"""
        return Image.open(
                resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png')
                )

    def get_program_description(self) -> str:
        """Returns the program description"""
        return "A simple screenshot tool supporting multiple backends."

    def get_program_website(self) -> str:
        """Returns the URL of the program website"""
        return "https://github.com/thenaterhood/gscreenshot"

    def get_program_name(self) -> str:
        """Returns the program name"""
        return "gscreenshot"

    def get_program_license_text(self) -> str:
        """Returns the license text"""
        return resource_string('gscreenshot.resources', 'LICENSE').decode('UTF-8')

    def get_program_license(self) -> str:
        """Returns the license name"""
        return "GPLv2"

    def get_program_version(self, padded: bool=False) -> str:
        """Returns the program version"""
        if not padded:
            return require("gscreenshot")[0].version
        else:
            version = require("gscreenshot")[0].version.split(".")
            padded_version = [v.rjust(2, "0") for v in version]
            return ".".join(padded_version)

    def __repr__(self) -> str:
        return f'Gscreenshot(screenshooter={self.screenshooter})'

    def quit(self):
        """
        Exits the application and interpreter
        """
        sys.exit(0)
