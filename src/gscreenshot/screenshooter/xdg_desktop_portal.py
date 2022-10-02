#!/usr/bin/python3

# this used to live at https://gitlab.gnome.org/snippets/814
# but has since been deleted, the original author is unknown
# reuploading here for safe keeping

'''
Wayland integration using xdg-desktop-portal

Based on code from https://gitlab.gnome.org/snippets/814
'''
try:
    import dbus
except ImportError:
    dbus = None

import secrets
import re
import os
import sys
import shutil

from time import sleep
from gi.repository import GLib
from dbus.mainloop.glib import DBusGMainLoop

from gscreenshot.screenshooter import Screenshooter


class XdgPortalScreenshot:
    '''
    Utility class intended to be used when this script
    is called directly.
    '''

    def __init__(self):
        '''constructor'''
        DBusGMainLoop(set_as_default = True)
        self.bus = dbus.SessionBus()
        self.portal = self.bus.get_object(
            'org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop'
        )

    def request(self, parent_window = ''):
        '''Requests a screenshot. Note that xdg-desktop-portal is asynchronous'''
        #pylint: disable=fixme
        # TODO: change to f-strings when dropping python2 support
        #pylint: disable=consider-using-f-string
        request_token = 'gscreenshot_%s' % secrets.token_hex(16)

        options = { 'handle_token': request_token }

        self.bus.add_signal_receiver(
            self.callback,
            'Response',
            'org.freedesktop.portal.Request',
            'org.freedesktop.portal.Desktop',
            self.get_request_handle(request_token)
        )

        self.portal.Screenshot(
            parent_window,
            options,
            dbus_interface='org.freedesktop.portal.Screenshot'
        )

    def get_request_handle(self, token):
        '''get a request handle name'''
        sender_name = re.sub(r'\.', '_', self.bus.get_unique_name()).lstrip(':')
        #pylint: disable=fixme
        # TODO: change to f-strings when dropping python2 support
        #pylint: disable=consider-using-f-string
        return '/org/freedesktop/portal/desktop/request/%s/%s'%(sender_name, token)

    @staticmethod
    def callback(response, result):
        '''callback function when a screenshot is completed'''
        if response == 0:
            uri = result["uri"]
            path = uri.replace("file://", "")
            shutil.move(path, sys.argv[1])
            loop.quit()
        else:
            loop.quit()
            sys.exit(1)


class XdgDesktopPortal(Screenshooter):
    """
    Python wrapper for xdg-desktop-portal screenshots
    """

    __utilityname__ = "xdg-desktop-portal"

    def __init__(self):
        """constructor"""
        Screenshooter.__init__(self)

    def grab_fullscreen(self, delay=0, capture_cursor=False):
        """grabs a full screen screenshot"""

        sleep(delay)
        script_path = os.path.realpath(__file__)
        self._call_screenshooter("python", [script_path, self.tempfile])

    @staticmethod
    def can_run():
        """Whether dbus is available"""
        return dbus is not None

if __name__ == "__main__":
    loop = GLib.MainLoop()
    XdgPortalScreenshot().request()

    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
