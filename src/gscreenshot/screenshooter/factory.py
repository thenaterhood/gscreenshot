'''
Utilities for selecting a screenshot utility
'''
from gscreenshot.screenshooter.scrot import Scrot
from gscreenshot.screenshooter.imlib_2 import Imlib2
from gscreenshot.screenshooter.imagemagick import ImageMagick
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError

class ScreenshooterFactory(object):

    def __init__(self, screenshooter=None):
        self.screenshooter = screenshooter
        self.screenshooters = {
                'scrot': Scrot,
                'imagemagick': ImageMagick,
                'imlib2': Imlib2
                }

    def create(self):
        if (self.screenshooter is not None):
            return self.screenshooter

        for shooter in self.screenshooters.values():
            if shooter.can_run():
                return shooter()

        raise NoSupportedScreenshooterError(
                "No supported screenshot backend available"
                )

    def get_screenshooters(self):
        return self.screenshooters.values()

    def get_screenshooter_names(self):
        return self.screenshooters.keys()

    def select_screenshooter(self, screenshooter=None):
        if screenshooter is None:
            # This will force a redetect next time we're called
            self.screenshooter = None
            return True

        if screenshooter in self.get_screenshooter_names():
            self.screenshooter = self.screenshooters[screenshooter]()
            return True

        return False
