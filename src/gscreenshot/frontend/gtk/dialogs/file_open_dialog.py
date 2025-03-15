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


class FileOpenDialog():
    '''The 'open a file' dialog'''
    #pylint: disable=too-many-arguments
    def __init__(self, default_filename=None, default_folder=None,
        parent=None, choose_directory=False, mime_types=None,
    ):
        
        self.default_filename = default_filename
        self.default_folder = default_folder
        self.parent = parent
        self._choose_directory = choose_directory
        self._mime_types = mime_types

    def run(self):
        ''' Run the dialog'''
        filename = self.request_file()

        return filename

    def request_file(self):
        '''Run the file selection dialog'''

        file_filter:Gtk.FileFilter = Gtk.FileFilter()

        if self._mime_types:
            _ = [file_filter.add_mime_type(format) for format in self._mime_types]

        chooser = Gtk.FileChooserNative(
                transient_for=self.parent,
                title=None,
                action=Gtk.FileChooserAction.OPEN,
                filter=file_filter,
                )

        if self.default_filename is not None:
            chooser.set_current_name(self.default_filename)

        if self.default_folder is not None:
            chooser.set_current_folder(self.default_folder)

        chooser.set_do_overwrite_confirmation(True)

        response = chooser.run()

        if response in [Gtk.ResponseType.OK, Gtk.ResponseType.ACCEPT]:
            return_value = chooser.get_filename()
        else:
            return_value = None

        chooser.destroy()
        return return_value
