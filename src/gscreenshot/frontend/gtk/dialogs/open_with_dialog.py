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


class OpenWithDialog(Gtk.AppChooserDialog):
    '''The "Open With" dialog'''

    def __init__(self, parent=None):

        Gtk.AppChooserDialog.__init__(self, content_type="image/png", parent=parent)
        self.set_title(i18n("Choose an Application"))
        self.connect("response", self._on_response)
        self.appinfo = None

    def _on_response(self, _, response):
        if response == Gtk.ResponseType.OK:
            self.appinfo = self.get_app_info()
        else:
            self.appinfo = None