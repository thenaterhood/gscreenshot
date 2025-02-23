'''
Selector factory module
'''

import logging
import typing
from gscreenshot.util import session_is_wayland
from .gscreenshot_x_select import GscreenshotXSelect
from .exceptions import NoSupportedSelectorError
from .region_selector import RegionSelector
from .slop import Slop
from .slurp import Slurp

log = logging.getLogger(__name__)


def get_region_selector(screenselector: typing.Optional[RegionSelector] = None):
    """Gets a workable region selector"""
    return SelectorFactory(screenselector).create()


class SelectorFactory():
    '''Selects and instantiates a usable selector class'''

    def __init__(self, screenselector:typing.Optional[RegionSelector]=None):
        self.screenselector:typing.Optional[RegionSelector] = screenselector
        self.xorg_selectors = [
                Slop,
                GscreenshotXSelect,
                ]

        self.wayland_selectors = [
                Slurp,
                ]

        self.selectors:list = []

        if session_is_wayland():
            self.selectors = self.wayland_selectors
        else:
            self.selectors = self.xorg_selectors

    def create(self) -> RegionSelector:
        '''Returns a screenselector instance'''
        if self.screenselector is not None:
            log.debug("using predefined selector '%s'", self.screenselector.__utilityname__)
            return self.screenselector

        for selector in self.selectors:
            if selector.can_run():
                log.debug("using autodetected selector '%s'", selector.__utilityname__)
                return selector()

        raise NoSupportedSelectorError(
                "No supported selector backend available"
                )
