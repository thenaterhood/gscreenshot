import unittest
from unittest.mock import Mock
import mock

from pkg_resources import resource_filename
from PIL import Image
from PIL import ImageChops
from src.gscreenshot.screenshooter import Screenshooter
from src.gscreenshot.screenshot import Screenshot
from src.gscreenshot.screenshot.effects.stamp import StampEffect


class ScreenshotTest(unittest.TestCase):

    def setUp(self):
        self.image = Mock()
        self.screenshot = Screenshot(self.image)

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

        expected_img = Image.open("../test/gscreenshot/screenshot/cursor_overlay_expected.png")

        self.screenshot = Screenshot(original_img)

        self.assertIsNotNone(self.screenshot.get_image())

        self.screenshot.add_effect(
            StampEffect(cursor_img, (20, 40))
        )
        self.assertLess(
            len(set(ImageChops.difference(expected_img, self.screenshot.get_image()).getdata())),  # type: ignore
            100,
            "cursor was not stamped onto the test image correctly")
