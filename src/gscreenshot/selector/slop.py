'''
Wrapper for the slop screen selector utility
'''
import typing
from gscreenshot.util import find_executable
from .region_selector import RegionSelector


class Slop(RegionSelector):

    """
    Python class wrapper for the slop region selection tool

    All methods return a tuple of; the x, y coordinates
    of both corners of the selection.
    """

    __utilityname__: str = "slop"

    def __init__(self):
        """
        constructor
        """
        RegionSelector.__init__(self)

    def region_select(self):
        """
        Select an arbitrary region of the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        return self._get_boundary_interactive([
                'slop',
                '--nodecorations=0',
                '-l',
                '-c',
                '0.8,0.8,0.8,0.6',
                '-f',
                'X=%x,Y=%y,W=%w,H=%h'
            ])

    def window_select(self):
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        return self._get_boundary_interactive([
                'slop',
                '--nodecorations=0',
                '-l',
                '-c',
                '0.8,0.8,0.8,0.6',
                '-f',
                'X=%x,Y=%y,W=%w,H=%h'
            ])

    @staticmethod
    def can_run() -> bool:
        """Whether slop is available"""
        return find_executable('slop') is not None
