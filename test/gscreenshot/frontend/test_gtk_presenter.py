from importlib.resources import as_file, files
import unittest
from unittest.mock import MagicMock
from PIL import Image
import mock

from gscreenshot.frontend.presenter import Presenter


class GtkPresenterTest(unittest.TestCase):

    def setUp(self):
        self.app = MagicMock()
        self.app.get_available_cursors.return_value = {}
        pixmaps_path = "gscreenshot.resources.pixmaps"
        with as_file(files(pixmaps_path).joinpath('gscreenshot.png')) as png_path:
            self.app.get_thumbnail.return_value = Image.open(
                    png_path
                )
        self.screenshot_collection = MagicMock()
        self.app.get_screenshot_collection.return_value = self.screenshot_collection
        self.view = MagicMock()
        self.view.get_preview_dimensions.return_value = (20, 30)
        self.presenter = Presenter(self.app, self.view)

    def test_on_copy_clicked_gtk_persistent_clipboard(self):
        self.view.copy_to_clipboard.return_value = True
        success = self.presenter.on_button_copy_clicked()
        self.app.copy_last_screenshot_to_clipboard.assert_not_called()
        self.view.copy_to_clipboard.assert_called_once()
        self.assertTrue(success)

    @mock.patch('src.gscreenshot.screenshot.actions.copy.subprocess.Popen')
    def test_on_copy_clicked_gtk_no_persistent_clipboard(self, copy):
        self.view.copy_to_clipboard.return_value = False
        self.app.copy_last_screenshot_to_clipboard.return_value = True
        success = self.presenter.on_button_copy_clicked()
        self.view.copy_to_clipboard.assert_called_once()
        copy.assert_called_once()
        self.assertTrue(success)

    @mock.patch('src.gscreenshot.screenshot.actions.xdg_open.subprocess.run')
    def test_on_button_open_clicked(self, xdg_open):
        self.app.open_last_screenshot.return_value = True
        self.screenshot_collection.cursor_current.return_value = None
        self.presenter.on_button_open_clicked()
        xdg_open.assert_called_once()
        self.app.quit.assert_called_once()

    def test_on_fullscreen_toggle(self):
        self.presenter.on_fullscreen_toggle()
        self.view.toggle_fullscreen.assert_called_once()

    def test_on_button_quit_clicked(self):
        self.screenshot_collection.len = 1
        self.presenter.on_button_quit_clicked()

        self.app.quit.assert_called_once()

    def test_on_window_resize(self):
        self.presenter.on_window_resize()
        self.view.resize.assert_called_once()
        # Called once in the constructor already
        self.assertEqual(self.app.current_always.get_preview.call_count, 2)

    def test_on_button_copy_and_close_clicked(self):
        self.screenshot_collection.cursor_current.return_value = None
        self.presenter.on_button_copy_and_close_clicked()
        self.view.copy_to_clipboard.assert_called_once()
        self.app.quit.assert_called_once()

    def test_capture_cursor_toggled_active(self):
        widget_mock = MagicMock()
        self.view.widget_bool_value.return_value = True

        self.presenter.capture_cursor_toggled(widget_mock)
        self.view.show_cursor_options.assert_called_with(True)

    def test_capture_cursor_toggled_inactive(self):
        widget_mock = MagicMock()
        self.view.widget_bool_value.return_value = False

        self.presenter.capture_cursor_toggled(widget_mock)
        self.view.show_cursor_options.assert_called_with(False)

    def test_on_button_all_clicked(self):
        # Note - this is more of an integration test as we're not
        # mocking any of the threading
        self.presenter.on_button_all_clicked()
        self.app.screenshot_full_display.assert_called_once()
        self.app.current_always.get_preview.assert_called_once()
        self.view.update_preview.assert_called_once()

    def test_on_button_window_clicked(self):
        self.presenter.on_button_window_clicked()
        self.app.screenshot_selected.assert_called_once()
        self.app.current_always.get_preview.assert_called_once()
        self.view.update_preview.assert_called_once()

    def test_on_button_selectarea_clicked(self):
        self.presenter.on_button_selectarea_clicked()
        self.app.screenshot_selected.assert_called_once()
        self.app.current_always.get_preview.assert_called_once()
        self.view.update_preview.assert_called_once()
