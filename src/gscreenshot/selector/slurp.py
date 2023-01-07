'''
Wrapper for the slurp screen selector utility
'''
import typing
from gscreenshot.selector import RegionSelector
from gscreenshot.util import find_executable


class Slurp(RegionSelector):

    """
    Python class wrapper for the slurp region selection tool

    All methods return a tuple of; the x, y coordinates
    of both corners of the selection.
    """

    __utilityname__: str = "slurp"

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
        return self._get_boundary_interactive(['slurp', '-f', 'X=%x,Y=%y,W=%w,H=%h'])

    def window_select(self) -> typing.Tuple[int, int, int, int]:
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        return self._get_boundary_interactive(['slurp', '-f', 'X=%x,Y=%y,W=%w,H=%h'])

    @staticmethod
    def can_run() -> bool:
        """Whether slurp is available"""
        return find_executable('slurp') is not None
