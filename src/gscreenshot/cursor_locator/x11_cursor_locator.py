"""
Xlib cursor locator classes
"""
import typing
try:
    from Xlib import display
except ImportError:
    display = None

from .cursor_locator import CursorLocator


class X11CursorLocator(CursorLocator):
    '''Xlib-based cursor locator'''

    __utilityname__: str = "python-xlib"

    def get_cursor_position(self) -> typing.Optional[typing.Tuple[int, int]]:
        """
        Gets the current position of the mouse cursor, if able.
        Returns (x, y) or None.
        """
        if display is None:
            return None

        try:
            # This is a ctype
            # pylint: disable=protected-access
            mouse_data = display.Display().screen().root.query_pointer()._data
            if 'root_x' not in mouse_data or 'root_y' not in mouse_data:
                return None
        # pylint: disable=bare-except
        except:
            # We don't really care about the specific error here. If we can't
            # get the pointer, then just move on.
            return None

        return (mouse_data["root_x"], mouse_data["root_y"])

    @staticmethod
    def can_run() -> bool:
        '''can_run'''
        return display is not None
