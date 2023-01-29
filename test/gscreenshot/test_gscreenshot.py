import mock
import subprocess
import unittest
from unittest.mock import Mock, mock_open, ANY
from src.gscreenshot import Gscreenshot


class GscreenshotTest(unittest.TestCase):

    def setUp(self):
        self.fake_screenshooter = Mock()
        self.fake_image = Mock()
        self.fake_screenshot = Mock()
        self.fake_screenshot.get_image.return_value = self.fake_image

        self.fake_screenshooter.image = self.fake_image
        self.fake_screenshooter.screenshot = self.fake_screenshot
        self.gscreenshot = Gscreenshot(self.fake_screenshooter)

    def test_screenshot_full_display_defaults(self):

        actual = self.gscreenshot.screenshot_full_display()

        self.fake_screenshooter.grab_fullscreen_.assert_called_once_with(
            0,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_full_display_delay(self):
        actual = self.gscreenshot.screenshot_full_display(5)

        self.fake_screenshooter.grab_fullscreen_.assert_called_once_with(
            5,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_full_display_cursor(self):
        actual = self.gscreenshot.screenshot_full_display(capture_cursor=True)

        self.fake_screenshooter.grab_fullscreen_.assert_called_once_with(
            0,
            True,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_selected_defaults(self):

        actual = self.gscreenshot.screenshot_selected()

        self.fake_screenshooter.grab_selection_.assert_called_once_with(
            0,
            False,
            use_cursor=None,
            region=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_selected_delay(self):
        actual = self.gscreenshot.screenshot_selected(5)

        self.fake_screenshooter.grab_selection_.assert_called_once_with(
            5,
            False,
            use_cursor=None,
            region=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_selection_cursor(self):
        actual = self.gscreenshot.screenshot_selected(capture_cursor=True)

        self.fake_screenshooter.grab_selection_.assert_called_once_with(
            0,
            True,
            use_cursor=None,
            region=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_window_defaults(self):

        actual = self.gscreenshot.screenshot_window()

        self.fake_screenshooter.grab_window_.assert_called_once_with(
            0,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_window_delay(self):
        actual = self.gscreenshot.screenshot_window(5)

        self.fake_screenshooter.grab_window_.assert_called_once_with(
            5,
            False,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_screenshot_window_cursor(self):
        actual = self.gscreenshot.screenshot_window(capture_cursor=True)

        self.fake_screenshooter.grab_window_.assert_called_once_with(
            0,
            True,
            use_cursor=None
        )

        self.assertEqual(self.fake_image, actual)

    def test_get_thumbnail(self):
        fake_thumbnail = Mock()
        fake_thumbnail.thumbnail.return_falue = fake_thumbnail
        self.fake_screenshot.get_preview.return_value = fake_thumbnail

        self.gscreenshot.screenshot_full_display()

        actual = self.gscreenshot.get_thumbnail(50, 50)
        self.assertEqual(fake_thumbnail, actual)

    def test_get_program_authors(self):
        self.assertIsInstance(self.gscreenshot.get_program_authors(), list)

    def test_get_program_description(self):
        self.assertIsInstance(self.gscreenshot.get_program_description(), str)

    def test_get_program_name(self):
        self.assertIsInstance(self.gscreenshot.get_program_name(), str)

    def test_get_program_license(self):
        self.assertIsInstance(self.gscreenshot.get_program_license(), str)

    def test_get_program_license_text(self):
        self.assertIsInstance(self.gscreenshot.get_program_license_text(), str)

    def test_get_program_website(self):
        self.assertIsInstance(self.gscreenshot.get_program_website(), str)

    def test_get_program_version(self):
        self.assertIsInstance(self.gscreenshot.get_program_version(), str)

    def test_get_supported_formats(self):
        self.assertIsInstance(self.gscreenshot.get_supported_formats(), list)

    def test_get_last_image(self):
        self.gscreenshot.screenshot_full_display()
        self.assertEqual(self.fake_image, self.gscreenshot.get_last_image())

    def test_get_screenshooter_name(self):
        self.assertEqual(
            self.fake_screenshooter.__class__.__name__,
            self.gscreenshot.get_screenshooter_name()
            )

        self.fake_screenshooter.__utilityname__ = "fake"
        self.assertEqual("fake", self.gscreenshot.get_screenshooter_name())

    @mock.patch("builtins.open", new_callable=mock_open, create=True)
    def test_save_last_image_success(self, mock_open):

        self.gscreenshot.screenshot_full_display()
        success = self.gscreenshot.save_last_image("potato.png")
        self.fake_image.save.assert_called_with(mock_open(), "PNG", exif=ANY)
        self.assertTrue(success)

    def test_save_last_image_bad_extension(self):

        self.gscreenshot.screenshot_full_display()
        success = self.gscreenshot.save_last_image("potato.nopenope")
        self.fake_image.save.assert_not_called()
        self.assertFalse(success)

    def test_save_last_image_ioerror(self):

        self.gscreenshot.screenshot_full_display()
        self.fake_image.save.side_effect = IOError("mocked IOError")
        success = self.gscreenshot.save_last_image("potato.png")
        self.assertFalse(success)

    @mock.patch('src.gscreenshot.subprocess')
    def test_show_screenshot_notification(self, mock_subprocess):

        self.gscreenshot.show_screenshot_notification()
        mock_subprocess.run.assert_called_once_with(
            ['notify-send', 'gscreenshot', mock.ANY, '--icon', 'gscreenshot'],
            check=True,
            timeout=2
        )

    @mock.patch('src.gscreenshot.subprocess.run')
    def test_show_screenshot_notification_error(self, mock_subprocess):
        mock_subprocess.run.side_effect = OSError("fake error")
        self.gscreenshot.show_screenshot_notification()
        mock_subprocess.assert_called_once_with(
            ['notify-send', 'gscreenshot', mock.ANY, '--icon', 'gscreenshot'],
            check=True,
            timeout=2
        )

    @mock.patch('src.gscreenshot.os')
    @mock.patch('src.gscreenshot.subprocess')
    def test_display_mismatch_warning_no_session_id(self, mock_subprocess, mock_os):
        mock_os.environ = {}
        self.gscreenshot.run_display_mismatch_warning()
        mock_subprocess.run.assert_not_called()

    @mock.patch('src.gscreenshot.os')
    @mock.patch('src.gscreenshot.subprocess')
    def test_display_mismatch_warning_no_session_type(self, mock_subprocess, mock_os):
        mock_os.environ = {'XDG_SESSION_ID': 0}
        self.gscreenshot.run_display_mismatch_warning()
        mock_subprocess.run.assert_called_once()

    @mock.patch('src.gscreenshot.os')
    @mock.patch('src.gscreenshot.subprocess')
    def test_display_mismatch_warning_show_notification(self, mock_subprocess, mock_os):
        mock_os.environ = {'XDG_SESSION_ID': 0, 'XDG_SESSION_TYPE': 'fake'}
        self.gscreenshot.run_display_mismatch_warning()
        # We have a dedicated test for interactions with notify-send, so don't
        # get into specifics here
        mock_subprocess.run.assert_called_once()

    @mock.patch('src.gscreenshot.os')
    @mock.patch('src.gscreenshot.subprocess')
    def test_display_mismatch_warning_no_show_notification(self, mock_subprocess, mock_os):
        mock_os.environ = {'XDG_SESSION_ID': 0, 'XDG_SESSION_TYPE': 'X11'}
        self.gscreenshot.run_display_mismatch_warning()
        mock_subprocess.run.assert_not_called()

    @mock.patch('src.gscreenshot.session_is_wayland')
    @mock.patch('src.gscreenshot.subprocess')
    def test_copy_to_clipboard_x11(self, mock_subprocess, mock_util):
        self.gscreenshot.screenshot_full_display()
        mock_util.return_value = False
        success = self.gscreenshot.copy_last_screenshot_to_clipboard()
        self.fake_image.save.assert_called_once()

        mock_subprocess.Popen.assert_called_once_with([
            'xclip',
            '-selection',
            'clipboard',
            '-t',
            'image/png'
            ],
            close_fds=True,
            stdin=mock_subprocess.PIPE,
            stdout=None,
            stderr=None
        )

        self.assertTrue(success)

    @mock.patch('src.gscreenshot.session_is_wayland')
    @mock.patch('src.gscreenshot.subprocess')
    def test_copy_to_clipboard_wayland(self, mock_subprocess, mock_util):
        mock_util.return_value = True
        self.gscreenshot.screenshot_full_display()
        success = self.gscreenshot.copy_last_screenshot_to_clipboard()
        self.fake_image.save.assert_called_once()

        mock_subprocess.Popen.assert_called_once_with([
            'wl-copy',
            '-t',
            'image/png'
            ],
            close_fds=True,
            stdin=mock_subprocess.PIPE,
            stdout=None,
            stderr=None
        )

        self.assertTrue(success)

    @mock.patch('src.gscreenshot.session_is_wayland')
    @mock.patch('src.gscreenshot.subprocess')
    def test_copy_to_clipboard_process_error(self, mock_subprocess, mock_util):
        mock_util.return_value = False
        mock_subprocess.Popen.side_effect = OSError
        # We can't mock the exception itself
        mock_subprocess.CalledProcessError = subprocess.CalledProcessError
        self.gscreenshot.screenshot_full_display()
        success = self.gscreenshot.copy_last_screenshot_to_clipboard()

        self.fake_image.save.assert_called_once()

        mock_subprocess.Popen.assert_called_once_with([
            'xclip',
            '-selection',
            'clipboard',
            '-t',
            'image/png'
            ],
            close_fds=True,
            stdin=mock_subprocess.PIPE,
            stdout=None,
            stderr=None
        )

        self.assertFalse(success)
