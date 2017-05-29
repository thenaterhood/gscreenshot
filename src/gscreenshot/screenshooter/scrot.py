import os
import subprocess
import tempfile
import PIL.Image
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
        self._call_scrot(['-d', str(delay)])

    def _grab_selection_fallback(self, delay=0):
        self._call_scrot(['-d', str(delay), '-s'])

    def _call_scrot(self, params=None):
        """
        Performs a subprocess call to scrot with a given list of
        parameters.

        Parameters:
            array[string]
        """

        # This is safer than passing an empty
        # list as a default value
        if params is None:
            params = []

        params = ['scrot', '-z', self.tempfile] + params
        try:
            subprocess.check_output(params)
            self._image = PIL.Image.open(self.tempfile)
            os.unlink(self.tempfile)
        except subprocess.CalledProcessError:
            self._image = None
