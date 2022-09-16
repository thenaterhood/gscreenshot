'''
Utilities for selecting a screenshot utility
'''

from gscreenshot.screenshooter.grim import Grim
from gscreenshot.screenshooter.imagemagick import ImageMagick
from gscreenshot.screenshooter.imlib_2 import Imlib2
from gscreenshot.screenshooter.pil import PILWrapper
from gscreenshot.screenshooter.scrot import Scrot
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError
from gscreenshot.util import session_is_wayland

class ScreenshooterFactory(object):
    '''Selects and instantiates a usable screenshot class'''

    def __init__(self, screenshooter=None):
        self.screenshooter = screenshooter
        self.xorg_screenshooters = [
                Scrot,
                ImageMagick,
                #PILWrapper,
                #Imlib2
                ]

        self.wayland_screenshooters = [
                Grim
                ]

        if session_is_wayland():
            self.screenshooters = self.wayland_screenshooters
        else:
            self.screenshooters = self.xorg_screenshooters

    def create(self):
        '''Returns a screenshooter instance'''
        if self.screenshooter is not None:
            return self.screenshooter

        for shooter in self.screenshooters:
            if shooter.can_run():
                return shooter()

        raise NoSupportedScreenshooterError(
                "No supported screenshot backend available",
                [x.__utilityname__ for x in self.screenshooters if x.__utilityname__ is not None]
                )
