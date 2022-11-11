'''
Classes and exceptions related to screen region selection
'''
import subprocess
import typing
from gscreenshot.util import GSCapabilities


class SelectionError(BaseException):
    '''Generic selection error'''

class SelectionExecError(BaseException):
    '''Error executing selector'''

class SelectionParseError(BaseException):
    '''Error parsing selection output'''

class SelectionCancelled(BaseException):
    '''Selection cancelled error'''

class NoSupportedSelectorError(BaseException):
    '''No region selection tool available'''

class RegionSelector():
    '''Region selection interface'''

    def __init__(self):
        """
        constructor
        """

    def get_capabilities(self) -> typing.List[str]:
        """
        Get the features this selector supports
        """
        return [
            GSCapabilities.WINDOW_SELECTION,
            GSCapabilities.REGION_SELECTION
        ]

    def region_select(self) -> typing.Tuple[int, int, int, int]:
        """
        Select an arbitrary region of the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        raise SelectionError("Not implemented")

    def window_select(self) -> typing.Tuple[int, int, int, int]:
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        raise SelectionError("Not implemented")

    @staticmethod
    def can_run() -> bool:
        """
        Returns whether this is capable of running.
        """
        return False

    def _get_boundary_interactive(self, params: typing.List[str]
                                ) -> typing.Tuple[int, int, int, int]:
        """
        Runs the selector and returns the parsed output. This accepts a list
        that will be passed directly to subprocess.Popen and expects the
        utility to be capable of returning a string parseable by _parse_selection_output.
        """
        try:
            with subprocess.Popen(
                params,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
                ) as selector_process:

                try:
                    stdout, stderr = selector_process.communicate(timeout=60)
                except subprocess.TimeoutExpired:
                    selector_process.kill()
                    #pylint: disable=raise-missing-from
                    raise SelectionExecError(f"{params[0]} selection timed out")

                return_code = selector_process.returncode

                if return_code != 0:
                    selector_error = stderr.decode("UTF-8")

                    if "cancelled" in selector_error:
                        raise SelectionCancelled("Selection was cancelled")

                    raise SelectionExecError(selector_error)

                selector_output = stdout.decode("UTF-8").strip().split("\n")

                return self._parse_selection_output(selector_output)
        except OSError:
            #pylint: disable=raise-missing-from
            raise SelectionExecError(f"{params[0]} was not found") #from exception

    def _parse_selection_output(self, region_output: typing.List[str]
                                ) -> typing.Tuple[int, int, int, int]:
        '''
        Parses output from a region selection tool in the format
        X=%x,Y=%y,W=%w,H=%h OR X=%x\nY=%x\nW=%w\nH=%h.

        Returns a tuple of the X and Y coordinates of the corners:
        (X top left, Y top left, X bottom right, Y bottom right)
        '''
        region_parsed = {}
        # We iterate through the output so we're not reliant
        # on the order or number of lines in the output
        for line in region_output:
            for comma_split in line.split(","):
                if '=' in comma_split:
                    spl = comma_split.split("=")
                    region_parsed[spl[0]] = int(spl[1])

        # (left, upper, right, lower)
        try:
            crop_box = (
                region_parsed['X'],
                region_parsed['Y'],
                region_parsed['X'] + region_parsed['W'],
                region_parsed['Y'] + region_parsed['H']
            )
        except KeyError:
            #pylint: disable=raise-missing-from
            raise SelectionParseError("Unexpected output") #from exception

        return crop_box

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}()'
