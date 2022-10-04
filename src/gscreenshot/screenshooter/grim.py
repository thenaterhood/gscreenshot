'''
Integration for the grim screenshot utility
'''
from time import sleep
import subprocess

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
        params = [self.tempfile]

        if capture_cursor:
            params = ['-c', self.tempfile]

        self._call_screenshooter('grim', params)

    @staticmethod
    def can_run():
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

    def get_capabilities(self):
        """
        Get supported features
        """
        capabilities = [
            GSCapabilities.CURSOR_CAPTURE
        ]

        return capabilities + self.selector.get_capabilities()

    def _grab_selection_fallback(self, delay=0, capture_cursor=False):
        sleep(delay)
        params = [self.tempfile]

        if capture_cursor:
            params = ['-c', self.tempfile]

        self._call_screenshooter('grim', params)
