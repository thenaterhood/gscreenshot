'''
Screenshot container classes for gscreenshot
'''
import typing
from PIL import Image


class Screenshot(object):
    '''
    Represents a screenshot taken via Gscreenshot.

    This stores various runtime metadata about the
    individual screenshot whose PIL.Image.Image it contains
    '''

    _image: Image.Image
    _saved_to: typing.Optional[str]

    def __init__(self, image: Image.Image):
        '''Constructor'''
        self._image = image

    def get_image(self) -> Image.Image:
        '''Gets the underlying PIL.Image.Image'''
        return self._image

    def get_thumbnail(self, width: int, height: int,
                      ) -> Image.Image:
        """
        Gets a thumbnail of either the current image, or a passed one
        Params:
            width: int
            height: int
            image: Image|None
        Returns:
            Image
        """
        thumbnail = self._image.copy()

        antialias_algo = None
        try:
            antialias_algo = Image.Resampling.LANCZOS
        except AttributeError: # PIL < 9.0
            antialias_algo = Image.ANTIALIAS

        thumbnail.thumbnail((width, height), antialias_algo)
        return thumbnail

    def set_saved_path(self, path: typing.Optional[str]):
        '''Set the path this screenshot image was saved to'''
        self._saved_to = path

    def get_saved_path(self) -> typing.Optional[str]:
        '''Get the path this screenshot image was saved to'''
        return self._saved_to

    def saved(self) -> bool:
        '''Whether this screenshot image was saved'''
        return self.get_saved_path() is not None

    
class ScreenshotCollection(object):
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

    def append(self, item: Screenshot):
        '''adds a screenshot to the end of the collection'''
        self._screenshots.append(item)

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
        return self._screenshots[self._cursor]

    def cursor_to_start(self):
        '''move the cursor to index 0'''
        self._cursor = 0

    def cursor_to_end(self):
        '''move the cursor to the last (highest) index'''
        self._cursor = len(self._screenshots) - 1
