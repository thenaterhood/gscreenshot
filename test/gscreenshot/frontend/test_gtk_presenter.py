from importlib.resources import as_file, files
import unittest
from unittest.mock import Mock
from PIL import Image
import mock

from gscreenshot.frontend.gtk.presenter import Presenter


class GtkPresenterTest(unittest.TestCase):

    def setUp(self):
        self.app = Mock()
        self.app.get_available_cursors.return_value = {}
        pixmaps_path = "gscreenshot.resources.pixmaps"
        with as_file(files(pixmaps_path).joinpath('gscreenshot.png')) as png_path:
            self.app.get_thumbnail.return_value = Image.open(
                    png_path
                )
        self.screenshot_collection = Mock()
        self.app.get_screenshot_collection.return_value = self.screenshot_collection
        self.view = Mock()
        self.view.get_preview_dimensions.return_value = (20, 30)
        self.presenter = Presenter(self.app, self.view)

    def test_on_copy_clicked_gtk_persistent_clipboard(self):
        self.view.copy_to_clipboard.return_value = True
        success = self.presenter.on_button_copy_clicked()
        self.app.copy_last_screenshot_to_clipboard.assert_not_called()
        self.view.copy_to_clipboard.assert_called_once()
        self.assertTrue(success)

    def test_on_copy_clicked_gtk_no_persistent_clipboard(self):
        self.view.copy_to_clipboard.return_value = False
        self.app.copy_last_screenshot_to_clipboard.return_value = True
        success = self.presenter.on_button_copy_clicked()
        self.app.copy_last_screenshot_to_clipboard.assert_called_once()
        self.view.copy_to_clipboard.assert_called_once()
        self.assertTrue(success)

    def test_on_button_open_clicked(self):
        self.app.open_last_screenshot.return_value = True
        self.screenshot_collection.cursor_current.return_value = None
        self.presenter.on_button_open_clicked()
        self.app.open_last_screenshot.assert_called_once()
        self.app.quit.assert_called_once()

    def test_on_fullscreen_toggle(self):
        self.presenter.on_fullscreen_toggle()
        self.view.toggle_fullscreen.assert_called_once()

    def test_on_button_quit_clicked(self):
        self.presenter.on_button_quit_clicked()
        self.app.quit.assert_called_once()

    def test_on_window_resize(self):
        self.presenter.on_window_resize()
        self.view.resize.assert_called_once()
        # Called once in the constructor already
        self.assertEqual(self.app.get_thumbnail.call_count, 2)

    def test_on_button_copy_and_close_clicked(self):
        self.screenshot_collection.cursor_current.return_value = None
        self.presenter.on_button_copy_and_close_clicked()
        self.view.copy_to_clipboard.assert_called_once()
        self.app.quit.assert_called_once()

    def test_capture_cursor_toggled_active(self):
        widget_mock = Mock()
        widget_mock.get_active.return_value = True

        self.presenter.capture_cursor_toggled(widget_mock)
        self.view.show_cursor_options.assert_called_with(True)

    def test_on_button_all_clicked(self):
        # Note - this is more of an integration test as we're not
        # mocking any of the threading
        self.presenter.on_button_all_clicked()
        self.app.screenshot_full_display.assert_called_once()
        self.app.get_thumbnail.assert_called_once()
        self.view.update_preview.assert_called_once()

    def test_on_button_window_clicked(self):
        self.presenter.on_button_window_clicked()
        self.app.screenshot_selected.assert_called_once()
        self.app.get_thumbnail.assert_called_once()
        self.view.update_preview.assert_called_once()

    def test_on_button_selectarea_clicked(self):
        self.presenter.on_button_selectarea_clicked()
        self.app.screenshot_selected.assert_called_once()
        self.app.get_thumbnail.assert_called_once()
        self.view.update_preview.assert_called_once()
