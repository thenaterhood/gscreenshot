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


class WarningDialog():
    '''A warning dialog'''

    def __init__(self, message, parent=None):
        self.parent = parent
        self.message_dialog = Gtk.MessageDialog(
                parent,
                None,
                Gtk.MessageType.WARNING,
                Gtk.ButtonsType.OK,
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
