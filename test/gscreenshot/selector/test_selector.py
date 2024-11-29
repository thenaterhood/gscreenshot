import unittest

import mock

from src.gscreenshot.selector import RegionSelector\


class BaseSelector(RegionSelector):

    def __init__(self):
        RegionSelector.__init__(self)
        self.called = None
        self.mock_output = [""]

    @staticmethod
    def can_run():
        return True

    def region_select(self, selection_color_rgba=None):
        return self._parse_selection_output(self.mock_output)


class SelectorTest(unittest.TestCase):

    def setUp(self):
        self.selector = BaseSelector()

    @mock.patch('src.gscreenshot.selector.region_selector.get_scaling_factor')
    def test_parse_output_oneline(self, get_scaling_factor):

        self.selector.mock_output = ["X=1,Y=2,W=3,H=4"]
        get_scaling_factor.return_value = 1
        region = self.selector.region_select()
        self.assertEqual((1, 2, 4, 6), region)

    @mock.patch('src.gscreenshot.selector.region_selector.get_scaling_factor')
    def test_parse_output_oneline_extra_lines(self, get_scaling_factor):

        self.selector.mock_output = ["", "X=1,Y=2,W=3,H=4", ""]
        get_scaling_factor.return_value = 1
        region = self.selector.region_select()
        self.assertEqual((1, 2, 4, 6), region)

    @mock.patch('src.gscreenshot.selector.region_selector.get_scaling_factor')
    def test_parse_output_online_extra_garbage(self, get_scaling_factor):

        self.selector.mock_output = ["ASDFSDFSDF", "X=1,Y=2,W=3,H=4", "45"]
        get_scaling_factor.return_value = 1
        region = self.selector.region_select()
        self.assertEqual((1, 2, 4, 6), region)

    @mock.patch('src.gscreenshot.selector.region_selector.get_scaling_factor')
    def test_parse_output_multiline(self, get_scaling_factor):

        self.selector.mock_output = ["X=1", "Y=2", "W=3" ,"H=4"]
        get_scaling_factor.return_value = 1
        region = self.selector.region_select()
        self.assertEqual((1, 2, 4, 6), region)
