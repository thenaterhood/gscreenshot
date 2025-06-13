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


class FileSaveDialog(Gtk.FileChooserDialog):
    '''The 'save as' dialog'''
    def __init__(self, default_filename=None, default_folder=None,
        parent=None, choose_directory=False
    ):
        action = Gtk.FileChooserAction.SAVE
        if choose_directory:
            action = Gtk.FileChooserAction.CREATE_FOLDER

        super().__init__(
            transient_for=parent,
            title=None,
            action=action,
        )

        self.add_buttons(
            i18n("Cancel"),
            Gtk.ResponseType.CANCEL,
            i18n("Save"),
            Gtk.ResponseType.OK
        )

        if default_filename is not None:
            self.set_current_name(default_filename)

        if default_folder is not None:
            self.set_current_folder(default_folder)

        self.set_do_overwrite_confirmation(True)
        self.connect("response", self._on_response)
        self.filename = None

    def _on_response(self, _, response):
        if response == Gtk.ResponseType.OK:
            self.filename = self.get_filename()
        else:
            self.filename = None

    def run(self):
        ''' Run the dialog'''
        super().run()
        return self.filename
