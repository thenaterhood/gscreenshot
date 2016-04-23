import subprocess
import tempfile
import subprocess
from time import sleep
from PIL import Image
import os

class Scrot(object):
    """
    Python class wrapper for the scrot screenshooter utility
    """

    __slots__ = ('image', 'tempfile')

    def __init__(self):
        """
        constructor
        """

        self.image = None
        self.tempfile = os.path.join(
                tempfile.gettempdir(),
                str(os.getpid()) + ".png"
                )

    def get_image(self):
        """
        Returns the last screenshot taken

        Returns:
            PIL.Image or None
        """
        return self.image

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
        given delay

        Parameters:
            int delay: seconds
        """

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

        params = ['scrot', self.tempfile] + params
        subprocess.check_output(params)

        self.image = Image.open(self.tempfile)
        os.unlink(self.tempfile)
