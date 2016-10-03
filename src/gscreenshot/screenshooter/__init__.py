import os
import tempfile


class Screenshooter(object):
    """
    Python interface for a screenshooter
    """

    __slots__ = ('_image', 'tempfile')

    def __init__(self):
        """
        constructor
        """

        self._image = None
        self.tempfile = os.path.join(
                tempfile.gettempdir(),
                str(os.getpid()) + ".png"
                )

    @property
    def image(self):
        """
        Returns the last screenshot taken

        Returns:
            PIL.Image or None
        """
        return self._image

    def grab_fullscreen(self, delay=0):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        raise Exception("Not implemented")

    def grab_selection(self, delay=0):
        """
        Takes an interactive screenshot of a selected area with a
        given delay

        Parameters:
            int delay: seconds
        """
        raise Exception("Not implemented")

    def grab_window(self, delay=0):
        """
        Takes an interactive screenshot of a selected window with a
        given delay

        Parameters:
            int delay: seconds
        """
        raise Exception("Not implemented")

