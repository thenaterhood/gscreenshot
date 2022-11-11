'''
Wrapper for the slurp screen selector utility
'''
import subprocess
import typing
from gscreenshot.selector import SelectionExecError, SelectionCancelled, RegionSelector
from gscreenshot.util import find_executable, GSCapabilities


class Slurp(RegionSelector):

    """
    Python class wrapper for the slurp region selection tool

    All methods return a tuple of; the x, y coordinates
    of both corners of the selection.
    """

    def __init__(self):
        """
        constructor
        """
        RegionSelector.__init__(self)

    def get_capabilities(self) -> list:
        """
        Get the features this selector supports
        """
        return [
            GSCapabilities.REGION_SELECTION
        ]

    def region_select(self) -> typing.Tuple[int, int, int, int]:
        """
        Select an arbitrary region of the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        return self._get_boundary_interactive()

    def window_select(self) -> typing.Tuple[int, int, int, int]:
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        return self._get_boundary_interactive()

    @staticmethod
    def can_run() -> bool:
        """Whether slurp is available"""
        return find_executable('slurp') is not None

    def _get_boundary_interactive(self) -> typing.Tuple[int, int, int, int]:
        """
        Calls slurp and returns the boundary produced by
        slurp
        """

        try:
            with subprocess.Popen(
                ['slurp', '-f', 'X=%x,Y=%y,W=%w,H=%h'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                ) as slurp:

                try:
                    stdout, stderr = slurp.communicate(timeout=60)
                except subprocess.TimeoutExpired:
                    slurp.kill()
                    #pylint: disable=raise-missing-from
                    raise SelectionExecError("Slurp selection timed out")

                return_code = slurp.returncode

                if return_code != 0:
                    slurp_error = stderr.decode("UTF-8")

                    if "cancelled" in slurp_error:
                        raise SelectionCancelled("Selection was cancelled")

                    raise SelectionExecError(slurp_error)

                slurp_output = stdout.decode("UTF-8").strip().split("\n")

                return self._parse_selection_output(slurp_output)
        except OSError:
            #pylint: disable=raise-missing-from
            raise SelectionExecError("Slurp was not found") #from exception
