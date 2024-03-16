'''
Wrapper for the slurp screen selector utility
'''
from time import sleep
import typing
from gscreenshot.selector import RegionSelector
from gscreenshot.util import find_executable, GSCapabilities


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

    def get_capabilities(self) -> typing.Dict[str, str]:
        """
        Get the features this selector supports
        """
        return {
            GSCapabilities.REGION_SELECTION: self.__utilityname__,
            GSCapabilities.REUSE_REGION: self.__utilityname__
        }

    def region_select(self) -> typing.Tuple[int, int, int, int]:
        """
        Select an arbitrary region of the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        ret = self._get_boundary_interactive([
            'slurp', '-f', 'X=%x,Y=%y,W=%w,H=%h',
            '-b', '#00000011', '-s', '#00000011', '-c', '#808080FF'])
        # Sleep so we hopefully don't catch the edge of slurp closing
        sleep(0.1)
        return ret

    def window_select(self) -> typing.Tuple[int, int, int, int]:
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        ret = self._get_boundary_interactive([
            'slurp', '-f', 'X=%x,Y=%y,W=%w,H=%h',
            '-b', '#00000011', '-s', '#00000011', '-c', '#808080FF'])
        # Sleep so we hopefully don't catch the edge of slurp closing
        sleep(0.1)
        return ret

    @staticmethod
    def can_run() -> bool:
        """Whether slurp is available"""
        return find_executable('slurp') is not None
