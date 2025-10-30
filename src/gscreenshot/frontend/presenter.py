#pylint: disable=unused-argument
#pylint: disable=wrong-import-order
#pylint: disable=wrong-import-position
#pylint: disable=ungrouped-imports
#pylint: disable=too-many-statements
'''
Classes for the GTK gscreenshot frontend
'''
import gettext
import threading
import typing
from gscreenshot import Gscreenshot
from gscreenshot.cache import GscreenshotCache
from gscreenshot.filename import get_time_filename
from gscreenshot.frontend.abstract_view import AbstractGscreenshotView
from gscreenshot.screenshot.actions import (
    CopyAction,
    ScreenshotActionError,
    SaveTmpfileAction,
    XdgOpenAction,
)
from gscreenshot.screenshot.actions.save import SaveAction
from gscreenshot.screenshot.effects import CropEffect

from gscreenshot.util import get_supported_formats

i18n = gettext.gettext


class Presenter():
    '''Presenter class for the frontend'''

    __slots__ = ('_delay', '_app', '_hide',
            '_view', '_keymappings', '_capture_cursor',
            '_cursor_selection', '_overwrite_mode')

    _delay: int
    _app: Gscreenshot
    _hide: bool
    _view: AbstractGscreenshotView
    _keymappings: dict
    _capture_cursor: bool
    _overwrite_mode: bool
    _cursor_selection: typing.Optional[str]

    def __init__(self, application: Gscreenshot, view: AbstractGscreenshotView):
        self._app = application
        self._view = view
        self._delay = 0
        self._hide = True
        self._capture_cursor = False
        self._show_preview()
        self._keymappings = {}
        self._overwrite_mode = True

        cursors = self._app.get_available_cursors()
        cursors[i18n("custom")] = None

        self._cursor_selection = None

        self._view.update_available_cursors(
                cursors
                )

        self._view.update_available_regions(
            self._app.get_available_regions(),
            self.on_stored_region_selected
        )

        self._view.show_cursor_options(self._capture_cursor)

    def _begin_take_screenshot(self, app_method, **args):
        app_method(delay=self._delay,
            capture_cursor=self._capture_cursor,
            cursor_name=self._cursor_selection,
            overwrite=self._overwrite_mode,
            **args)

        self._view.idle_add(self._end_take_screenshot)

    def _end_take_screenshot(self):
        self._show_preview()
        screenshot_collection = self._app.get_screenshot_collection()
        self._view.update_gallery_controls(screenshot_collection)

        self._view.unhide()
        self._view.set_ready()

    def set_keymappings(self, keymappings: dict):
        '''Set the keymappings'''
        self._keymappings = keymappings

    def window_state_event_handler(self, widget, event, *_):
        '''Handle window state events'''
        self._view.handle_state_event(widget, event)

    def take_screenshot(self, app_method: typing.Callable, **args):
        '''Take a screenshot using the passed app method'''
        self._view.set_busy()

        if self._hide:
            self._view.hide()

        # Do work in background thread.
        # Taken from here: https://wiki.gnome.org/Projects/PyGObject/Threading
        _thread = threading.Thread(target=self._begin_take_screenshot(app_method, **args))
        _thread.daemon = True
        _thread.start()

    def handle_keypress(self, widget, event, *args):
        """
        This method handles individual keypresses. These are
        handled separately from accelerators (which include
        modifiers).
        """
        if event.keyval in self._keymappings:
            # The called function should return True to prevent
            # further handling of the keypress
            return self._keymappings[event.keyval](widget)

        return False

    def handle_preview_click_event(self, *args):
        '''
        Handle a click on the screenshot preview widget
        '''
        self._view.handle_preview_click_event(*args)

    def hide_window_toggled(self, widget):
        '''Toggle the window to hidden'''
        self._hide = self._view.widget_bool_value(widget)

    def capture_cursor_toggled(self, widget):
        '''Toggle capturing cursor'''
        self._capture_cursor = self._view.widget_bool_value(widget)
        self._view.show_cursor_options(self._capture_cursor)

    def overwrite_mode_toggled(self, widget):
        '''Toggle overwrite or multishot mode'''
        self._overwrite_mode = self._view.widget_bool_value(widget)

    def delay_value_changed(self, widget):
        '''Handle a change with the screenshot delay input'''
        self._delay = self._view.widget_int_value(widget)

    def selected_cursor_changed(self, widget):
        '''Handle a change to the selected cursor'''
        try:
            cursor_selection = self._view.widget_str_value(widget)
        except IndexError:
            return

        if cursor_selection is None:
            return

        if cursor_selection == "custom":

            formats = [
                f"image/{format}" for format in get_supported_formats()
                if format not in ["pdf"]
            ]

            chosen = None
            cancelled = False
            while not (chosen or cancelled):
                chosen = self._view.ask_for_file_to_open(formats)
                if chosen is None:
                    cancelled = True

            if chosen:
                try:
                    cursor_selection = self._app.register_stamp_image(chosen)
                #pylint: disable=broad-except
                except Exception:
                    self._view.show_warning(f"Unable to open {chosen}")
                    cancelled = True

            if cancelled or cursor_selection is None:
                cursor_selection = self._cursor_selection

            cursors = self._app.get_available_cursors()
            cursors[i18n("custom")] = None
            self._view.update_available_cursors(
                cursors,
                cursor_selection
            )

        self._cursor_selection = cursor_selection

    def on_button_all_clicked(self, *_):
        '''Take a screenshot of the full screen'''
        self.take_screenshot(
            self._app.screenshot_full_display
            )

    def on_button_window_clicked(self, *args):
        '''Take a screenshot of a window'''
        self._button_select_area_or_window_clicked(args)

    def on_button_selectarea_clicked(self, *args):
        '''Take a screenshot of an area'''
        self._button_select_area_or_window_clicked(args)

    def _button_select_area_or_window_clicked(self, *_):
        '''Take a screenshot of an area or window'''
        self.take_screenshot(
            self._app.screenshot_selected
            )

    def on_preview_drag(self, _widget, _drag_context, data, _info, _time):
        '''
        Handle dragging and dropping the image preview
        '''
        screenshot = self._app.current
        if not screenshot:
            return

        fname = None
        action = SaveTmpfileAction()
        try:
            fname = action.execute(screenshot)
        except ScreenshotActionError:
            pass

        if fname is None:
            return

        data.set_uris([f"file://{fname}"])

    def on_delete(self, *_):
        """
        remove the current screenshot
        """
        screenshots = self._app.get_screenshot_collection()
        current = self._app.current
        if current:
            screenshots.remove(current)

            self._view.update_gallery_controls(screenshots)
            self._show_preview()

        return True

    def on_use_last_region_clicked(self, *_):
        '''
        Take a screenshot with the same region as the
        screenshot under the cursor, if applicable
        '''
        last_screenshot = self._app.current
        region = None

        if last_screenshot is not None:
            effects = last_screenshot.get_effects()
            crop_effect = next((i for i in effects if isinstance(i, CropEffect)), None)
            if crop_effect and "region" in crop_effect.meta:
                region = crop_effect.meta["region"]

        if region:
            self.take_screenshot(
                self._app.screenshot_selected,
                region=region
            )

        else:
            self.take_screenshot(
                self._app.screenshot_full_display
            )

    def on_preview_prev_clicked(self, *_):
        '''Handle a click of the "previous" button on the preview'''
        screenshot_collection = self._app.get_screenshot_collection()
        screenshot_collection.cursor_prev()
        self._show_preview()
        self._view.update_gallery_controls(screenshot_collection)
        return True

    def on_preview_next_clicked(self, *_):
        '''Handle a click of the "next" button on the preview'''
        screenshot_collection = self._app.get_screenshot_collection()
        screenshot_collection.cursor_next()
        self._show_preview()
        self._view.update_gallery_controls(screenshot_collection)
        return True

    def effect_checkbox_handler(self, widget, effect):
        '''
        Handles toggling effects on and off
        '''
        screenshot = self._app.current
        if screenshot is None:
            return

        if self._view.widget_bool_value(widget):
            effect.enable()
        else:
            effect.disable()

        self._show_preview()

    def on_button_saveas_clicked(self, *_) -> bool:
        '''Handle the saveas button'''
        saved = False
        cancelled = False

        screenshot = self._app.current
        if screenshot is None:
            return False

        while not (saved or cancelled):
            cache = GscreenshotCache.load()
            fname = self._view.ask_for_save_location(
                get_time_filename(filetype=cache.last_save_type),
                cache.last_save_dir
            )
            saved = False
            if fname is not None:
                try:
                    saved = SaveAction(
                        filename=fname, update_cache=True
                    ).execute(screenshot) is not None
                except ScreenshotActionError:
                    self._view.show_warning(i18n("Failed to save screenshot!"))
            else:
                cancelled = True

        if saved:
            self._view.update_gallery_controls(self._app.get_screenshot_collection())
            self._view.notify_save_complete()
            return True

        return False

    def on_button_save_all_clicked(self, *_):
        '''Handle the "save all" button'''
        saved = False
        cancelled = False

        while not (saved or cancelled):
            fname = self._view.ask_for_save_directory(
                self._app.get_time_foldername(),
                GscreenshotCache.load().last_save_dir,
            )
            if fname is not None:
                self._view.set_busy()
                saved = self._app.save_screenshot_collection(fname)
                self._view.set_ready()
            else:
                cancelled = True

        if saved:
            self._view.update_gallery_controls(self._app.get_screenshot_collection())
            self._view.notify_save_complete()

    def on_button_openwith_clicked(self, *_):
        '''Handle the "open with" button'''
        screenshot = self._app.current
        if screenshot is None:
            return

        try:
            fname = SaveTmpfileAction().execute(screenshot)
        except ScreenshotActionError:
            return

        if fname is None:
            return

        appinfo = self._view.ask_open_with()

        if appinfo is not None:
            if appinfo.launch_uris(["file://"+fname], None):
                self._view.notify_open_complete()

                screenshots = self._app.get_screenshot_collection()
                current = screenshots.cursor_current()
                if current is not None:
                    screenshots.remove(current)

                current = screenshots.cursor_current()
                if current is not None:
                    self._view.update_gallery_controls(screenshots)
                    self._show_preview()

                    return

                self.quit(None, skip_warning=True)

    def on_button_copy_clicked(self, *_) -> bool:
        """
        Copy the current screenshot to the clipboard
        """
        screenshot = self._app.current
        if screenshot is None:
            return False

        if not self._view.copy_to_clipboard(screenshot):
            try:
                CopyAction().execute(screenshot)
            except ScreenshotActionError as error:
                self._view.show_warning(
                    i18n(
                        "Your clipboard doesn't support persistence and {0} isn't available."
                    ).format(error),
                )
                return False

        self._view.notify_copy_complete()
        return True

    def on_button_copy_and_close_clicked(self, *_):
        """
        Copy the current screenshot to the clipboard and
        close gscreenshot
        """
        if self.on_button_copy_clicked():
            screenshots = self._app.get_screenshot_collection()
            current = screenshots.cursor_current()
            if current is not None:
                screenshots.remove(current)

            current = screenshots.cursor_current()
            if current is not None:
                self._view.update_gallery_controls(screenshots)
                self._show_preview()

                return

            self.quit(None, skip_warning=True)

    def on_button_open_clicked(self, *_):
        '''Handle the open button'''
        screenshot = self._app.current
        if not screenshot:
            return

        success = False
        try:
            success = XdgOpenAction().execute(screenshot)
        except ScreenshotActionError:
            pass

        if not success:
            self._view.show_warning(
                i18n("Please install xdg-open to open files.")
            )
        else:
            self._view.notify_open_complete()
            screenshots = self._app.get_screenshot_collection()
            current = screenshots.cursor_current()
            if current is not None:
                screenshots.remove(current)

            current = screenshots.cursor_current()
            if current is not None:
                self._view.update_gallery_controls(screenshots)
                self._show_preview()

                return
            self.quit(None, skip_warning=True)

    def on_button_about_clicked(self, *_):
        '''Handle the about button'''
        self._view.show_about(self._app.get_capabilities())

    def on_fullscreen_toggle(self, *_):
        '''Handle the window getting toggled to fullscreen'''
        self._view.toggle_fullscreen()

    def on_button_quit_clicked(self, *_, widget=None):
        '''Handle the quit button'''
        self.quit(widget)
        return True

    def on_window_main_destroy(self, widget=None):
        '''Handle the titlebar close button'''
        self.quit(widget)
        return True

    def on_window_resize(self, *_):
        '''Handle window resizes'''
        self._view.resize()
        self._show_preview()

    def on_region_save_clicked(self, *_, region_name = None):
        last_screenshot = self._app.current
        region = None

        if last_screenshot is not None:
            effects = last_screenshot.get_effects()
            crop_effect = next((i for i in effects if isinstance(i, CropEffect)), None)
            if crop_effect and crop_effect.enabled and "region" in crop_effect.meta:
                region = crop_effect.meta["region"]

        if not region:
            return

        region_name = region_name or self._view.ask_input("Region Name")
        if not region_name:
            return

        self._app.add_stored_region(region_name, region)

        self._view.update_available_regions(
            self._app.get_available_regions(),
            self.on_stored_region_selected
        )

    def on_stored_region_selected(self, menu_item, action: typing.Literal["new", "edit"] = "new"):
        region_name = self._view.widget_str_value(menu_item)
        region = None

        if region_name:
            region = self._app.get_available_regions().get(
                region_name
            )

        if action == "new":
            self.take_screenshot(
                self._app.screenshot_selected,
                region=region
            )
        elif action == "edit":
            screenshot = self._app.current_always
            effects = screenshot.get_effects()
            crop_effect = next((i for i in effects if isinstance(i, CropEffect)), None)
            if crop_effect and crop_effect.enabled:
                screenshot.remove_effect(crop_effect)

            screenshot.add_effect(CropEffect(region))
            self._show_preview()

    def on_settings_clicked(self, *_):
        def on_delete_region(region_name: str):
            self._app.remove_stored_region(region_name)
            self._view.update_available_regions(
                self._app.get_available_regions(),
                self.on_stored_region_selected,
            )

        self._view.show_settings(
            stored_regions=self._app.get_available_regions(),
            on_delete_region=on_delete_region,
        )

    def on_uncrop_clicked(self, *_):
        screenshot = self._app.current_always
        for effect in screenshot.get_effects():
            if isinstance(effect, CropEffect):
                effect.disable()

        self._show_preview()

    def on_change_region_clicked(self, region_name):
        region_name = self._view.widget_str_value(region_name)

        if not region_name:
            return

        screenshot = self._app.current_always
        region = self._app.get_available_regions().get(region_name)
        for effect in screenshot.get_effects():
            if isinstance(effect, CropEffect):
                effect.disable()

        screenshot.add_effect(CropEffect(region=region))
        self._show_preview()

    def quit(self, *args, skip_warning=False):
        '''Exit the app'''
        if skip_warning:
            self._app.quit()
            return True # not strictly needed most of the time

        screenshot_collection = self._app.get_screenshot_collection()

        if len(screenshot_collection) > 1 and screenshot_collection.has_unsaved():
            confirmed = self._view.ask_confirmation(
                i18n("There are unsaved screenshots. Quit without saving?"),
            )

            if not confirmed:
                return True

        self._app.quit()

        return True

    def _show_preview(self):
        height, width = self._view.get_preview_dimensions()

        if height > 0 and width > 0:
            preview_img = self._app.current_always.get_preview(width, height, with_border=True)
            self._view.update_preview(preview_img)
