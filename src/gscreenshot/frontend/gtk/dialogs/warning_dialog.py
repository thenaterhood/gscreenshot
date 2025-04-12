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


class WarningDialog(Gtk.MessageDialog):
    '''A warning dialog'''

    def __init__(self, message, parent=None):
        self.parent = parent
        super().__init__(
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

        super().run()
        self.destroy()

        if self.parent is not None:
            self.parent.set_sensitive(True)
