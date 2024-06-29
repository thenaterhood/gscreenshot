#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
'''
Dialog boxes for the GTK frontend to gscreenshot
'''
import gettext
import pygtkcompat

pygtkcompat.enable()
pygtkcompat.enable_gtk(version='3.0')
from gi.repository import Gtk

i18n = gettext.gettext


class FileSaveDialog(object):
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
        action = Gtk.FILE_CHOOSER_ACTION_SAVE
        if self._choose_directory:
            action = Gtk.FILE_CHOOSER_ACTION_CREATE_FOLDER

        chooser = Gtk.FileChooserDialog(
                transient_for=self.parent,
                title=None,
                action=action,
                buttons=(
                    Gtk.STOCK_CANCEL,
                    Gtk.RESPONSE_CANCEL,
                    Gtk.STOCK_SAVE,
                    Gtk.RESPONSE_OK
                    )
                )

        if self.default_filename is not None:
            chooser.set_current_name(self.default_filename)

        if self.default_folder is not None:
            chooser.set_current_folder(self.default_folder)

        chooser.set_do_overwrite_confirmation(True)

        response = chooser.run()

        if response == Gtk.RESPONSE_OK:
            return_value = chooser.get_filename()
        else:
            return_value = None

        chooser.destroy()
        return return_value
