'''
Integration for the grim screenshot utility
'''
from time import sleep

from gscreenshot.util import find_executable
from gscreenshot.screenshooter import Screenshooter


class Grim(Screenshooter):
    """
    Python class wrapper for the grim screenshooter utility
    """

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
        """Whether scrot is available"""
        return find_executable('grim') is not None

    def _grab_selection_fallback(self, delay=0, capture_cursor=False):
        sleep(delay)
        params = [self.tempfile]

        if capture_cursor:
            params = ['-c', self.tempfile]

        self._call_screenshooter('grim', params)
