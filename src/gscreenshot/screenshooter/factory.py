'''
Utilities for selecting a screenshot utility
'''
from gscreenshot.screenshooter.scrot import Scrot
from gscreenshot.screenshooter.imlib_2 import Imlib2
from gscreenshot.screenshooter.imagemagick import ImageMagick
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError

class ScreenshooterFactory(object):
    '''Selects and instantiates a usable screenshot class'''

    def __init__(self, screenshooter=None):
        self.screenshooter = screenshooter
        self.screenshooters = [
                Scrot,
                ImageMagick,
                Imlib2
                ]

    def create(self):
        '''Returns a screenshooter instance'''
        if self.screenshooter is not None:
            return self.screenshooter

        for shooter in self.screenshooters:
            if shooter.can_run():
                return shooter()

        raise NoSupportedScreenshooterError(
                "No supported screenshot backend available"
                )
