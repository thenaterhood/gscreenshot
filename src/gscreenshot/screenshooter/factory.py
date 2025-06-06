'''
Utilities for selecting a screenshot utility
'''
import logging
import typing
from gscreenshot.util import session_is_wayland
from .grim import Grim
from .imagemagick import ImageMagick
from .imlib_2 import Imlib2
from .pil import PILWrapper
from .scrot import Scrot
from .xdg_desktop_portal import XdgDesktopPortal
from .exceptions import NoSupportedScreenshooterError
from .screenshooter import Screenshooter


log = logging.getLogger(__name__)


def get_screenshooter(screenshooter: typing.Optional[Screenshooter] = None):
    """Gets a workable screenshooter"""
    return ScreenshooterFactory(screenshooter).create()


class ScreenshooterFactory():
    '''Selects and instantiates a usable screenshot class'''

    def __init__(self, screenshooter:typing.Optional[Screenshooter]=None):
        self.screenshooter:typing.Optional[Screenshooter] = screenshooter
        self.xorg_screenshooters = [
                Scrot,
                ImageMagick,
                PILWrapper,
                Imlib2,
                XdgDesktopPortal
                ]

        self.wayland_screenshooters = [
                Grim,
                XdgDesktopPortal,
                ]

        self.screenshooters:list = []

        if session_is_wayland():
            self.screenshooters = self.wayland_screenshooters
        else:
            self.screenshooters = self.xorg_screenshooters

    def create(self) -> Screenshooter:
        '''Returns a screenshooter instance'''
        if self.screenshooter is not None:
            log.debug("using predefined screenshotter '%s'", self.screenshooter.__utilityname__)
            return self.screenshooter

        for shooter in self.screenshooters:
            if shooter.can_run():
                log.debug("using autodetected screenshooter '%s", {shooter.__utilityname__})
                return shooter()

        log.info("no supported screenshotter available")
        raise NoSupportedScreenshooterError(
                "No supported screenshot backend available",
                [x.__utilityname__ for x in self.screenshooters if x.__utilityname__ is not None]
                )
