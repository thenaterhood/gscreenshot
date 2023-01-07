import unittest
from unittest.mock import Mock
import mock

from pkg_resources import resource_filename
from PIL import Image
from PIL import ImageChops
from gscreenshot.selector import SelectionCancelled, SelectionParseError
from src.gscreenshot.screenshooter import Screenshooter
from src.gscreenshot.screenshot import Screenshot


class BaseScreenshooter(Screenshooter):

    def __init__(self):
        Screenshooter.__init__(self)
        self.called = None

    def grab_fullscreen(self, delay=0, capture_cursor=False):
        self._image = Mock()
        self._image.size = (20, 30)
        self._image.copy.return_value = self._image
        self._screenshot = Mock()
        self._screenshot.get_image.return_value = self._image
        self.called = "fullscreen"

    def grab_selection(self, delay=0, capture_cursor=False):
        self._image = Mock()
        self._image.size = (20, 30)
        self._image.copy.return_value = self._image
        self._screenshot = Mock()
        self._screenshot.get_image.return_value = self._image
        self.called = "selection"

    def grab_window(self, delay=0, capture_cursor=False):
        self._image = Mock()
        self._image.size = (20, 30)
        self._image.copy.return_value = self._image
        self._screenshot = Mock()
        self._screenshot.get_image.return_value = self._image
        self.called = "window"

    def set_image(self, image):
        self._image = image
        self._screenshot = Mock()
        self._screenshot.get_image.return_value = self._image

    @staticmethod
    def can_run():
        return True


class ScreenshooterTest(unittest.TestCase):

    def setUp(self):
        self.screenshooter = BaseScreenshooter()
        self.screenshooter._selector = Mock()
        self.screenshooter._selector.get_capabilities.return_value = {}

    def test_grab_fullscreen(self):
        self.assertIsNone(self.screenshooter.image)
        self.screenshooter.grab_fullscreen_()
        self.assertIsNotNone(self.screenshooter.image)

    @mock.patch('src.gscreenshot.screenshooter.PIL')
    @mock.patch('src.gscreenshot.screenshooter.display')
    def test_grab_fullscreen_capture_cursor(self, mock_xlib, mock_pil):
        mock_xlib.Display().screen().root.query_pointer()._data = {'root_x': 20, 'root_y': 40}
        mock_cursor = Mock()
        mock_cursor.size = (20, 30)
        self.screenshooter.grab_fullscreen_(capture_cursor=True, use_cursor=mock_cursor)
        self.assertIsNotNone(self.screenshooter.image)
        self.screenshooter.image.paste.assert_called_once()

    def test_grab_selection(self):
        self.assertIsNone(self.screenshooter.image)
        self.screenshooter.grab_selection_()
        self.assertIsNotNone(self.screenshooter.image)

    @mock.patch('src.gscreenshot.screenshooter.PIL')
    @mock.patch('src.gscreenshot.screenshooter.display')
    def test_grab_selection_capture_cursor(self, mock_xlib, mock_pil):
        mock_xlib.Display().screen().root.query_pointer()._data = {'root_x': 20, 'root_y': 40}
        mock_cursor = Mock()
        mock_cursor.size = (20, 30)
        self.screenshooter.grab_selection_(capture_cursor=True, use_cursor=mock_cursor)
        self.assertIsNotNone(self.screenshooter.image)
        # Stamping the cursor onto a selected area is not trivial, so we currently
        # will not do cursor capture with a strategy not native to a screenshot
        # utility.
        self.screenshooter.image.paste.assert_not_called()

    def test_grab_window(self):
        self.assertIsNone(self.screenshooter.image)
        self.screenshooter.grab_window_()
        self.assertIsNotNone(self.screenshooter.image)

    @mock.patch('src.gscreenshot.screenshooter.PIL')
    @mock.patch('src.gscreenshot.screenshooter.display')
    def test_grab_window_capture_cursor(self, mock_xlib, mock_pil):
        mock_xlib.Display().screen().root.query_pointer()._data = {'root_x': 20, 'root_y': 40}
        mock_cursor = Mock()
        mock_cursor.size = (20, 30)
        self.screenshooter.grab_window_(capture_cursor=True, use_cursor=mock_cursor)
        self.assertIsNotNone(self.screenshooter.image)
        self.screenshooter.image.paste.assert_called_once()

    @mock.patch('src.gscreenshot.screenshooter.display')
    def test_add_fake_cursor(self, mock_xlib):
        mock_xlib.Display().screen().root.query_pointer()._data = {'root_x': 20, 'root_y': 40}

        original_img = Image.open(
                resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png')
            )

        cursor_img = Image.open(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'cursor-adwaita.png'
                    )
                )

        expected_img = Image.open("../test/gscreenshot/screenshooter/cursor_overlay_expected.png")

        self.screenshooter.set_image(original_img)
        self.screenshooter.add_fake_cursor(cursor_img)

        self.assertIsNotNone(self.screenshooter.image)
        self.assertLess(
            len(set(ImageChops.difference(expected_img, self.screenshooter.image).getdata())),  # type: ignore
            100,
            "cursor was not stamped onto the test image correctly")

    @mock.patch('src.gscreenshot.screenshooter.display')
    def test_add_fake_cursor_xlib_missing(self, mock_xlib):
        mock_xlib = None
        original_img = Image.open(
                resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png')
            )

        cursor_img = Image.open(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'cursor-adwaita.png'
                    )
                )

        self.screenshooter.set_image(original_img)
        self.screenshooter.add_fake_cursor(cursor_img)

        self.assertIsNotNone(self.screenshooter.image)
        self.assertLess(
            len(set(ImageChops.difference(original_img, self.screenshooter.image).getdata())),  # type: ignore
            100,
            "original and actual image should not differ")

    @mock.patch('src.gscreenshot.screenshooter.display')
    def test_add_fake_cursor_xlib_bad_data(self, mock_xlib):
        mock_xlib.Display().screen().root.query_pointer()._data = {'root_x': 20}

        original_img = Image.open(
                resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png')
            )

        cursor_img = Image.open(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'cursor-adwaita.png'
                    )
                )

        self.screenshooter.set_image(original_img)
        self.screenshooter.add_fake_cursor(cursor_img)

        self.assertIsNotNone(self.screenshooter.image)
        self.assertLess(
            len(set(ImageChops.difference(original_img, self.screenshooter.image).getdata())),  # type: ignore
            100,
            "original and actual image should not differ")

    def test_get_capabilities(self):
        self.assertIsInstance(self.screenshooter.get_capabilities_(), dict)

    @mock.patch('src.gscreenshot.screenshooter.subprocess.check_output')
    @mock.patch('src.gscreenshot.screenshooter.PIL')
    @mock.patch('src.gscreenshot.screenshooter.os')
    def test_call_screenshooter_success(self, mock_os, mock_pil, mock_subprocess):
        success = self.screenshooter._call_screenshooter('potato', ['pancake'])
        mock_subprocess.assert_called_once_with(
            ['potato', 'pancake']
        )
        self.assertTrue(success)

    @mock.patch('src.gscreenshot.screenshooter.subprocess.check_output')
    @mock.patch('src.gscreenshot.screenshooter.PIL')
    @mock.patch('src.gscreenshot.screenshooter.os')
    def test_call_screenshooter_subprocess_no_params(self, mock_os, mock_pil, mock_subprocess):
        mock_subprocess.side_effect = OSError()
        success = self.screenshooter._call_screenshooter('potato')
        mock_subprocess.assert_called_once_with(
            ['potato']
        )
        self.assertFalse(success)

    @mock.patch('src.gscreenshot.screenshooter.subprocess.check_output')
    @mock.patch('src.gscreenshot.screenshooter.PIL')
    @mock.patch('src.gscreenshot.screenshooter.os')
    def test_call_screenshooter_subprocess_error(self, mock_os, mock_pil, mock_subprocess):
        mock_subprocess.side_effect = OSError()
        success = self.screenshooter._call_screenshooter('potato', ['pancake'])
        mock_subprocess.assert_called_once_with(
            ['potato', 'pancake']
        )
        self.assertFalse(success)

    def test_grab_selection_fallback(self):
        self.screenshooter._selector = None
        self.screenshooter.grab_selection_()
        self.assertIsNotNone(self.screenshooter.image)
        self.assertEqual("fullscreen", self.screenshooter.called)

    def test_grab_selection_cancelled(self):
        self.screenshooter._selector.region_select.side_effect = SelectionCancelled()
        self.screenshooter.grab_selection_()
        self.assertIsNotNone(self.screenshooter.image)
        self.assertEqual("fullscreen", self.screenshooter.called)

    def test_grab_selection_exec_error(self):
        self.screenshooter._selector.region_select.side_effect = OSError()
        self.screenshooter.grab_selection_()
        self.assertIsNotNone(self.screenshooter.image)
        self.assertEqual("fullscreen", self.screenshooter.called)

    def test_grab_selection_parse_error(self):
        self.screenshooter._selector.region_select.side_effect = SelectionParseError()
        self.screenshooter.grab_selection_()
        self.assertIsNotNone(self.screenshooter.image)
        self.assertEqual("fullscreen", self.screenshooter.called)
