'''
Wrapper for the slop screen selector utility
'''
import typing
import subprocess
from gscreenshot.selector import SelectionExecError, SelectionCancelled, RegionSelector
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
        RegionSelector.__init__(self)

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
        """Whether slop is available"""
        return find_executable('slop') is not None

    def _get_boundary_interactive(self) -> typing.Tuple[int, int, int, int]:
        """
        Calls slop and returns the boundary produced by
        slop
        """
        try:
            # nodecorations=0 - this is the slop default, but there's a bug
            # so skipping the "=0" causes a segfault.
            with subprocess.Popen(
                ['slop', '--nodecorations=0', '-f', 'X=%x,Y=%y,W=%w,H=%h'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                ) as slop:

                try:
                    stdout, stderr = slop.communicate(timeout=60)
                except subprocess.TimeoutExpired:
                    slop.kill()
                    #pylint: disable=raise-missing-from
                    raise SelectionExecError("slop selection time out") #from exception

                return_code = slop.returncode

                if return_code != 0:
                    slop_error = stderr.decode("UTF-8")

                    if "cancelled" in slop_error:
                        raise SelectionCancelled("Selection was cancelled")

                    raise SelectionExecError(slop_error)

                slop_output = stdout.decode("UTF-8").strip().split("\n")

                return self._parse_selection_output(slop_output)

        except OSError:
            #pylint: disable=raise-missing-from
            raise SelectionExecError("Slop was not found") #from exception
