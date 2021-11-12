'''
Classes and exceptions related to screen region selection
'''
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

    def get_capabilities(self):
        """
        Get the features this selector supports
        """
        return [
            GSCapabilities.WINDOW_SELECTION,
            GSCapabilities.REGION_SELECTION
        ]

    def region_select(self):
        """
        Select an arbitrary region of the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        raise SelectionError("Not implemented")

    def window_select(self):
        """
        Selects a window from the screen

        Returns:
           (x top left, y top left, x bottom right, y bottom right)
        """
        raise SelectionError("Not implemented")

    def can_run(self):
        """
        Returns whether this is capable of running.
        """
        return False

    def _parse_selection_output(self, region_output):
        '''
        Parses output from a region selection tool in the format
        X=%x,Y=%y,W=%w,H=%h.

        Returns a tuple of the X and Y coordinates of the corners:
        (X top left, Y top left, X bottom right, Y bottom right)
        '''
        region_parsed = {}
        # We iterate through the output so we're not reliant
        # on the order or number of lines in the output
        for line in region_output:
            if '=' in line:
                spl = line.split("=")
                region_parsed[spl[0]] = spl[1]

        # (left, upper, right, lower)
        try:
            crop_box = (
                int(region_parsed['X']),
                int(region_parsed['Y']),
                int(region_parsed['X']) + int(region_parsed['W']),
                int(region_parsed['Y']) + int(region_parsed['H'])
            )
        except KeyError:
            #pylint: disable=raise-missing-from
            raise SelectionParseError("Unexpected output") #from exception

        return crop_box
