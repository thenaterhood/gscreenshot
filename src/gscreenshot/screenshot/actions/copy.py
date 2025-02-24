"""copy action"""

import io
import subprocess
from typing import Optional, TYPE_CHECKING
from gscreenshot.screenshot.actions.screenshot_action import (
    ScreenshotActionError,
    ScreenshotAction,
)
from gscreenshot.util import session_is_wayland

if TYPE_CHECKING:
    from gscreenshot.screenshot import Screenshot


class CopyAction(ScreenshotAction[bool]):
    """copy action"""

    verb = "Copy"

    def execute(self, screenshot: Optional["Screenshot"]) -> bool:
        """
        Copies the last screenshot to the clipboard with
        xclip, if available. Most frontends should try to
        use native methods (e.g. Gdk.Clipboard) if possible.

        Returns:
            bool success
        """
        if screenshot is None:
            return False

        image = screenshot.get_image()

        if image is None:
            return False

        params = [
            'xclip',
            '-selection',
            'clipboard',
            '-t',
            'image/png'
            ]
        clipper_name = "xclip"

        if session_is_wayland():
            params = [
                    'wl-copy',
                    '-t',
                    'image/png'
                ]
            clipper_name = "wl-copy"

        with io.BytesIO() as png_data:
            image.save(png_data, "PNG")

            try:
                with subprocess.Popen(
                    params,
                    close_fds=True,
                    stdin=subprocess.PIPE,
                    stdout=None,
                    stderr=None) as xclip:

                    xclip.communicate(input=png_data.getvalue())
                    return True
            except (OSError, subprocess.CalledProcessError) as exc:
                #pylint: disable=raise-missing-from
                raise ScreenshotActionError(
                    f"failed to clip screenshot with clipper = '{clipper_name}': {exc}"
                )
