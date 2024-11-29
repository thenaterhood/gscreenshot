'''
Interface class for integrating a screenshot utility
'''
import os
import subprocess
import tempfile
import typing
import PIL.Image
from gscreenshot.cursor_locator.factory import get_cursor_locator

from gscreenshot.scaling import get_scaling_method_name
from gscreenshot.screenshot import Screenshot
from gscreenshot.screenshot.effects import CropEffect
from gscreenshot.screenshot.effects import StampEffect
from gscreenshot.selector import RegionSelector, get_region_selector
from gscreenshot.selector.exceptions import SelectionExecError, SelectionParseError
from gscreenshot.selector.exceptions import SelectionCancelled, NoSupportedSelectorError
from gscreenshot.util import GSCapabilities
from .exceptions import ScreenshotError


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
                self._selector = get_region_selector()
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

        try:
            cursor_locator = get_cursor_locator()
        # pylint: disable=bare-except
        except:
            cursor_locator = None

        if cursor_locator is not None:
            capabilities[GSCapabilities.ALTERNATE_CURSOR] = cursor_locator.__utilityname__
            capabilities[GSCapabilities.CURSOR_CAPTURE] = cursor_locator.__utilityname__

        scaling_name = get_scaling_method_name()
        capabilities[GSCapabilities.SCALING_DETECTION] = scaling_name

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
            if capture_cursor and use_cursor and self._screenshot:
                cursor_position = self.get_cursor_position()
                if cursor_position is not None:
                    stamp = StampEffect(use_cursor, cursor_position)
                    stamp.set_alias("cursor")
                    self._screenshot.add_effect(stamp)

    def grab_fullscreen(self, delay: int=0, capture_cursor: bool=False):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        raise NotImplementedError(
            "Not implemented. Fullscreen grab called with delay " + str(delay)
            )

    def grab_selection_(self, delay: int=0, capture_cursor: bool=False,
                        use_cursor: typing.Optional[PIL.Image.Image]=None,
                        region: typing.Optional[typing.Tuple[int, int, int, int]]=None,
                        select_color_rgba: typing.Optional[str]=None):
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
                crop = CropEffect(region)
                crop.set_alias("region")
                self._screenshot.add_effect(crop)
            return

        if self._selector is None:
            self._grab_selection_fallback(delay, capture_cursor)
            return

        try:
            crop_box = self._selector.region_select(selection_box_rgba=select_color_rgba)
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
            crop = CropEffect(crop_box)
            crop.set_alias("region")
            self._screenshot.add_effect(crop)

    def grab_window_(self, delay: int=0, capture_cursor: bool=False,
                     use_cursor: typing.Optional[PIL.Image.Image]=None,
                    select_color_rgba: typing.Optional[str]=None):
        '''
        Internal API method for grabbing a window. This should not
        be overridden by extending classes. Implement grab_window instead.

        '''
        self.grab_selection_(delay, capture_cursor, use_cursor, select_color_rgba=select_color_rgba)

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

        try:
            cursor_locator = get_cursor_locator()
            return cursor_locator.get_cursor_position_adjusted()
        # pylint: disable=bare-except
        except:
            # We don't really care about the specific error here. If we can't
            # get the pointer, then just move on.
            return None

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
        self._screenshot = None
        try:
            screenshot_output = subprocess.check_output(params)
            if not os.path.exists(self._tempfile):
                if len(screenshot_output.decode()) > 0:
                    raise ScreenshotError(f"screenshot failed: {screenshot_output.decode()}")
                raise ScreenshotError("screenshot failed but provided no output")

            self._screenshot = Screenshot(PIL.Image.open(self._tempfile))
            os.unlink(self._tempfile)
        except (subprocess.CalledProcessError, IOError, OSError, ScreenshotError) as exc:
            print(repr(exc))

        return self._screenshot is not None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(selector={self._selector})'
