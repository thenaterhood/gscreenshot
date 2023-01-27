'''
Crop effect
'''

from PIL import Image
from gscreenshot.screenshot.effects import ScreenshotEffect


class CropEffect(ScreenshotEffect):
    '''
    Applies a crop to the screenshot
    '''

    def __init__(self, region=None):
        '''constructor'''
        super().__init__()
        self._meta["region"] = region

    def apply_to(self, screenshot: Image.Image) -> Image.Image:
        '''apply the effect'''
        return screenshot.crop(self._meta["region"])

    def __repr__(self):
        return f"CropEffect({self._meta['region']})"
