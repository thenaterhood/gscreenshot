'''
Integration for the Scrot screenshot utility
'''
from gscreenshot.util import find_executable
from gscreenshot.screenshooter import Screenshooter


class Scrot(Screenshooter):
    """
    Python class wrapper for the scrot screenshooter utility
    """

    def __init__(self):
        """
        constructor
        """
        Screenshooter.__init__(self)
        self.supports_native_cursor_capture = True

    def grab_fullscreen(self, delay=0, capture_cursor=False):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        params = ['-z', self.tempfile, '-d', str(delay)]
        if capture_cursor:
            params.append('-p')

        self._call_screenshooter('scrot', params)

    @staticmethod
    def can_run():
        """Whether scrot is available"""
        return find_executable('scrot') is not None

    def _grab_selection_fallback(self, delay=0, capture_cursor=False):
        params =  ['-z', self.tempfile, '-d', str(delay), '-s']
        if capture_cursor:
            params.append('-p')

        self._call_screenshooter('scrot', params)
