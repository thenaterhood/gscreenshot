'''
Screenshot container classes for gscreenshot
'''
import os
import typing
from PIL import Image

from .effects import ScreenshotEffect


class Screenshot():
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
            antialias_algo = Image.ANTIALIAS # type: ignore

        if thumbnail.height/height < .1 and thumbnail.width/width < .1:
            thumbnail = thumbnail.resize((thumbnail.width*10, thumbnail.height*10))

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
