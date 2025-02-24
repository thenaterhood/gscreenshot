"""save action"""
from dataclasses import dataclass
from datetime import datetime
import logging
import os
from typing import Optional, TYPE_CHECKING
from gscreenshot.filename import get_time_filename, interpolate_filename
from gscreenshot.util import get_supported_formats
from gscreenshot.screenshot.actions.screenshot_action import (
    ScreenshotActionError,
    ScreenshotActionInvalid,
    ScreenshotAction,
)

if TYPE_CHECKING:
    from gscreenshot.screenshot import Screenshot

log = logging.getLogger(name=__name__)


@dataclass
class SaveActionParams():

    overwrite: bool = True

    filename: Optional[str] = None


class SaveAction(ScreenshotAction[str | None]):
    """save action"""

    verb = "Save"

    param_class = SaveActionParams

    # generated using piexif
    EXIF_TEMPLATE = b'Exif\x00\x00MM\x00*\x00\x00\x00\x08\x00\x02\x011\x00\x02\x00\x00\x00\x15\x00\x00\x00&\x87i\x00\x04\x00\x00\x00\x01\x00\x00\x00;\x00\x00\x00\x00gscreenshot [[VERSION]]\x00\x00\x01\x90\x03\x00\x02\x00\x00\x00\x14\x00\x00\x00I[[CREATE_DATE]]\x00' #pylint: disable=line-too-long

    #pylint:disable=too-many-branches
    def execute(self, screenshot: Optional["Screenshot"]) -> Optional[str]:
        '''
        method for saving an image to a file
        '''
        if not self.params:
            raise ScreenshotActionInvalid

        if screenshot is None:
            return None

        filename = self.params.filename

        if filename is None:
            filename = get_time_filename(screenshot=screenshot)
        else:
            filename = interpolate_filename(filename, screenshot)

        file_type = "png"

        if "/dev" not in filename or filename.index("/dev") != 0:

            file_extension = os.path.splitext(filename)[1][1:].lower()

            if file_extension == "":
                # If we don't have any file extension, assume
                # we were given a directory; create the tree
                # if it doesn't exist, then store the screenshot
                # there with a time-based filename.
                try:
                    os.makedirs(filename)
                    log.debug("created directory tree for '%s'", filename)
                except (IOError, OSError) as exc:
                    # Likely the directory already exists, so
                    # we'll throw the exception away.
                    # If we fail to save, we'll return a status
                    # saying so, so we'll be okay.
                    log.debug(
                        "failed to create tree for '%s': %s", filename, exc
                    )

                filename = os.path.join(
                        filename,
                        get_time_filename(screenshot=screenshot)
                        )
                file_type = 'png'

            else:
                file_type = file_extension

            if not self.params.overwrite and os.path.exists(filename):
                return None

        if file_type == 'jpg':
            file_type = 'jpeg'

        if file_type not in get_supported_formats():
            raise ScreenshotActionError(f"unrecognized image format '{file_type}'")

        try:
            # add exif data. This is sketchy but we don't need to
            # dynamically generate it, just find and replace.
            # This avoids needing an external library for such a simple
            # thing.
            exif_data = self.EXIF_TEMPLATE.replace(
                '[[VERSION]]'.encode(),
                '3.x.x'.encode()
            )
            exif_data = exif_data.replace(
                '[[CREATE_DATE]]'.encode(),
                datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode()
            )

            # open(... , 'w*') truncates the file, so this is not vulnerable
            # to the 2023 android and windows 11 problem of leaking data from
            # cropped screenshots.
            with open(filename, "wb") as file_pointer:
                screenshot.get_image().save(
                    file_pointer, file_type.upper(), exif=exif_data
                )

        except IOError as exc:
            raise ScreenshotActionError from exc

        if screenshot is not None:
            screenshot.set_saved_path(filename)

        return filename
