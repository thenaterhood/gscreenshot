from importlib.resources import as_file, files
import unittest
from unittest.mock import call, mock_open
from PIL import Image
import mock

from src.gscreenshot.screenshot.screenshot import Screenshot
from src.gscreenshot.frontend.cli import main
from src.gscreenshot.frontend.cli.args import get_args


class CLITestGscreenshotCalls(unittest.TestCase):

    def setUp(self):
        self.app = mock.MagicMock()
        self.app.get_available_cursors.return_value = {}
        pixmaps_path = "gscreenshot.resources.pixmaps"
        screenshot = None
        with as_file(files(pixmaps_path).joinpath('gscreenshot.png')) as png_path:
            img = Image.open(png_path)
            self.app.get_thumbnail.return_value = img
            screenshot = Screenshot(img)

        self.screenshot_collection = mock.MagicMock()
        self.screenshot_collection.cursor_current.return_value = screenshot
        self.app.get_screenshot_collection.return_value = self.screenshot_collection

    @mock.patch('builtins.open', new_callable=mock_open, create=True)
    @mock.patch('os.makedirs')
    def test_smoke(self, makedirs, fopen):
        args = get_args([])
        main(app=self.app, args=args)
        self.app.screenshot_full_display.assert_called_with(
            delay=0,
            capture_cursor=False,
            cursor_name=None,
            overwrite=True,
        )

    @mock.patch('builtins.open', new_callable=mock_open, create=True)
    @mock.patch('os.makedirs')
    def test_params_fullscreen(self, makedirs, fopen):
        # TODO this should also test a custom pointer glyph
        args = get_args(["--delay", "5", "--pointer"])
        main(app=self.app, args=args)
        self.app.screenshot_full_display.assert_called_with(
            delay=5,
            capture_cursor=True,
            cursor_name=None,
            overwrite=True,
        )

    @mock.patch('builtins.open', new_callable=mock_open, create=True)
    @mock.patch('os.makedirs')
    def test_params_region(self, makedirs, fopen):
        # TODO this should also test a custom pointer glyph
        args = get_args(["--delay", "5", "--pointer", "-s"])
        main(app=self.app, args=args)
        self.app.screenshot_selected.assert_called_with(
            delay=5, capture_cursor=True, cursor_name=None, overwrite=True
        )

    @mock.patch('builtins.open', new_callable=mock_open, create=True)
    @mock.patch('os.makedirs')
    @mock.patch('src.gscreenshot.actions.subprocess.run')
    def test_notify(self, notify, makedirs, fopen):
        args = get_args(["--delay", "5", "--notify"])
        main(app=self.app, args=args)
        self.app.screenshot_full_display.assert_called_with(
            delay=5, capture_cursor=False, cursor_name=None, overwrite=True
        )
        notify.assert_called_once()

    @mock.patch('builtins.open', new_callable=mock_open, create=True)
    @mock.patch('os.makedirs')
    def test_selection_color(self, makedirs, fopen):
        args = get_args(["--delay", "5", "--select-color", "#00000000", "-s"])
        main(app=self.app, args=args)
        self.app.set_select_color.assert_called_with("#00000000")
        self.app.screenshot_selected.assert_called_with(
            delay=5, capture_cursor=False, cursor_name=None, overwrite=True)

    @mock.patch('builtins.open', new_callable=mock_open, create=True)
    @mock.patch('os.makedirs')
    def test_selection_weight(self, makedirs, fopen):
        args = get_args(['--select-border-weight', '20', '--select-color', '', '-s'])
        main(app=self.app, args=args)
        self.app.set_select_border_weight.assert_called_with(20)
        self.app.screenshot_selected.assert_called()

    @mock.patch('src.gscreenshot.screenshot.actions.copy.subprocess.Popen')
    @mock.patch('src.gscreenshot.screenshot.actions.xdg_open.subprocess.run')
    def test_clip_and_open(self, copy, xdg_open):
        args = get_args(["--clip", "--open"])
        main(app=self.app, args=args)

        self.app.screenshot_full_display.assert_called()
        copy.assert_called_once()
        xdg_open.assert_called_once()

    @mock.patch('builtins.open', new_callable=mock_open, create=True)
    @mock.patch('src.gscreenshot.screenshot.actions.xdg_open.subprocess.run')
    def test_save_filename(self, xdg_open, fopen):
        args = get_args(["--open", "--filename", "potato.png"])
        main(app=self.app, args=args)

        call_found = False
        for c in fopen.call_args_list:
            if c == call("potato.png", "wb"):
                call_found = True
                break

        self.app.screenshot_full_display.assert_called()
        xdg_open.assert_called_once()
        self.assertTrue(call_found, "file write call was not found")
