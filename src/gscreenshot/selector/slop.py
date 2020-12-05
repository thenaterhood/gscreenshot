'''
Wrapper for the slop screen selector utility
'''
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

    def _get_boundary_interactive(self):
        """
        Calls slop and returns the boundary produced by
        slop
        """
        try:
            # nodecorations=0 - this is the slop default, but there's a bug
            # so skipping the "=0" causes a segfault.
            process = subprocess.Popen(
                ['slop', '--nodecorations=0', '-f', 'X=%x,Y=%y,W=%w,H=%h'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )
            stdout, stderr = process.communicate()
            return_code = process.returncode
        except OSError as exception:
            #pylint: disable=raise-missing-from
            raise SelectionExecError("Slop was not found") #from exception

        if return_code != 0:
            slop_error = stderr.decode("UTF-8")

            if "cancelled" in slop_error:
                raise SelectionCancelled("Selection was cancelled")

            raise SelectionExecError(slop_error)

        slop_output = stdout.decode("UTF-8").strip().split(",")

        slop_parsed = {}
        # We iterate through the output so we're not reliant
        # on the order or number of lines in slop's output
        for line in slop_output:
            if '=' in line:
                spl = line.split("=")
                slop_parsed[spl[0]] = spl[1]

        # (left, upper, right, lower)
        try:
            crop_box = (
                int(slop_parsed['X']),
                int(slop_parsed['Y']),
                int(slop_parsed['X']) + int(slop_parsed['W']),
                int(slop_parsed['Y']) + int(slop_parsed['H'])
            )
        except KeyError as exception:
            raise SelectionParseError("Unexpected slop output") from exception

        return crop_box
