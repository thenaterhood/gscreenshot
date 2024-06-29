#!/usr/bin/python3
'''
Wayland integration using xdg-desktop-portal

Based on code from https://gitlab.gnome.org/snippets/814

This script is structured as two parts - an importable
module for gscreenshot and an executable script that takes
a screenshot with xdg-desktop-portal. The module runs the
script as a subprocess due to issues with the DBus loop and
async call.
'''
try:
    import dbus
except ImportError:
    dbus = None

import binascii
import re
import os
import sys
import shutil
import subprocess

from random import SystemRandom
from time import sleep
from gi.repository import GLib

try:
    from dbus.mainloop.glib import DBusGMainLoop
except ImportError:
    DBusGMainLoop = None

# This MUST be an absolute import path or we either get a circular import
# or the script doesn't work
from gscreenshot.screenshooter.screenshooter import Screenshooter
from gscreenshot.screenshooter.exceptions import NoSupportedScreenshooterError


class XdgPortalScreenshot:
    '''
    Utility class intended to be used when this script
    is called directly.
    '''

    def __init__(self):
        '''constructor'''
        if DBusGMainLoop is None or dbus is None:
            raise NoSupportedScreenshooterError('python-dbus is unavailable')

        DBusGMainLoop(set_as_default = True)
        self.bus = dbus.SessionBus()
        self.portal = self.bus.get_object(
            'org.freedesktop.portal.Desktop', '/org/freedesktop/portal/desktop'
        )

    def request(self, parent_window = ''):
        '''Requests a screenshot. Note that xdg-desktop-portal is asynchronous'''

        # The following three lines perform the same
        # logic as secrets.token_hex without requiring
        # python-secrets
        sysrand = SystemRandom()

        try:
            # Python 3
            token_bytes = sysrand.randbytes(16)
        except AttributeError:
            # Python 2
            # This is not cryptographically secure, but
            # is "good enough" for this purpose
            token_bytes = os.urandom(16)

        token_hex = binascii.hexlify(token_bytes).decode('ascii')

        request_token = f"gscreenshot_{token_hex}"

        options = { 'handle_token': request_token, 'interactive': False }

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

    def get_request_handle(self, token) -> str:
        '''get a request handle name'''
        sender_name = re.sub(r'\.', '_', self.bus.get_unique_name()).lstrip(':')
        return f"/org/freedesktop/portal/desktop/request/{sender_name}/{token}"

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
        py_call = "python3"
        if sys.version_info.major < 3:
            py_call = "python2"

        self._call_screenshooter(py_call, [script_path, self._tempfile])

    @staticmethod
    def can_run() -> bool:
        """Whether dbus is available"""
        if dbus is None:
            return False

        try:
            subprocess.check_output(["pidof", "xdg-desktop-portal"])
        except (subprocess.CalledProcessError, OSError):
            return False

        return True


if __name__ == "__main__":
    loop = GLib.MainLoop()
    XdgPortalScreenshot().request()

    try:
        loop.run()
    except KeyboardInterrupt:
        loop.quit()
