#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
#pylint: disable=too-many-statements
'''
CLI frontend
'''

import gettext
import logging
import typing
from PIL import Image
from gscreenshot.frontend.abstract_view import AbstractGscreenshotView
from gscreenshot.meta import (
    get_program_authors,
    get_program_description,
    get_program_license,
    get_program_name,
    get_program_version,
    get_program_website,
)
from gscreenshot.screenshot import ScreenshotCollection
from gscreenshot.screenshot.screenshot import Screenshot

_ = gettext.gettext
log = logging.getLogger(__name__)


class GscreenshotCli(AbstractGscreenshotView):
    '''View class for the CLI frontend'''

    def __init__(self, args):
        self._args = args

    def update_gallery_controls(self, screenshots:ScreenshotCollection):
        '''
        updates the preview controls to match the current state
        '''
        return

    def connect_signals(self, presenter):
        '''
        connects signals
        '''
        return

    def notify_save_complete(self):
        """
        Show an indication that saving the file completed
        """
        return

    def notify_copy_complete(self):
        """
        Show an indication that copying the file completed
        """
        return

    def notify_open_complete(self):
        """
        Show an indication that opening the file completed
        """
        return

    def set_busy(self):
        """
        Sets the window as busy with visual indicators
        """
        return

    def set_ready(self):
        """
        Sets the window as ready with visual indicators
        """
        return

    def show_cursor_options(self, show: bool):
        '''
        Toggle the cursor combobox and label hidden/visible
        '''
        return

    def update_available_cursors(self, cursors: dict, selected: typing.Optional[str] = None):
        '''
        Update the available cursor selection in the combolist
        Params: self, {name: PIL.Image}
        '''
        return

    def run(self):
        '''Run the view'''
        return

    def show_actions_menu(self):
        '''
        Show the actions/saveas menu at the pointer
        '''
        return

    def toggle_fullscreen(self):
        '''Toggle the window to full screen'''
        return

    def handle_state_event(self, _, event):
        '''Handles a window state event'''
        return

    def hide(self):
        '''Hide the view'''
        return

    def unhide(self):
        '''Unhide the view'''
        return

    def resize(self):
        '''Resize the display'''
        return

    def get_preview_dimensions(self):
        '''Get the current dimensions of the preview widget'''
        return 0, 0

    def update_preview(self, img: Image.Image):
        '''
        Update the preview widget with a new image.

        This assumes the pixbuf has already been resized appropriately.
        '''
        return

    def idle_add(self, callback):
        """
        Passthrough for GLib.idle_add
        """
        return

    def handle_preview_click_event(self, widget, event, *args):
        '''
        Handle a click on the screenshot preview widget
        '''
        return

    def copy_to_clipboard(self, screenshot: Screenshot) -> bool:
        """
        Copy the provided image to the screen's clipboard,
        if it supports persistence
        """
        return False

    def show_warning(self, warning: str):
        """
        Show a warning message
        """
        log.warning(warning)

    def show_about(self, capabilities: typing.Dict[str, str]):
        """
        Show the about dialog
        """
        description = get_program_description()
        name = get_program_name()
        version = get_program_version()

        capabilities_formatted = []
        for capability, provider in capabilities.items():
            capabilities_formatted.append(f"{_(capability)} ({provider})")

        print(f"{name} {version}; {description}")
        print()
        print(_("Available features:"))
        for count, item in enumerate(sorted(capabilities_formatted), 1):
            print(item.ljust(50), end='')
            if count % 2 == 0:
                print()
        print()
        print()
        print(get_program_website())
        print("")
        print(_("Author(s)"))
        print("\n".join(get_program_authors()))
        print("")
        print(_("Licensed as {0}").format(get_program_license()))

    def ask_open_with(self):
        """
        Ask the user what to open a file with

        Note: return type is Gtk appinfo, for which
        I haven't gotten the return type for type hinting TODO
        """
        return

    def ask_for_save_location(
            self, default_filename: str, default_folder: str
    ) -> typing.Optional[str]:
        """
        Ask the user where to save something

        Returns a file path as a string
        """
        if self._args.filename:
            return self._args.filename

        return default_filename

    def ask_for_save_directory(
            self, default_folder: str, parent_folder: str
    ) -> typing.Optional[str]:
        """
        Ask the user for a directory to save to

        This is not equivalent to ask_for_save_location.
        ask_for_save_location returns a filename whereas this returns a folder name
        """
        return None

    def ask_for_file_to_open(self, formats=None) -> typing.Optional[str]:
        """
        Ask the user for a file to open
        """
        return self._args.pointer_glyph

    def ask_confirmation(self, message: str) -> bool:
        """
        Request confirmation from the user
        """
        return False

    def widget_bool_value(self, widget) -> bool:
        return bool(widget)

    def widget_int_value(self, widget) -> int:
        return int(widget)

    def widget_str_value(self, widget) -> typing.Optional[str]:
        return str(widget) if widget else None
