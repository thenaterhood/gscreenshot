"""save action"""
import os
import tempfile
from typing import Optional, TYPE_CHECKING
from gscreenshot.screenshot.actions import SaveAction
from gscreenshot.filename import get_time_filename

from .screenshot_action import ScreenshotAction

if TYPE_CHECKING:
    from gscreenshot.screenshot import Screenshot


class SaveTmpfileAction(ScreenshotAction[str | None]):
    """save action"""

    def execute(self, screenshot: Optional["Screenshot"]) -> Optional[str]:
        '''
        method for saving an image to a file
        '''
        if not screenshot:
            return None

        filename = os.path.join(
                tempfile.gettempdir(),
                get_time_filename(screenshot)
            )

        save_action = SaveAction(filename=filename)
        return save_action.execute(screenshot)
