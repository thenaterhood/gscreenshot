import unittest
from unittest.mock import Mock
import mock

from PIL import Image
from PIL import ImageChops
from gscreenshot.selector import SelectionCancelled, SelectionParseError
from src.gscreenshot.selector import RegionSelector\


class BaseSelector(RegionSelector):

    def __init__(self):
        RegionSelector.__init__(self)
        self.called = None
        self.mock_output = [""]

    @staticmethod
    def can_run():
        return True

    def region_select(self):
        return self._parse_selection_output(self.mock_output)


class SelectorTest(unittest.TestCase):

    def setUp(self):
        self.selector = BaseSelector()

    def test_parse_output_oneline(self):

        self.selector.mock_output = ["X=1,Y=2,W=3,H=4"]
        region = self.selector.region_select()
        self.assertEqual((1, 2, 4, 6), region)

    def test_parse_output_oneline_extra_lines(self):

        self.selector.mock_output = ["", "X=1,Y=2,W=3,H=4", ""]
        region = self.selector.region_select()
        self.assertEqual((1, 2, 4, 6), region)

    def test_parse_output_online_extra_garbage(self):

        self.selector.mock_output = ["ASDFSDFSDF", "X=1,Y=2,W=3,H=4", "45"]
        region = self.selector.region_select()
        self.assertEqual((1, 2, 4, 6), region)

    def test_parse_output_multiline(self):

        self.selector.mock_output = ["X=1", "Y=2", "W=3" ,"H=4"]
        region = self.selector.region_select()
        self.assertEqual((1, 2, 4, 6), region)
