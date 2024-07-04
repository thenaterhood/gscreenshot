'''
Interface class for integrating cursor locators
'''
import typing

from gscreenshot.scaling import get_scaling_factor


class CursorLocator():
    '''Parent class for cursor locator strategies'''

    __utilityname__: str = "default"

    def __init__(self):
        """constructor"""

    def get_cursor_position(self) -> typing.Optional[typing.Tuple[int, int]]:
        '''Return the cursor position as a tuple of (x, y)'''
        raise NotImplementedError()

    def get_cursor_position_adjusted(self):
        '''Return the cursor position adjusted for scaling'''
        position = self.get_cursor_position()

        if not position:
            return None

        scaling_factor = get_scaling_factor()
        return (
            round(position[0] * scaling_factor),
            round(position[1] * scaling_factor)
        )

    @staticmethod
    def can_run() -> bool:
        """
        Whether this cursor locator can run
        """
        return True
