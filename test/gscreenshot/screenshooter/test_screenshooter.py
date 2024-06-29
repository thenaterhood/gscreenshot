import unittest
from unittest.mock import Mock
import mock

from gscreenshot.selector.exceptions import SelectionCancelled, SelectionParseError
from src.gscreenshot.screenshooter import Screenshooter


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

    def test_grab_selection(self):
        self.assertIsNone(self.screenshooter.image)
        self.screenshooter.grab_selection_()
        self.assertIsNotNone(self.screenshooter.image)

    def test_grab_window(self):
        self.assertIsNone(self.screenshooter.image)
        self.screenshooter.grab_window_()
        self.assertIsNotNone(self.screenshooter.image)

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
