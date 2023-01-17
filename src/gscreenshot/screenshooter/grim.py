'''
Integration for the grim screenshot utility
'''
from time import sleep
import subprocess
import typing

from gscreenshot.util import find_executable, GSCapabilities
from gscreenshot.screenshooter import Screenshooter


class Grim(Screenshooter):
    """
    Python class wrapper for the grim screenshooter utility
    """

    __utilityname__ = "grim"

    def __init__(self):
        """
        constructor
        """
        Screenshooter.__init__(self)

    def grab_fullscreen(self, delay=0, capture_cursor=False):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        sleep(delay)
        params = [self._tempfile]

        if capture_cursor:
            params = ['-c', self._tempfile]

        self._call_screenshooter('grim', params)

    @staticmethod
    def can_run() -> bool:
        """Whether grim is available"""
        if find_executable('grim') is None:
            return False

        # Grim doesn't work in all situations. In some we would rather
        # use the xdg-desktop-portal method so we'll do another check
        try:
            subprocess.check_output(["grim", "-"])
        except subprocess.CalledProcessError:
            return False

        return True

    def get_capabilities(self) -> typing.Dict[str, str]:
        """
        Get supported features
        """
        return {
            GSCapabilities.CURSOR_CAPTURE: self.__utilityname__
        }
