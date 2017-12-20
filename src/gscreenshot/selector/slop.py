import subprocess
from gscreenshot.selector import SelectionParseError, SelectionExecError, SelectionCancelled


class Slop(object):

    """
    Python class wrapper for the slop region selection tool

    All methods return a tuple of; the x, y coordinates
    of both corners of the selection.
    """

    def __init__(self):
        """
        constructor
        """
        pass

    def region_select(self):
        """
        Select an arbitrary region of the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        return self._get_boundary_interactive()

    def window_select(self):
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        return self._get_boundary_interactive()

    def grab_window(self, delay=0):
        """
        Takes an interactive screenshot of a selected window with a
        given delay

        Parameters:
            int delay: seconds
        """
        self.grab_selection(delay)

    def _get_boundary_interactive(self):
        """
        Calls slop and returns the boundary produced by
        slop
        """
        try:
            # nodecorations=0 - this is the slop default, but there's a bug
            # so skipping the "=0" causes a segfault.
            p = subprocess.Popen(
                ['slop', '--nodecorations=0', '-f', 'X=%x,Y=%y,W=%w,H=%h'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )
            stdout, stderr = p.communicate()
            return_code = p.returncode
        except OSError:
            raise SelectionExecError("Slop was not found")

        if (return_code != 0):
            slop_error = stderr.decode("UTF-8")

            if ("cancelled" in slop_error):
                raise SelectionCancelled("Selection was cancelled")
            else:
                raise SelectionExecError(slop_error)

        slop_output = stdout.decode("UTF-8").strip().split(",")

        slop_parsed = {}
        # We iterate through the output so we're not reliant
        # on the order or number of lines in slop's output
        for l in slop_output:
            if ('=' in l):
                spl = l.split("=")
                slop_parsed[spl[0]] = spl[1]

        # (left, upper, right, lower)
        try:
            crop_box = (
                int(slop_parsed['X']),
                int(slop_parsed['Y']),
                int(slop_parsed['X']) + int(slop_parsed['W']),
                int(slop_parsed['Y']) + int(slop_parsed['H'])
            )
        except KeyError:
            raise SelectionParseError("Unexpected slop output")

        return crop_box
