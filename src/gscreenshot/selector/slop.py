'''
Wrapper for the slop screen selector utility
'''
import subprocess
from gscreenshot.selector import SelectionParseError, SelectionExecError, SelectionCancelled, RegionSelector
from gscreenshot.util import find_executable


class Slop(RegionSelector):

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

    @staticmethod
    def can_run():
        """Whether slop is available"""
        return find_executable('slop') is not None

    def _get_boundary_interactive(self):
        """
        Calls slop and returns the boundary produced by
        slop
        """
        try:
            # nodecorations=0 - this is the slop default, but there's a bug
            # so skipping the "=0" causes a segfault.
            #pylint: disable=fixme
            # TODO: when dropping python2 support, switch to using with here
            #pylint: disable=consider-using-with
            process = subprocess.Popen(
                ['slop', '--nodecorations=0', '-f', 'X=%x,Y=%y,W=%w,H=%h'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                )
            stdout, stderr = process.communicate()
            return_code = process.returncode
        except OSError:
            #pylint: disable=raise-missing-from
            raise SelectionExecError("Slop was not found") #from exception

        if return_code != 0:
            slop_error = stderr.decode("UTF-8")

            if "cancelled" in slop_error:
                raise SelectionCancelled("Selection was cancelled")

            raise SelectionExecError(slop_error)

        slop_output = stdout.decode("UTF-8").strip().split(",")

        return self._parse_selection_output(slop_output)

