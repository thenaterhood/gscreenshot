import os
import mock
import unittest

from unittest.mock import Mock

from pkg_resources import resource_filename
from PIL import Image
from PIL import ImageChops
from src.gscreenshot.screenshooter import Screenshooter


class BaseScreenshooter(Screenshooter):

    def __init__(self):
        super().__init__()

    def grab_fullscreen(self, delay=0, capture_cursor=False):
        self._image = Mock()
        self._image.size = (20, 30)
        self._image.copy.return_value = self._image

    def grab_selection(self, delay=0, capture_cursor=False):
        self._image = Mock()
        self._image.size = (20, 30)
        self._image.copy.return_value = self._image

    def grab_window(self, delay=0, capture_cursor=False):
        self._image = Mock()
        self._image.size = (20, 30)
        self._image.copy.return_value = self._image

    def set_image(self, image):
        self._image = image

    @staticmethod
    def can_run():
        return True


class ScreenshooterTest(unittest.TestCase):

    def setUp(self):
        self.screenshooter = BaseScreenshooter()
        self.screenshooter.selector = Mock()

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

        self.assertLess(
            len(set(ImageChops.difference(expected_img, self.screenshooter.image).getdata())),
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

        self.assertLess(
            len(set(ImageChops.difference(original_img, self.screenshooter.image).getdata())),
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

        self.assertLess(
            len(set(ImageChops.difference(original_img, self.screenshooter.image).getdata())),
            100,
            "original and actual image should not differ")
