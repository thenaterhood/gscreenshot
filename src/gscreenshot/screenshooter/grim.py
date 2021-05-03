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

    def grab_fullscreen(self, delay=0):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        sleep(delay)
        self._call_screenshooter('grim', ['-o', self.tempfile])

    @staticmethod
    def can_run():
        """Whether scrot is available"""
        return find_executable('grim') is not None

    def _grab_selection_fallback(self, delay=0):
        sleep(delay)
        self._call_screenshooter('grim', ['-o', self.tempfile])
