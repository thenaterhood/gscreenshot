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


class FileSaveDialog():
    '''The 'save as' dialog'''
    def __init__(self, default_filename=None, default_folder=None,
        parent=None, choose_directory=False
    ):
        self.default_filename = default_filename
        self.default_folder = default_folder
        self.parent = parent
        self._choose_directory = choose_directory

    def run(self):
        ''' Run the dialog'''
        filename = self.request_file()

        return filename

    def request_file(self):
        '''Run the file selection dialog'''
        action = Gtk.FileChooserAction.SAVE
        if self._choose_directory:
            action = Gtk.FileChooserAction.CREATE_FOLDER

        chooser = Gtk.FileChooserDialog(
                transient_for=self.parent,
                title=None,
                action=action,
                buttons=(
                    i18n("Cancel"),
                    Gtk.ResponseType.CANCEL,
                    i18n("Save"),
                    Gtk.ResponseType.OK
                    )
                )

        if self.default_filename is not None:
            chooser.set_current_name(self.default_filename)

        if self.default_folder is not None:
            chooser.set_current_folder(self.default_folder)

        chooser.set_do_overwrite_confirmation(True)

        response = chooser.run()

        if response == Gtk.ResponseType.OK:
            return_value = chooser.get_filename()
        else:
            return_value = None

        chooser.destroy()
        return return_value
