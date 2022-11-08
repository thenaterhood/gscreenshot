'''
ImageMagick screenshot class
'''
from time import sleep

from gscreenshot.screenshooter import Screenshooter
from gscreenshot.util import find_executable
from gscreenshot.util import GSCapabilities


class ImageMagick(Screenshooter):
    """
    Python class wrapper for the scrot screenshooter utility
    """

    __utilityname__ = "imagemagick"

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
        self._call_screenshooter('import', ['-window', 'root', self.tempfile])

    def get_capabilities(self) -> list:
        '''List of capabilities'''
        return [
            GSCapabilities.REGION_SELECTION,
            GSCapabilities.WINDOW_SELECTION
        ]

    @staticmethod
    def can_run() -> bool:
        '''Whether this utility is available'''
        return find_executable('import') is not None

    def _grab_selection_fallback(self, delay=0, capture_cursor=False):
        sleep(delay)
        if not self._call_screenshooter('import', [self.tempfile]):
            super()._grab_selection_fallback(delay=0)
