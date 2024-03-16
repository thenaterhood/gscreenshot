import typing


class CursorLocator():

    __utilityname__: str = "default"

    def __init__(self):
        """constructor"""
        pass

    def get_cursor_position(self) -> typing.Optional[typing.Tuple[int, int]]:
        raise NotImplementedError()

    @staticmethod
    def can_run() -> bool:
        """
        Whether this cursor locator can run
        """
        return True