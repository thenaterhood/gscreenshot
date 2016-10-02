import os
import subprocess
import tempfile
from PIL import Image
from gscreenshot.screenshooter import Screenshooter


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
            crop_box = self._get_boundary_interactive()
            self._call_scrot(['-d', str(delay)])
            self._image = self._image.crop(crop_box)
        except FileNotFoundError:
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
        subprocess.check_output(params)

        self._image = Image.open(self.tempfile)
        os.unlink(self.tempfile)

    def _get_boundary_interactive(self):
        """
        Calls slop and returns the boundary produced by
        slop
        """
        proc_output = subprocess.check_output(['slop'])
        slop_output = proc_output.decode("UTF-8").strip().split("\n")

        slop_parsed = {}
        # We iterate through the output so we're not reliant
        # on the order or number of lines in slop's output
        for l in slop_output:
            spl = l.split("=")
            slop_parsed[spl[0]] = spl[1]

        # (left, upper, right, lower)
        crop_box = (
            int(slop_parsed['X']),
            int(slop_parsed['Y']),
            int(slop_parsed['X']) + int(slop_parsed['W']),
            int(slop_parsed['Y']) + int(slop_parsed['H'])
        )

        return crop_box
