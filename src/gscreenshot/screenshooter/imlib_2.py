'''
Integration for the imlib2 screenshot utility
'''
from time import sleep

from gscreenshot.screenshooter import Screenshooter
from gscreenshot.util import find_executable


class Imlib2(Screenshooter):
    """
    Python class wrapper for the scrot screenshooter utility
    """

    __utilityname__ = "imlib_2"

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
        self._call_screenshooter('imlib2_grab', [self.tempfile])

    @staticmethod
    def can_run() -> bool:
        '''Whether this utility is available'''
        return find_executable('imlib2_grab') is not None
