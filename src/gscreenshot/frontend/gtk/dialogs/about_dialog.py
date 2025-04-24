#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
'''
Dialog boxes for the GTK frontend to gscreenshot
'''
import gettext
from typing import Dict

from gi import require_version

from gscreenshot.frontend.gtk.util import image_to_pixbuf
from gscreenshot.meta import (
    get_app_icon,
    get_program_authors,
    get_program_description,
    get_program_license_text,
    get_program_name,
    get_program_version,
    get_program_website,
)
require_version('Gtk', '3.0')
from gi.repository import Gtk # type: ignore

i18n = gettext.gettext


class AboutDialog(Gtk.AboutDialog):
    '''An about dialog'''

    def __init__(self, capabilities: Dict[str, str], parent=None):
        super().__init__(self, transient_for=parent)

        self.set_authors(get_program_authors())

        description = i18n(get_program_description())

        capabilities_formatted = []
        capabilities_rows = []

        for capability, provider in capabilities.items():
            capabilities_formatted.append(f"{i18n(capability)} ({provider})")

        capabilities_row = ""
        for count, item in enumerate(sorted(capabilities_formatted), 1):
            capabilities_row = capabilities_row + item.ljust(50)
            if count % 2 == 0:
                capabilities_rows.append(capabilities_row)
                capabilities_row = ""

        description += "\n" + i18n("Available features:")
        description += "\n" + "\n".join(capabilities_rows)

        self.set_comments(i18n(description))

        website = get_program_website()
        self.set_website(website)
        self.set_website_label(website)

        self.set_program_name(get_program_name())
        self.set_title(i18n("About"))

        self.set_license(get_program_license_text())

        self.set_version(get_program_version())

        self.set_logo(image_to_pixbuf(get_app_icon()))
