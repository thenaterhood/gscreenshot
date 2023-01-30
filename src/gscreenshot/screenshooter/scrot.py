'''
Integration for the Scrot screenshot utility
'''
import subprocess
import typing

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
        params = ['-z', self._tempfile, '-d', str(int(delay))]
        if capture_cursor and Scrot._supports_native_cursor_capture:
            params.append('-p')

        self._call_screenshooter('scrot', params)

    def get_capabilities(self) -> typing.Dict[str, str]:
        '''List of capabilities'''
        capabilities = {
            GSCapabilities.REGION_SELECTION: self.__utilityname__,
            GSCapabilities.WINDOW_SELECTION: self.__utilityname__
        }

        if self._supports_native_cursor_capture:
            capabilities[GSCapabilities.CURSOR_CAPTURE] = self.__utilityname__

        return capabilities

    @staticmethod
    def can_run() -> bool:
        """Whether scrot is available"""
        try:
            scrot_version_output = subprocess.check_output(['scrot', '--version'])
            scrot_version_str = scrot_version_output.decode().strip().rsplit('.', maxsplit=1)[-1]

            if int(scrot_version_str.split('.')[0]) >= 1:
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
        params =  ['-z', self._tempfile, '-d', str(int(delay)), '-s']
        if capture_cursor and Scrot._supports_native_cursor_capture:
            params.append('-p')

        self._call_screenshooter('scrot', params)
