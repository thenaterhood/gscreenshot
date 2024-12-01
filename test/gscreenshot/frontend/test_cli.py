from importlib.resources import as_file, files
import unittest
from unittest.mock import Mock
from PIL import Image

from src.gscreenshot.frontend.cli import run
from src.gscreenshot.frontend.args import get_args


class CLITestGscreenshotCalls(unittest.TestCase):

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

    def test_smoke(self):
        args = get_args([])
        run(app=self.app, args=args)
        self.app.screenshot_full_display.assert_called_with(delay=0, capture_cursor=False, cursor_name=None)

    def test_params_fullscreen(self):
        # TODO this should also test a custom pointer glyph
        args = get_args(["--delay", "5", "--pointer"])
        run(app=self.app, args=args)
        self.app.screenshot_full_display.assert_called_with(delay=5, capture_cursor=True, cursor_name=None)

    def test_params_region(self):
        # TODO this should also test a custom pointer glyph
        args = get_args(["--delay", "5", "--pointer", "-s"])
        run(app=self.app, args=args)
        self.app.screenshot_selected.assert_called_with(delay=5, capture_cursor=True, cursor_name=None)

    def test_notify(self):
        args = get_args(["--delay", "5", "--notify"])
        run(app=self.app, args=args)
        self.app.screenshot_full_display.assert_called_with(delay=5, capture_cursor=False, cursor_name=None)
        self.app.show_screenshot_notification.assert_called()

    def test_selection_color(self):
        args = get_args(["--delay", "5", "--select-color", "#00000000", "-s"])
        run(app=self.app, args=args)
        self.app.set_select_color.assert_called_with("#00000000")
        self.app.screenshot_selected.assert_called_with(delay=5, capture_cursor=False, cursor_name=None)

    def test_clip_and_open(self):
        args = get_args(["--clip", "--open"])
        run(app=self.app, args=args)

        self.app.screenshot_full_display.assert_called()
        self.app.copy_last_screenshot_to_clipboard.assert_called()
        self.app.open_last_screenshot.assert_called()

    def test_save_filename(self):
        args = get_args(["--open", "--filename", "potato.png"])
        run(app=self.app, args=args)

        self.app.screenshot_full_display.assert_called()
        self.app.save_last_image.assert_called_with("potato.png")
        self.app.open_last_screenshot.assert_called()
