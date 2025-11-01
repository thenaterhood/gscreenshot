import typing

from PIL import Image

from gscreenshot.compat import get_resource_file, get_resource_string, get_version


def get_program_authors() -> typing.List[str]:
    """
    Returns the list of authors

    Returns:
        string[]
    """
    authors = [
            "Nate Levesque <public@thenaterhood.com>",
            "Original Author (2006)",
            "matej.horvath <matej.horvath@gmail.com>"
            ]

    return authors


def get_app_icon(variant: str = "") -> Image.Image:
    """Returns the application icon"""
    name = "gscreenshot.png" if not variant else f"gscreenshot-{variant}.png"
    pixmaps_path = 'gscreenshot.resources.pixmaps'
    filename = get_resource_file(pixmaps_path, name)
    return Image.open(filename)


def get_program_description() -> str:
    """Returns the program description"""
    return "A simple screenshot tool supporting multiple backends."


def get_program_website() -> str:
    """Returns the URL of the program website"""
    return "https://github.com/thenaterhood/gscreenshot"


def get_program_name() -> str:
    """Returns the program name"""
    return "gscreenshot"


def get_program_license_text() -> str:
    """Returns the license text"""
    return get_resource_string("gscreenshot.resources", "LICENSE")


def get_program_license() -> str:
    """Returns the license name"""
    return "GPLv2"


def get_program_version(padded: bool=False) -> str:
    """Returns the program version"""
    if not padded:
        return get_version()
    version_str = get_version().split(".")
    padded_version = [v.rjust(2, "0") for v in version_str]
    return ".".join(padded_version)
