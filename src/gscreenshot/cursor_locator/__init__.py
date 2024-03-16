'''
Interface class for integrating cursor locators
'''
import typing


class CursorLocator():
    '''Parent class for cursor locator strategies'''

    __utilityname__: str = "default"

    def __init__(self):
        """constructor"""

    def get_cursor_position(self) -> typing.Optional[typing.Tuple[int, int]]:
        raise NotImplementedError()

    @staticmethod
    def can_run() -> bool:
        """
        Whether this cursor locator can run
        """
        return True
