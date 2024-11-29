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
from PIL import Image
from gscreenshot.compat import get_resource_file, get_resource_string, get_version
from gscreenshot.screenshot import ScreenshotCollection
from gscreenshot.screenshooter import Screenshooter, get_screenshooter
from gscreenshot.util import session_is_wayland

_ = gettext.gettext


#pylint: disable=missing-class-docstring
class GscreenshotClipboardException(Exception):
    pass


class Gscreenshot(object):
    """
    Gscreenshot application
    """

    __slots__ = ['screenshooter', 'cache', 'session', '_screenshots', '_stamps', '_select_color']

    screenshooter: Screenshooter
    cache: typing.Dict[str, str]
    _screenshots: ScreenshotCollection
    _stamps: typing.Dict[str, Image.Image]
    session: typing.Dict[str, typing.Any]

    # generated using piexif
    EXIF_TEMPLATE = b'Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x02\x011\x00\x02\x00\x00\x00\x15\x00\x00\x00&\x87i\x00\x04\x00\x00\x00\x01\x00\x00\x00;\x00\x00\x00\x00gscreenshot [[VERSION]]\x00\x00\x01\x90\x03\x00\x02\x00\x00\x00\x14\x00\x00\x00I[[CREATE_DATE]]\x00' #pylint: disable=line-too-long

    def __init__(self, screenshooter=None):
        """
        constructor
        """
        self.session = {}
        try:
            locale_path = get_resource_file("gscreenshot.resources", "locale")
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

        self.screenshooter = get_screenshooter(screenshooter)
        self._screenshots = ScreenshotCollection()

        self._stamps = {}
        self._select_color = None

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

    def set_select_color(self, select_color_rgba: str):
        self._select_color = select_color_rgba

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

        existing = self.get_available_cursors()
        i = 0
        while name in existing:
            name = f"Custom{i}"
            i += 1

        if len(name) > 9:
            name = f"{name[0:8]}..."

        self._stamps[name] = glyph

        return name

    def get_available_cursors(self) -> typing.Dict[str, typing.Optional[Image.Image]]:
        '''
        Get the alternate pointer pixmaps gscreenshot can use
        Returns {name: PIL.Image}
        '''
        pixmaps_path = "gscreenshot.resources.pixmaps"

        adwaita_path = get_resource_file(pixmaps_path, "cursor-adwaita.png")
        prohibit_path = get_resource_file(pixmaps_path, "cursor-prohibit.png")
        allow_path = get_resource_file(pixmaps_path, "cursor-allow.png")

        available = {
            'theme': None,
            'adwaita': Image.open(
                adwaita_path
            ),
            'prohibit': Image.open(
                prohibit_path
            ),
            'allow': Image.open(
                allow_path
            )
        }

        if session_is_wayland():
            del available['theme']

        available.update(self._stamps)
        return available

    def get_cursor_by_name(self, name: typing.Optional[str]):
        '''
        Get the cursor glyph that goes by the given name. This is
        safe to call with None or bad names and will return a default
        value.
        '''
        cursors = self.get_available_cursors()
        #pylint: disable=consider-iterating-dictionary
        default = list(cursors.keys())[0]

        if name and name in cursors.keys():
            return cursors[name]

        return cursors[default]

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
                                cursor_name: typing.Optional[str]=None,
                                overwrite: bool=False, count: int=1
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
            use_cursor = self.get_cursor_by_name(cursor_name)

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
                    self._screenshots.insert(self.screenshooter.screenshot)

        self.run_display_mismatch_warning()

        return self.get_last_image()

    #pylint: disable=too-many-arguments
    def screenshot_selected(self, delay: int=0, capture_cursor: bool=False,
                            cursor_name: typing.Optional[str]=None,
                            overwrite: bool=False, count: int=1,
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
            use_cursor = self.get_cursor_by_name(cursor_name)

        for _ in range(0, count):
            self.screenshooter.grab_selection_(
                delay,
                capture_cursor,
                use_cursor=use_cursor,
                region=region,
                select_color_rgba=self._select_color,
            )

            if self.screenshooter.screenshot is not None:
                if overwrite:
                    self._screenshots.replace(self.screenshooter.screenshot)
                else:
                    self._screenshots.insert(self.screenshooter.screenshot)

        self.run_display_mismatch_warning()

        return self.get_last_image()

    #pylint: disable=too-many-arguments
    def screenshot_window(self, delay: int=0, capture_cursor: bool=False,
                          cursor_name: typing.Optional[str]=None,
                          overwrite: bool=False, count: int=1
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
            use_cursor = self.get_cursor_by_name(cursor_name)

        for _ in range(0, count):
            self.screenshooter.grab_window_(
                delay,
                capture_cursor,
                use_cursor=use_cursor,
                select_color_rgba=self._select_color,
            )

            if self.screenshooter.screenshot is not None:
                if overwrite:
                    self._screenshots.replace(self.screenshooter.screenshot)
                else:
                    self._screenshots.insert(self.screenshooter.screenshot)

        self.run_display_mismatch_warning()

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
                    overwrite: bool=True) -> typing.Optional[str]:
        '''
        Internal method for saving an image to a file
        '''
        if filename is None:
            filename = self.get_time_filename()
        else:
            filename = self.interpolate_filename(filename)

        file_type = "png"

        if "/dev" not in filename or filename.index("/dev") != 0:

            file_extension = os.path.splitext(filename)[1][1:].lower()

            if file_extension == "":
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
                file_type = 'png'

            else:
                file_type = file_extension

            if not overwrite and os.path.exists(filename):
                return None

            self.cache["last_save_dir"] = os.path.dirname(filename)
            self.save_cache()

        if file_type == 'jpg':
            file_type = 'jpeg'

        if file_type not in self.get_supported_formats():
            return None

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

            # open(... , 'w*') truncates the file, so this is not vulnerable
            # to the 2023 android and windows 11 problem of leaking data from
            # cropped screenshots.
            with open(filename, "wb") as file_pointer:
                image.save(file_pointer, file_type.upper(), exif=exif_data)

        except IOError:
            filename = None

        screenshot = self._screenshots.cursor_current()
        if screenshot is not None:
            screenshot.set_saved_path(filename)

        return filename

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
            if self._save_image(screenshot.get_image(), fname, False) is not None:
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

        saved_path = self._save_image(image, filename)
        if saved_path:
            screenshot = self._screenshots.cursor_current()
            if screenshot is not None:
                screenshot.set_saved_path(saved_path)

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
        clipper_name = "xclip"

        if session_is_wayland():
            params = [
                    'wl-copy',
                    '-t',
                    'image/png'
                ]
            clipper_name = "wl-copy"

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
                #pylint: disable=raise-missing-from
                raise GscreenshotClipboardException(clipper_name)

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
        pixmaps_path = 'gscreenshot.resources.pixmaps'
        filename = get_resource_file(pixmaps_path, "gscreenshot.png")
        return Image.open(filename)

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
        return get_resource_string("gscreenshot.resources", "LICENSE")

    def get_program_license(self) -> str:
        """Returns the license name"""
        return "GPLv2"

    def get_program_version(self, padded: bool=False) -> str:
        """Returns the program version"""
        if not padded:
            return get_version()
        else:
            version_str = get_version().split(".")
            padded_version = [v.rjust(2, "0") for v in version_str]
            return ".".join(padded_version)

    def __repr__(self) -> str:
        return f'Gscreenshot(screenshooter={self.screenshooter})'

    def quit(self):
        """
        Exits the application and interpreter
        """
        sys.exit(0)
