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

    @mock.patch('src.gscreenshot.selector.region_selector.get_scaling_factor')
    def test_scaling_factor_200(self, get_scaling_factor):

        self.selector.mock_output = ["X=1,Y=2,W=3,H=4"]
        get_scaling_factor.return_value = 2
        region = self.selector.region_select()
        self.assertEqual((2, 4, 8, 12), region)

    def test_rgba_hex_to_tuple_valid_with_prefix(self):
        self.assertEqual(
            (1.0, 0.996078431372549, 0.9921568627450981, 1.0),
            self.selector._rgba_hex_to_decimals("#FFFEFDFF")
        )

    def test_rgba_hex_to_tuple_valid_no_prefix(self):
        self.assertEqual(
            (0.00392156862745098, 0.00784313725490196, 0.011764705882352941, 1.0),
            self.selector._rgba_hex_to_decimals("010203FF")
        )

    def test_rgba_hex_to_tuple_no_alpha(self):
        self.assertEqual(
            (0.00392156862745098, 0.00784313725490196, 0.011764705882352941),
            self.selector._rgba_hex_to_decimals("#010203")
        )

    def test_rgba_hex_to_alpha_bad_length(self):
        self.assertEqual(
            (0.8, 0.8, 0.8, 0.6),
            self.selector._rgba_hex_to_decimals("#FFFF")
        )

    def test_rgba_hex_to_alpha_invalid(self):
        self.assertEqual(
            (0.8, 0.8, 0.8, 0.6),
            self.selector._rgba_hex_to_decimals("#POTATO")
        )