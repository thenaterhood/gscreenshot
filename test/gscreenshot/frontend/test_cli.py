from importlib.resources import as_file, files
import unittest
from unittest.mock import Mock, mock_open
from PIL import Image
import mock

from src.gscreenshot.screenshot.screenshot import Screenshot
from src.gscreenshot.frontend.cli import run
from src.gscreenshot.frontend.args import get_args


class CLITestGscreenshotCalls(unittest.TestCase):

    def setUp(self):
        self.app = Mock()
        self.app.get_available_cursors.return_value = {}
        pixmaps_path = "gscreenshot.resources.pixmaps"
        screenshot = None
        with as_file(files(pixmaps_path).joinpath('gscreenshot.png')) as png_path:
            img = Image.open(png_path)
            self.app.get_thumbnail.return_value = img
            screenshot = Screenshot(img)

        self.screenshot_collection = Mock()
        self.screenshot_collection.cursor_current.return_value = screenshot
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

    @mock.patch('src.gscreenshot.actions.subprocess.run')
    def test_notify(self, notify):
        args = get_args(["--delay", "5", "--notify"])
        run(app=self.app, args=args)
        self.app.screenshot_full_display.assert_called_with(delay=5, capture_cursor=False, cursor_name=None)
        notify.assert_called_once()

    def test_selection_color(self):
        args = get_args(["--delay", "5", "--select-color", "#00000000", "-s"])
        run(app=self.app, args=args)
        self.app.set_select_color.assert_called_with("#00000000")
        self.app.screenshot_selected.assert_called_with(delay=5, capture_cursor=False, cursor_name=None)

    def test_selection_weight(self):
        args = get_args(['--select-border-weight', '20', '--select-color', '', '-s'])
        run(app=self.app, args=args)
        self.app.set_select_border_weight.assert_called_with(20)
        self.app.screenshot_selected.assert_called()

    @mock.patch('src.gscreenshot.screenshot.actions.copy.subprocess.Popen')
    @mock.patch('src.gscreenshot.screenshot.actions.xdg_open.subprocess.run')
    def test_clip_and_open(self, copy, xdg_open):
        args = get_args(["--clip", "--open"])
        run(app=self.app, args=args)

        self.app.screenshot_full_display.assert_called()
        copy.assert_called_once()
        xdg_open.assert_called_once()

    @mock.patch('builtins.open', new_callable=mock_open, create=True)
    @mock.patch('src.gscreenshot.screenshot.actions.xdg_open.subprocess.run')
    def test_save_filename(self, fopen, xdg_open):
        args = get_args(["--open", "--filename", "potato.png"])
        run(app=self.app, args=args)

        self.app.screenshot_full_display.assert_called()
        fopen.assert_called_once()
        xdg_open.assert_called_once()
