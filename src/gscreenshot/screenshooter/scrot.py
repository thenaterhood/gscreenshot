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

        self._image = None
        self.tempfile = os.path.join(
            tempfile.gettempdir(),
            str(os.getpid()) + ".png"
        )
        self.selector = Slop()

    def grab_fullscreen(self, delay=0):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        self._call_scrot(['-d', str(delay)])

    def grab_selection(self, delay=0):
        """
        Takes an interactive screenshot of a selected area with a
        given delay. This attempts to use slop to select an
        area rather than using scrot's builtin selection as
        scrot's builtin selection does not work well, but will
        fall back on scrot's if slop is not available.

        Parameters:
            int delay: seconds
        """

        try:
            crop_box = self.selector.region_select()
            if crop_box is not None:
                self._call_scrot(['-d', str(delay)])
                self._image = self._image.crop(crop_box)
        except OSError:
            self._call_scrot(['-d', str(delay), '-s'])

    def grab_window(self, delay=0):
        """
        Takes an interactive screenshot of a selected window with a
        given delay

        Parameters:
            int delay: seconds
        """
        self.grab_selection(delay)

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
            pass

