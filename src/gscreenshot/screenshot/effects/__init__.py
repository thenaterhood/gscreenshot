'''
Provides a common API class for adding basic
editing to screenshots.
This is not intended for full image editing
support - just basics like crop and adding
simple overlays. Gscreenshot is not, and never
should be, GIMP or Krita.
'''
import typing
from PIL import Image


class ScreenshotEffect():
    '''
    A simple manipulation for a screenshot
    '''
    _enabled: bool = True
    _alias: typing.Optional[str] = None
    _meta: dict = {}

    def set_alias(self, alias: typing.Optional[str]):
        '''
        Add or change a name to this effect for identification
        to the user.
        '''
        self._alias = alias

    def enable(self):
        '''
        Set this effect to enabled (it will be applied to
        the screenshot)
        '''
        self._enabled = True

    def disable(self):
        '''
        Set this effect to disabled (it will NOT be applied
        to the screenshot)
        '''
        self._enabled = False

    def apply_to(self, screenshot: Image.Image) -> Image.Image:
        '''
        Applies this effect to a provided image
        '''
        return screenshot

    @property
    def enabled(self) -> bool:
        '''Returns whether this effect is enabled'''
        return self._enabled

    @property
    def alias(self) -> typing.Optional[str]:
        '''Returns the alias of this effect'''
        return self._alias

    @property
    def meta(self) -> typing.Dict[str, str]:
        '''Returns the metadata (if any)'''
        return self._meta
