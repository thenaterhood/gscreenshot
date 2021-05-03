'''
Integration for the PIL screenshot functionality
'''
from time import sleep
from gscreenshot.screenshooter import Screenshooter

SUPPORTED_PLATFORM = False

try:
    from PIL import ImageGrab
    SUPPORTED_PLATFORM = True
except ImportError:
    SUPPORTED_PLATFORM = False


class PILWrapper(Screenshooter):
    """
    Python class wrapper for PIL
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
        self._image = ImageGrab.grab(None)

    @staticmethod
    def can_run():
        '''Whether this utility is available'''
        return SUPPORTED_PLATFORM
