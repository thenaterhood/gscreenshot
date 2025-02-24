"""open action"""
import logging
import subprocess
from typing import Optional, TYPE_CHECKING

from .screenshot_action import ScreenshotActionError, ScreenshotAction
from .save_tmpfile import SaveTmpfileAction


if TYPE_CHECKING:
    from gscreenshot.screenshot import Screenshot

log = logging.getLogger(name=__name__)


class XdgOpenAction(ScreenshotAction[bool]):
    """open action"""

    verb = "Open"

    def execute(self, screenshot: Optional["Screenshot"]) -> bool:
        """
        Calls xdg to open the screenshot in its default application

        Returns:
            bool success
        """
        if screenshot is None:
            return False

        filename = screenshot.get_saved_path()
        if filename is None:
            action = SaveTmpfileAction()
            filename = action.execute(screenshot)

        if filename is None:
            return False

        try:
            subprocess.run(['xdg-open', filename], check=True)
            return True
        except (subprocess.CalledProcessError, IOError, OSError) as exc:
            log.warning("failed to open screenshot with xdg-open: %s", exc)
            raise ScreenshotActionError(
                "failed to open screenshot with xdg-open"
            ) from exc
