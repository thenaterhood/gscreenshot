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


class WarningDialog():
    '''A warning dialog'''

    def __init__(self, message, parent=None):
        self.parent = parent
        self.message_dialog = Gtk.MessageDialog(
                parent,
                None,
                Gtk.MESSAGE_WARNING,
                Gtk.BUTTONS_OK,
                message
                )

    def run(self):
        '''Run the warning dialog'''
        if self.parent is not None:
            self.parent.set_sensitive(False)

        self.message_dialog.run()
        self.message_dialog.destroy()

        if self.parent is not None:
            self.parent.set_sensitive(True)
