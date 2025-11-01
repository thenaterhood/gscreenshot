from importlib.resources import as_file, files
import unittest
from unittest.mock import Mock

from PIL import Image
from PIL import ImageChops
from src.gscreenshot.screenshot import Screenshot
from src.gscreenshot.screenshot.effects.stamp import StampEffect


class ScreenshotTest(unittest.TestCase):

    def setUp(self):
        self.image = Mock()
        self.screenshot = Screenshot(self.image)

    def test_add_fake_cursor(self):
        pixmaps_path = "gscreenshot.resources.pixmaps"
        with \
            as_file(files(pixmaps_path).joinpath('gscreenshot-grey.png')) as gscreenshot_png,\
            as_file(files(pixmaps_path).joinpath('cursor-adwaita.png')) as adwaita:

            original_img = Image.open(gscreenshot_png)
            cursor_img = Image.open(adwaita)

        expected_img = Image.open("test/gscreenshot/screenshot/cursor_overlay_expected.png").convert("RGB")

        self.screenshot = Screenshot(original_img)

        self.assertIsNotNone(self.screenshot.get_image())

        self.screenshot.add_effect(
            StampEffect(cursor_img, (20, 40))
        )
        self.assertLess(
            len(set(ImageChops.difference(expected_img, self.screenshot.get_image()).getdata())),  # type: ignore
            2,
            "cursor was not stamped onto the test image correctly")
