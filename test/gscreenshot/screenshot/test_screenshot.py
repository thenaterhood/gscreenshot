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

    def test_add_fake_cursor(self):
        original_img = Image.open(
                resource_filename('gscreenshot.resources.pixmaps', 'gscreenshot.png')
            )

        cursor_img = Image.open(
                    resource_filename(
                        'gscreenshot.resources.pixmaps', 'cursor-adwaita.png'
                    )
                )

        expected_img = Image.open("../test/gscreenshot/screenshot/cursor_overlay_expected.png").convert("RGB")

        self.screenshot = Screenshot(original_img)

        self.assertIsNotNone(self.screenshot.get_image())

        self.screenshot.add_effect(
            StampEffect(cursor_img, (20, 40))
        )
        self.assertLess(
            len(set(ImageChops.difference(expected_img, self.screenshot.get_image()).getdata())),  # type: ignore
            2,
            "cursor was not stamped onto the test image correctly")
