from time import sleep

from gscreenshot.screenshooter import Screenshooter
from gscreenshot.selector.slop import Slop
from gscreenshot.util import find_executable


class Imlib2(Screenshooter):

    """
    Python class wrapper for the scrot screenshooter utility
    """

    def __init__(self):
        """
        constructor
        """
        Screenshooter.__init__(self)
        self.selector = Slop()

    def grab_fullscreen(self, delay=0):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        sleep(delay)
        self._call_screenshooter('imlib2_grab', [self.tempfile])

    @staticmethod
    def can_run():
        return find_executable('imlib2_grab') is not None

