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
import json
import locale
import logging
import os
import sys
import typing

from PIL import Image
from gscreenshot.actions import NotifyAction
from gscreenshot.compat import deprecated, get_resource_file
from gscreenshot.meta import (
    get_app_icon,
    get_program_authors,
    get_program_description,
    get_program_license,
    get_program_license_text,
    get_program_name,
    get_program_version,
    get_program_website,
)
from gscreenshot.screenshot import ScreenshotCollection
from gscreenshot.screenshooter import Screenshooter, get_screenshooter

from gscreenshot.screenshot.actions import (
    CopyAction,
    SaveAction,
    SaveTmpfileAction,
    XdgOpenAction
)
from gscreenshot.screenshot.screenshot import Screenshot
from gscreenshot.util import (
    get_supported_formats,
    session_is_mismatched,
    session_is_wayland,
)
from gscreenshot.filename import (
    get_time_filename,
    get_time_foldername,
    interpolate_filename,
)

_ = gettext.gettext
log = logging.getLogger(__name__)


class Gscreenshot():
    """
    Gscreenshot application
    """

    __slots__ = [
        'screenshooter',
        'cache',
        'session',
        '_screenshots',
        '_stamps',
        '_select_color',
        '_select_border_weight',
    ]

    screenshooter: Screenshooter
    cache: typing.Dict[str, str]
    _screenshots: ScreenshotCollection
    _stamps: typing.Dict[str, Image.Image]
    session: typing.Dict[str, typing.Any]

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
        self._select_border_weight = None

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

    @property
    def screenshots(self) -> ScreenshotCollection:
        return self._screenshots

    @property
    def current(self) -> Screenshot | None:
        return self._screenshots.cursor_current()

    @property
    def current_always(self) -> Screenshot:
        return self._screenshots.cursor_current_fallback()

    def get_capabilities(self) -> typing.Dict[str, str]:
        '''
        Get the features supported in the current setup
        '''
        return self.screenshooter.get_capabilities_()

    def set_select_color(self, select_color_rgba: str):
        '''
        Set the selection color for region selection
        This accepts an RGBA hexadecimal string.
        '''
        log.debug("set select color to '%s'", select_color_rgba)
        self._select_color = select_color_rgba

    def set_select_border_weight(self, select_border_weight: int):
        '''Set the border weight for region selection'''
        log.debug("set select border weight to '%s'", select_border_weight)
        self._select_border_weight = select_border_weight

    def register_stamp_image(self, fname: str,
        name: typing.Optional[str]=None
    ) -> typing.Optional[str]:
        '''
        Adds a new stamp image from a file path
        '''
        if not os.path.exists(fname):
            log.info("cursor glyph path '%s' does not exist", fname)
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
        log.debug("added cursor path = '%s', name = '%s'", fname, name)

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

        log.info("cursor glyph name = '%s' does not exist, using default", name)
        return cursors[default]

    @deprecated("deprecated 3.9.0: use NotifyAction().execute")
    def show_screenshot_notification(self) -> bool:
        '''
        Show a notification that a screenshot was taken.
        This method is a "fire-and-forget" and won't
        return a status as to whether it succeeded.
        '''
        return NotifyAction().execute()

    def run_display_mismatch_warning(self):
        '''
        Send a notification if the screenshot was taken from a
        non-X11 or wayland session.
        '''
        if session_is_mismatched():
            NotifyAction().execute()

    def get_cache_file(self) -> str:
        """
        Find the gscreenshot cache file and return its path
        """
        if 'XDG_CACHE_HOME' in os.environ:
            return os.environ['XDG_CACHE_HOME'] + "/gscreenshot"
        return os.path.expanduser("~/.gscreenshot")

    def save_cache(self):
        """Writes the cache to disk"""
        try:
            with open(self.get_cache_file(), "w", encoding="UTF-8") as cachefile:
                json.dump(self.cache, cachefile)
                log.debug("wrote cache file '%s'", self.get_cache_file())
        except FileNotFoundError:
            log.warning(_("unable to save cache file - file not found"))

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

        screenshot = None

        for _ in range(0, count):
            self.screenshooter.grab_fullscreen_(
                delay,
                capture_cursor,
                use_cursor=use_cursor
            )

            screenshot = self.screenshooter.screenshot

            if screenshot is not None:
                if overwrite:
                    self._screenshots.replace(screenshot)
                else:
                    self._screenshots.insert(screenshot)

        self.run_display_mismatch_warning()

        if screenshot:
            return screenshot.get_image()

        return None

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
        screenshot = None
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
                select_border_weight=self._select_border_weight,
            )

            screenshot = self.screenshooter.screenshot

            if screenshot is not None:
                if overwrite:
                    self._screenshots.replace(screenshot)
                else:
                    self._screenshots.insert(screenshot)

        self.run_display_mismatch_warning()

        if screenshot:
            return screenshot.get_image()

        return None

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
        screenshot = None

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
                select_border_weight=self._select_border_weight,
            )

            screenshot = self.screenshooter.screenshot

            if screenshot is not None:
                if overwrite:
                    self._screenshots.replace(screenshot)
                else:
                    self._screenshots.insert(screenshot)

        self.run_display_mismatch_warning()

        if screenshot:
            return screenshot.get_image()

        return None

    @deprecated("deprecated 3.9.0: use Gscreenshot.current.get_image()")
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

    @deprecated("deprecated 3.9.0: use util.get_supported_formats instead")
    def get_supported_formats(self) -> typing.List[str]:
        """Get supported image formats"""
        return get_supported_formats()

    @deprecated("deprecated 3.9.0: use Gscreenshot.current_always.get_preview")
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
        return self.current_always.get_preview(width, height, with_border)

    @deprecated("deprecated 3.9.0: use filename.get_time_filename instead")
    def get_time_filename(self) -> str:
        """
        Generates a returns a filename based on the current time

        Returns:
            str
        """
        return get_time_filename(self._screenshots.cursor_current())

    @deprecated("deprecated 3.9.0: use filename.interpolate_filename instead")
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
        return interpolate_filename(
            filename,
            self._screenshots.cursor_current(),
        )

    @deprecated("deprecated 3.9.0: use filename.get_time_foldername instead")
    def get_time_foldername(self) -> str:
        '''Generates a time-based folder name'''
        return get_time_foldername(self._screenshots.cursor_current())

    @deprecated("deprecated 3.9.0: use SaveTmpFileAction.execute instead")
    def save_and_return_path(self) -> typing.Optional[str]:
        """
        Saves the last screenshot to /tmp if it hasn't been saved
        and returns the path to it.

        Returns:
            str
        """
        return SaveTmpfileAction().execute(self._screenshots.cursor_current())

    def save_screenshot_collection(self, foldername: typing.Optional[str]=None) -> bool:
        '''
        Saves every image in the current screenshot collection
        '''

        if foldername is None:
            foldername = get_time_foldername(None)
        else:
            foldername = interpolate_filename(foldername)

        if not os.path.exists(foldername):
            try:
                os.makedirs(foldername)
            except (IOError, OSError) as exc:
                log.info("failed to make tree '%s': %s", foldername, exc)

        i = 0
        for screenshot in self._screenshots:
            i += 1
            fname = os.path.join(foldername, f"gscreenshot-{i}.png")
            SaveAction(filename=fname, overwrite=False).execute(screenshot)

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
        path = SaveAction(filename=filename).execute(self._screenshots.cursor_current())
        if path:
            self.cache["last_save_dir"] = os.path.dirname(path)
            self.save_cache()

        return path is not None

    @deprecated("deprecated 3.9.0: use XdgOpenAction.execute")
    def open_last_screenshot(self) -> bool:
        """
        Calls xdg to open the screenshot in its default application

        Returns:
            bool success
        """
        return XdgOpenAction().execute(self._screenshots.cursor_current())

    @deprecated("deprecated 3.9.0: use CopyAction.execute")
    def copy_last_screenshot_to_clipboard(self) -> bool:
        """
        Copies the last screenshot to the clipboard with
        xclip, if available. Most frontends should try to
        use native methods (e.g. Gdk.Clipboard) if possible.

        Returns:
            bool success
        """
        return CopyAction().execute(self._screenshots.cursor_current())

    def get_last_save_directory(self) -> str:
        """Returns the path of the last save directory"""
        return self.cache["last_save_dir"]

    @deprecated("deprecated 3.9.0: use meta.get_program_authors instead")
    def get_program_authors(self) -> typing.List[str]:
        """
        Returns the list of authors

        Returns:
            string[]
        """
        return get_program_authors()

    @deprecated("deprecated 3.9.0: use meta.get_app_icon instead")
    def get_app_icon(self) -> Image.Image:
        """Returns the application icon"""
        return get_app_icon()

    @deprecated("deprecated 3.9.0: use meta.get_program_description instead")
    def get_program_description(self) -> str:
        """Returns the program description"""
        return get_program_description()

    @deprecated("deprecated 3.9.0: use meta.get_program_website instead")
    def get_program_website(self) -> str:
        """Returns the URL of the program website"""
        return get_program_website()

    @deprecated("deprecated 3.9.0: use meta.get_program_name instead")
    def get_program_name(self) -> str:
        """Returns the program name"""
        return get_program_name()

    @deprecated("deprecated 3.9.0: use meta.get_program_license_text instead")
    def get_program_license_text(self) -> str:
        """Returns the license text"""
        return get_program_license_text()

    @deprecated("deprecated 3.9.0: use meta.get_program_license instead")
    def get_program_license(self) -> str:
        """Returns the license name"""
        return get_program_license()

    @deprecated("deprecated 3.9.0: use meta.get_program_version instead")
    def get_program_version(self, padded: bool=False) -> str:
        """Returns the program version"""
        return get_program_version(padded)

    def __repr__(self) -> str:
        return f'Gscreenshot(screenshooter={self.screenshooter})'

    def quit(self):
        """
        Exits the application and interpreter
        """
        sys.exit(0)
