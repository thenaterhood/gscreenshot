from datetime import datetime
import platform
import typing

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from gscreenshot.screenshot.screenshot import Screenshot

def interpolate_filename(filename:str, screenshot: typing.Optional["Screenshot"] = None) -> str:
    '''
    Does interpolation of a filename, as the following:
        $$   a literal '$'
        $a   system hostname
        $h   image's height in pixels
        $p   image's size in pixels
        $w   image's width in pixels

        Format operators starting with "%" are
        run through strftime.
    '''
    if "$" not in filename and "%" not in filename:
        return filename

    interpolated = f"{filename}"

    general_replacements:typing.Dict[str, str] = {
        '$$': '$',
        '$a': platform.node()
    }

    if screenshot:
        image = screenshot.get_image()
        if image is not None:
            general_replacements.update({
                '$h': str(image.height),
                '$p': str(image.height * image.width),
                '$w': str(image.width)
            })

    for fmt, replacement in general_replacements.items():
        interpolated = interpolated.replace(fmt, replacement)

    now = datetime.now()
    interpolated = now.strftime(interpolated)

    return interpolated


def get_time_filename(screenshot: typing.Optional["Screenshot"] = None) -> str:
    """
    Generates a returns a filename based on the current time

    Returns:
        str
    """
    return interpolate_filename("gscreenshot_%Y-%m-%d-%H%M%S.png", screenshot)


def get_time_foldername(screenshot: typing.Optional["Screenshot"]) -> str:
    '''Generates a time-based folder name'''
    return interpolate_filename("gscreenshot_%Y-%m-%d-%H%M%S", screenshot)