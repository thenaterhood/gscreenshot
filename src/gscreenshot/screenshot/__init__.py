'''
Screenshot container classes for gscreenshot
'''
import os
import typing
from PIL import Image, ImageFilter
from gscreenshot.screenshot.effects import ScreenshotEffect


class Screenshot(object):
    '''
    Represents a screenshot taken via Gscreenshot.

    This stores various runtime metadata about the
    individual screenshot whose PIL.Image.Image it contains
    '''

    _image: Image.Image
    _saved_to: typing.Optional[str]
    _effects: typing.List[ScreenshotEffect]

    def __init__(self, image: Image.Image):
        '''Constructor'''
        self._image = image
        self._saved_to = None
        self._effects = []

    def add_effect(self, effect: ScreenshotEffect):
        '''
        Add another overlay effect to this screenshot
        '''
        self._effects.append(effect)

    def remove_effect(self, effect: ScreenshotEffect):
        '''
        Remove an overlay effect from this screenshot.
        Note that effects can also be disabled without
        being removed.
        '''
        self._effects.remove(effect)

    def get_effects(self) -> typing.List[ScreenshotEffect]:
        '''
        Provides the list of effects
        '''
        return self._effects

    def get_image(self) -> Image.Image:
        '''Gets the underlying PIL.Image.Image'''
        image = self._image.copy()

        for effect in self._effects:
            if effect.enabled:
                image = effect.apply_to(image)

        return image.convert("RGB")

    def get_preview(self, width: int, height: int, with_border=False) -> Image.Image:
        '''
        Gets a preview of the image.

        Params:
            width: int
            height: int
            with_border: bool, whether to add a drop shadow for visibility
        Returns:
            Image
        '''
        thumbnail = self.get_image().copy()

        antialias_algo = None
        try:
            antialias_algo = Image.Resampling.LANCZOS
        except AttributeError: # PIL < 9.0
            antialias_algo = Image.ANTIALIAS

        thumbnail.thumbnail((width, height), antialias_algo)

        if with_border:
            shadow = Image.new(
                'RGBA',
                (int(thumbnail.size[0]+4), int(thumbnail.size[1]+4)),
                (70, 70, 70, 50)
            )
            shadow.paste(thumbnail, (1, 1))
            return shadow

        return thumbnail

    def set_saved_path(self, path: typing.Optional[str]):
        '''Set the path this screenshot image was saved to'''
        self._saved_to = path

    def get_saved_path(self) -> typing.Optional[str]:
        '''Get the path this screenshot image was saved to'''
        return self._saved_to

    def saved(self) -> bool:
        '''Whether this screenshot image was saved'''
        saved_path = self.get_saved_path()

        if saved_path is None:
            return False

        return os.path.exists(saved_path)

    def __repr__(self) -> str:
        return f'''{self.__class__.__name__}(image={self._image})
        '''


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

    def cursor_to_start(self):
        '''move the cursor to index 0'''
        self._cursor = 0

    def cursor_to_end(self):
        '''move the cursor to the last (highest) index'''
        self._cursor = len(self._screenshots) - 1
