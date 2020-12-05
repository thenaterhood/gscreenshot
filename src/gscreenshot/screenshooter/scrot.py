'''
Integration for the Scrot screenshot utility
'''
from gscreenshot.util import find_executable
from gscreenshot.screenshooter import Screenshooter
from gscreenshot.selector.slop import Slop


class Scrot(Screenshooter):
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
        self._call_screenshooter('scrot', ['-z', self.tempfile, '-d', str(delay)])

    @staticmethod
    def can_run():
        """Whether scrot is available"""
        return find_executable('scrot') is not None

    def _grab_selection_fallback(self, delay=0):
        self._call_screenshooter('scrot', ['-z', self.tempfile, '-d', str(delay), '-s'])
