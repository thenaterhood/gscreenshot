import os
import tempfile
from gscreenshot.selector import SelectionExecError, SelectionParseError, SelectionCancelled


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
        given delay. This has some safety around the interactive selection:
        if it fails to run, it will call a fallback method (which defaults to
        taking a full screen screenshot). if it gives unexpected output it will
        fall back to a full screen screenshot.

        Parameters:
            int delay: seconds
        """
        try:
            crop_box = self.selector.region_select()
        except (SelectionCancelled) as e:
            print("Selection was cancelled")
            return
        except (OSError, SelectionExecError) as e:
            print("Failed to call region selector -- Using fallback region selection")
            self._grab_selection_fallback(delay)
            return
        except (SelectionParseError) as e:
            print("Invalid selection data -- falling back to full screen")
            self.grab_fullscreen(delay)
            return

        self.grab_fullscreen(delay)
        self._image = self._image.crop(crop_box)

    def grab_window(self, delay=0):
        """
        Takes an interactive screenshot of a selected window with a
        given delay

        Parameters:
            int delay: seconds
        """
        self.grab_selection(delay)

    def _grab_selection_fallback(self, delay=0):
        """
        Fallback for grabbing the selection, in case the selection tool fails to
        run entirely. Defaults to giving up and just taking a full screen shot.

        Parameters:
            int delay: seconds
        """
        self.grab_fullscreen(delay)
