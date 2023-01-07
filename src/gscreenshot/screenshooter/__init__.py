'''
Interface class for integrating a screenshot utility
'''
import os
import subprocess
import tempfile
import typing
import PIL.Image

from pkg_resources import resource_filename
from gscreenshot.screenshot import Screenshot
from gscreenshot.selector import RegionSelector
from gscreenshot.selector import SelectionExecError, SelectionParseError
from gscreenshot.selector import SelectionCancelled, NoSupportedSelectorError
from gscreenshot.selector.factory import SelectorFactory
from gscreenshot.util import session_is_wayland, GSCapabilities

try:
    from Xlib import display
except ImportError:
    display = None


class Screenshooter(object):
    """
    Python interface for a screenshooter
    """

    __slots__ = ('_tempfile', '_selector', '_screenshot')
    __utilityname__: str = "default"

    _screenshot: typing.Optional[Screenshot]
    _tempfile: str
    _selector: typing.Optional[RegionSelector]

    def __init__(self, selector: typing.Optional[RegionSelector]=None):
        """
        constructor
        """
        if selector is None:
            try:
                self._selector = SelectorFactory().create()
            except NoSupportedSelectorError:
                self._selector = None
        else:
            self._selector = selector

        self._screenshot = None
        self._tempfile = os.path.join(
                tempfile.gettempdir(),
                str(os.getpid()) + ".png"
                )

    @property
    def image(self) -> typing.Optional[PIL.Image.Image]:
        """
        Returns the last screenshot taken - PIL Image

        Deprecated. Use Screenshooter.screenshot.get_image().

        Returns:
            PIL.Image or None
        """
        if self._screenshot is not None:
            return self._screenshot.get_image()

        return None

    @property
    def screenshot(self) -> typing.Optional[Screenshot]:
        """
        Returns the last screenshot taken - Screenshot object
        """
        return self._screenshot

    def get_capabilities(self) -> typing.Dict[str, str]:
        """
        Get supported features. Note that under-the-hood the capabilities
        of the selector (if applicable) will be added to this.

        Returns:
            [GSCapabilities]
        """
        return {}

    def get_capabilities_(self) -> typing.Dict[str, str]:
        """
        Get supported features. This should not be overridden by extending
        classes. Implement get_capabilities instead.
        """
        capabilities = self.get_capabilities()
        # If we're running, this is the bare minimum
        capabilities[GSCapabilities.CAPTURE_FULLSCREEN] = self.__utilityname__

        if display is not None and not session_is_wayland():
            capabilities[GSCapabilities.ALTERNATE_CURSOR] = "python-xlib"
            capabilities[GSCapabilities.CURSOR_CAPTURE] = "python-xlib"

        if self._selector is not None:
            capabilities.update(self._selector.get_capabilities())

        return capabilities

    def grab_fullscreen_(self, delay: int=0, capture_cursor: bool=False,
                         use_cursor: typing.Optional[PIL.Image.Image]=None):
        '''
        Internal API method for grabbing the full screen. This should not
        be overridden by extending classes. Implement grab_fullscreen instead.
        '''
        if use_cursor is None and GSCapabilities.CURSOR_CAPTURE in self.get_capabilities():
            self.grab_fullscreen(delay, capture_cursor)
        else:
            self.grab_fullscreen(delay, capture_cursor=False)
            if capture_cursor:
                self.add_fake_cursor(use_cursor)

    def grab_fullscreen(self, delay: int=0, capture_cursor: bool=False):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        raise Exception("Not implemented. Fullscreen grab called with delay " + str(delay))

    def grab_selection_(self, delay: int=0, capture_cursor: bool=False,
                        use_cursor: typing.Optional[PIL.Image.Image]=None,
                        region: typing.Optional[typing.Tuple[int, int, int, int]]=None):
        """
        Internal API method for grabbing a selection. This should not
        be overridden by extending classes. Implement grab_selection instead.

        Takes an interactive screenshot of a selected area with a
        given delay. This has some safety around the interactive selection:
        if it fails to run, it will call a fallback method (which defaults to
        taking a full screen screenshot). if it gives unexpected output it will
        fall back to a full screen screenshot.

        Parameters:
            int delay: seconds
        """
        if region is not None:
            self.grab_fullscreen_(delay, capture_cursor, use_cursor)
            if self._screenshot is not None:
                self._screenshot.set_region(region)
            return

        if self._selector is None:
            self._grab_selection_fallback(delay, capture_cursor)
            return

        try:
            crop_box = self._selector.region_select()
        except SelectionCancelled:
            print("Selection was cancelled")
            self.grab_fullscreen_(delay, capture_cursor, use_cursor)
            return
        except (OSError, SelectionExecError):
            print("Failed to call region selector -- Using fallback region selection")
            self._grab_selection_fallback(delay, capture_cursor)
            return
        except SelectionParseError:
            print("Invalid selection data -- falling back to full screen")
            self.grab_fullscreen_(delay, capture_cursor, use_cursor)
            return

        self.grab_fullscreen_(delay, capture_cursor, use_cursor)

        if self._screenshot is not None:
            self._screenshot.set_region(crop_box)

    def grab_window_(self, delay: int=0, capture_cursor: bool=False,
                     use_cursor: typing.Optional[PIL.Image.Image]=None):
        '''
        Internal API method for grabbing a window. This should not
        be overridden by extending classes. Implement grab_window instead.

        '''
        if use_cursor is None and GSCapabilities.CURSOR_CAPTURE in self.get_capabilities():
            self.grab_window(delay, capture_cursor)
        else:
            self.grab_window(delay, capture_cursor=False)
            if capture_cursor:
                self.add_fake_cursor(use_cursor)

    def grab_window(self, delay: int=0, capture_cursor: bool=False):
        """
        Takes an interactive screenshot of a selected window with a
        given delay. This has a full implementation and may not need
        to be overridden in a child class. By default it will just
        use the selection method, as most region selection and screenshot
        tools don't differentiate.

        Parameters:
            int delay: seconds
        """
        self.grab_selection_(delay, capture_cursor)

    @staticmethod
    def can_run() -> bool:
        """
        Whether this utility can run
        """
        return False

    def get_cursor_position(self) -> typing.Optional[typing.Tuple[int, int]]:
        """
        Gets the current position of the mouse cursor, if able.
        Returns (x, y) or None.
        """
        if display is None:
            return None

        try:
            # This is a ctype
            # pylint: disable=protected-access
            mouse_data = display.Display().screen().root.query_pointer()._data
            if 'root_x' not in mouse_data or 'root_y' not in mouse_data:
                return None
        # pylint: disable=bare-except
        except:
            # We don't really care about the specific error here. If we can't
            # get the pointer, then just move on.
            return None

        return (mouse_data["root_x"], mouse_data["root_y"])

    def add_fake_cursor(self, cursor_img: typing.Optional[PIL.Image.Image]=None):
        """
        Stamps a fake cursor onto the screenshot.
        This is intended for use with screenshot backends that don't
        capture the cursor (or don't capture the cursor in some scenarios)
        """
        if self._screenshot is None:
            return

        cursor_pos = self.get_cursor_position()
        if cursor_pos is None:
            print("Unable to get cursor position - is xlib available?")
            return

        fname = resource_filename(
                  'gscreenshot.resources.pixmaps', 'cursor-adwaita.png'
                )

        if cursor_img is None:
            cursor_img = PIL.Image.open(fname)

        screenshot_img = self._screenshot.get_image().copy()

        screenshot_width, screenshot_height = screenshot_img.size

        # scale the cursor stamp to a reasonable size
        cursor_size_ratio = min(max(screenshot_width / 2000, .3), max(screenshot_height / 2000, .3))
        cursor_height = cursor_img.size[0] * cursor_size_ratio
        cursor_width = cursor_img.size[1] * cursor_size_ratio

        antialias_algo = None
        try:
            antialias_algo = PIL.Image.Resampling.LANCZOS
        except AttributeError: # PIL < 9.0
            antialias_algo = PIL.Image.ANTIALIAS

        cursor_img.thumbnail((int(cursor_width), int(cursor_height)), antialias_algo)

        # If the cursor glyph is square, adjust its position slightly so it
        # shows up where expected.
        if cursor_img.size[0] == cursor_img.size[1]:
            cursor_pos = (
                cursor_pos[0] - 20 if cursor_pos[0] - 20 > 0 else cursor_pos[0],
                cursor_pos[1] - 20 if cursor_pos[1] - 20 > 0 else cursor_pos[1]
            )

        # Passing cursor_img twice is intentional. The second time it's used
        # as a mask (PIL uses the alpha channel) so the cursor doesn't have
        # a black box.
        screenshot_img.paste(cursor_img, cursor_pos, cursor_img)
        self._screenshot = Screenshot(screenshot_img)

    def _grab_selection_fallback(self, delay: int=0, capture_cursor: bool=False):
        """
        Fallback for grabbing the selection, in case the selection tool fails to
        run entirely. Defaults to giving up and just taking a full screen shot.

        Parameters:
            int delay: seconds
        """
        self.grab_fullscreen(delay, capture_cursor)

    def _call_screenshooter(self, screenshooter: str,
                            params: typing.Optional[typing.List[str]]= None) -> bool:

        # This is safer than defaulting to []
        if params is None:
            params = []

        params = [screenshooter] + params
        try:
            subprocess.check_output(params)
            self._screenshot = Screenshot(PIL.Image.open(self._tempfile))
            os.unlink(self._tempfile)
        except (subprocess.CalledProcessError, IOError, OSError):
            self._screenshot = None
            return False

        return True

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(selector={self._selector})'
