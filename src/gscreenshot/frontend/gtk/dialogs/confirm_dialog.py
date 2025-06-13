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


class ConfirmationDialog(Gtk.Dialog):
    '''A confirmation dialog'''

    def __init__(self, message, parent=None):
        super().__init__(self, title=i18n("Confirmation"), transient_for=parent, flags=0)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            "Continue", Gtk.ResponseType.OK
        )
        self.set_default_size(300, 100)
        label = Gtk.Label(label=message)
        label.set_line_wrap(True)
        label.set_max_width_chars(60)
        label.set_margin_end(20)
        label.set_margin_start(20)
        label.set_margin_top(20)

        box = self.get_content_area()
        box.add(label)

        self.connect("response", self._on_response)
        self.confirmed = False
        box.show_all()

    def _on_response(self, _, response):
        self.confirmed = response == Gtk.ResponseType.OK
