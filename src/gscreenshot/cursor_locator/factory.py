'''
Utilities for selecting a cursor locator utility
'''

import typing
from gscreenshot.util import session_is_wayland
from .cursor_locator import CursorLocator
from .gtk_cursor_locator import GtkCursorLocator
from .x11_cursor_locator import X11CursorLocator


class NoSupportedCursorLocatorError(Exception):
    """NoSupportedCursorLocatorError"""


def get_cursor_locator(cursor_locator: typing.Optional[CursorLocator] = None):
    """Gets a workable cursor locator"""
    return CursorLocatorFactory(cursor_locator).create()


class CursorLocatorFactory(object):
    '''Selects and instantiates a usable cursor finder'''

    def __init__(self, cursor_locator=None):
        self.cursor_locator:typing.Optional[CursorLocator] = cursor_locator
        self.xorg_locators = [
                X11CursorLocator,
                GtkCursorLocator
                ]

        self.wayland_locators = [
                GtkCursorLocator
                ]

        self.locators:list = []

        if session_is_wayland():
            self.locators = self.wayland_locators
        else:
            self.locators = self.xorg_locators

    def create(self) -> CursorLocator:
        '''Returns a locator instance'''
        if self.cursor_locator is not None:
            return self.cursor_locator

        for locator in self.locators:
            if locator.can_run():
                return locator()

        raise NoSupportedCursorLocatorError(
                "No supported cursor locator available",
                [x.__utilityname__ for x in self.locators if x.__utilityname__ is not None]
                )
