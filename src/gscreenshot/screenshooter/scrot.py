'''
Integration for the Scrot screenshot utility
'''
import subprocess

from gscreenshot.screenshooter import Screenshooter
from gscreenshot.util import GSCapabilities


class Scrot(Screenshooter):
    """
    Python class wrapper for the scrot screenshooter utility
    """

    _supports_native_cursor_capture = False
    __utilityname__ = "scrot"

    def __init__(self):
        """
        constructor
        """
        Screenshooter.__init__(self)

    def grab_fullscreen(self, delay=0, capture_cursor=False):
        """
        Takes a screenshot of the full screen with a given delay

        Parameters:
            int delay, in seconds
        """
        params = ['-z', self.tempfile, '-d', str(delay)]
        if capture_cursor and Scrot._supports_native_cursor_capture:
            params.append('-p')

        self._call_screenshooter('scrot', params)
        if capture_cursor and not Scrot._supports_native_cursor_capture:
            self.add_fake_cursor()

    def get_capabilities(self):
        '''List of capabilities'''
        capabilities = [
            GSCapabilities.REGION_SELECTION,
            GSCapabilities.WINDOW_SELECTION
        ]

        if self._supports_native_cursor_capture:
            capabilities.append(GSCapabilities.CURSOR_CAPTURE)

        return capabilities

    @staticmethod
    def can_run():
        """Whether scrot is available"""
        try:
            scrot_version_output = subprocess.check_output(['scrot', '--version'])
            scrot_version_num = scrot_version_output.decode().strip().rsplit(' ', maxsplit=1)[-1]

            if float(scrot_version_num) >= 1:
                Scrot._supports_native_cursor_capture = True
            else:
                Scrot._supports_native_cursor_capture = False

            return True
        except (subprocess.CalledProcessError, IOError, OSError):
            return False

    def _grab_selection_fallback(self, delay=0, capture_cursor=False):
        """
        Fallback for selection which uses scrot's builtin
        region selection
        """
        params =  ['-z', self.tempfile, '-d', str(delay), '-s']
        if capture_cursor and Scrot._supports_native_cursor_capture:
            params.append('-p')

        self._call_screenshooter('scrot', params)
        if capture_cursor and not Scrot._supports_native_cursor_capture:
            self.add_fake_cursor()
