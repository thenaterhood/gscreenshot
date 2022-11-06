'''
Selector factory module
'''

from gscreenshot.selector.slop import Slop
from gscreenshot.selector.slurp import Slurp
from gscreenshot.selector import NoSupportedSelectorError
from gscreenshot.selector import RegionSelector
from gscreenshot.util import session_is_wayland


class SelectorFactory(object):
    '''Selects and instantiates a usable selector class'''

    def __init__(self, screenselector=None):
        self.screenselector = screenselector
        self.xorg_selectors = [
                Slop
                ]

        self.wayland_selectors = [
                Slurp
                ]

        if session_is_wayland():
            self.selectors = self.wayland_selectors
        else:
            self.selectors = self.xorg_selectors

    def create(self) -> RegionSelector:
        '''Returns a screenselector instance'''
        if self.screenselector is not None:
            return self.screenselector

        for selector in self.selectors:
            if selector.can_run():
                return selector()

        raise NoSupportedSelectorError(
                "No supported selector backend available"
                )
