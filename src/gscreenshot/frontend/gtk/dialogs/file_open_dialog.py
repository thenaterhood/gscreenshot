#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
'''
Dialog boxes for the GTK frontend to gscreenshot
'''
import gettext

from gi import require_version
require_version('Gtk', '3.0')
from gi.repository import Gtk # type: ignore

i18n = gettext.gettext


class FileOpenDialog(Gtk.FileChooserNative):
    '''The 'open a file' dialog'''

    def __init__(self, default_filename=None, default_folder=None,
        parent=None, mime_types=None,
    ):
        file_filter:Gtk.FileFilter = Gtk.FileFilter()

        if mime_types:
            _ = [file_filter.add_mime_type(format) for format in mime_types]

        super().__init__(
            transient_for=parent,
            title=None,
            action=Gtk.FileChooserAction.OPEN,
            filter=file_filter,
        )

        if default_filename is not None:
            self.set_current_name(default_filename)

        if default_folder is not None:
            self.set_current_folder(default_folder)

        self.set_do_overwrite_confirmation(True)

        self.connect("response", self._on_response)

        self.filename = None

    def run(self):
        super().run()

        return self.filename

    def _on_response(self, _, response):
        if response == Gtk.ResponseType.ACCEPT:
            self.filename = self.get_filename()
