'''
Screenshot container classes for gscreenshot
'''
import typing

from gscreenshot.meta import get_app_icon
from .screenshot import Screenshot


class ScreenshotCollection():
    '''
    The collection of screenshots taken by gscreenshot
    during the active session
    '''

    _screenshots: typing.List[Screenshot]
    _cursor: int

    def __init__(self):
        '''constructor'''
        self._screenshots = []
        self._cursor = 0

    def __len__(self) -> int:
        '''length'''
        return len(self._screenshots)

    def __getitem__(self, idx) -> Screenshot:
        '''get the screenshot with the given index'''
        return self._screenshots[idx]

    def __iter__(self):
        yield from self._screenshots

    def cursor(self) -> int:
        '''get the current cursor index'''
        return self._cursor

    def append(self, item: Screenshot):
        '''adds a screenshot to the end of the collection'''
        self._screenshots.append(item)

    def remove(self, item: Screenshot):
        '''removes a screenshot'''
        self._screenshots.remove(item)
        if not self.has_next():
            self.cursor_to_end()
        elif not self.has_previous():
            self.cursor_to_start()

    def replace(self, replacement: Screenshot, idx: int = -2):
        '''replaces a screenshot at the cursor or provided index'''
        if idx == -2:
            idx = self._cursor

        if len(self._screenshots) == 0:
            self.append(replacement)
            return

        try:
            self._screenshots[idx] = replacement
        except IndexError:
            self._screenshots[self._cursor] = replacement

    def insert(self, screenshot: Screenshot):
        '''
        Inserts a screenshot at the cursor
        '''
        if len(self._screenshots) < 1:
            self.append(screenshot)
            return

        try:
            self._screenshots = self._screenshots[:self._cursor + 1] + \
                [screenshot] + self._screenshots[self._cursor + 1:]

            self._cursor = self._cursor + 1

        except IndexError:
            self.append(screenshot)
            self.cursor_to_end()

    def has_next(self) -> bool:
        '''
        whether the collection has another screenshot
        at the index+1 of the current cursor position
        '''
        return (self._cursor + 1) < len(self._screenshots)

    def has_previous(self) -> bool:
        '''
        whether the collection has another screenshot at
        the index-1 of the current cursor position
        '''
        return (self._cursor - 1) > -1

    def cursor_next(self) -> typing.Optional[Screenshot]:
        '''
        get the next screenshot and increment the cursor
        '''
        if self.has_next():
            self._cursor += 1
            return self[self._cursor]

        return None

    def cursor_prev(self) -> typing.Optional[Screenshot]:
        '''
        get the previous screenshot and decrement the cursor
        '''
        if self.has_previous():
            self._cursor -= 1
            return self[self._cursor]

        return None

    def cursor_current(self) -> typing.Optional[Screenshot]:
        '''
        get the screenshot at the current cursor index
        '''
        try:
            return self._screenshots[self._cursor]
        except IndexError:
            return None

    def cursor_current_fallback(self) -> Screenshot:
        """
        Get the screenshot at the current cursor index
        or the application icon if no screenshot is available
        """
        screenshot = self.cursor_current()
        if not screenshot:
            return Screenshot(get_app_icon())

        return screenshot

    def cursor_to_start(self):
        '''move the cursor to index 0'''
        self._cursor = 0

    def cursor_to_end(self):
        '''move the cursor to the last (highest) index'''
        self._cursor = len(self._screenshots) - 1

    def has_unsaved(self):
        '''returns True if there are unsaved screenshots'''
        return not all(s.saved() for s in self._screenshots)
