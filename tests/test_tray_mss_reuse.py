
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Set up mocks for dependencies that might not be available or should be isolated
sys.modules['pystray'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageDraw'] = MagicMock()
sys.modules['plyer'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['windows_settings'] = MagicMock()
sys.modules['config'] = MagicMock()
sys.modules['phoenix.core.token_manager'] = MagicMock()
sys.modules['phoenix.core.api_client'] = MagicMock()
sys.modules['phoenix.core.window_detector'] = MagicMock()
sys.modules['phoenix.core.activity_detector'] = MagicMock()
sys.modules['phoenix.core.gaming_detector'] = MagicMock()
sys.modules['phoenix.core.inference_detector'] = MagicMock()

# Ensure current directory is in path to import tray_app
sys.path.append(os.getcwd())

# Need to mock mss before importing tray_app because it imports it at top level
mock_mss = MagicMock()
sys.modules['mss'] = mock_mss

import tray_app

class TestMssReuse(unittest.TestCase):

    def setUp(self):
        # Reset mocks completely
        mock_mss.reset_mock()
        mock_mss.mss.reset_mock(return_value=True, side_effect=True)
        # reset_mock(return_value=True, side_effect=True) is available in Python 3.6+
        # But explicitly clearing side_effect is safer
        mock_mss.mss.side_effect = None
        mock_mss.mss.return_value = MagicMock()

    @patch('tray_app.TokenManager')
    @patch('tray_app.WindowDetector')
    @patch('tray_app.ActivityDetector')
    @patch('tray_app.GamingDetector')
    @patch('tray_app.InferenceDetector')
    @patch('tray_app.settings_manager')
    def test_mss_reuse(self, mock_settings, mock_inf, mock_gaming, mock_activity, mock_window, mock_token):
        """Verify that mss is reused across capture calls."""
        # Setup mock mss instance behavior
        mock_sct_instance = MagicMock()
        mock_mss.mss.return_value = mock_sct_instance

        # Setup mock monitors
        mock_sct_instance.monitors = [{'left': 0, 'top': 0, 'width': 1920, 'height': 1080}]
        mock_sct_instance.grab.return_value = MagicMock() # Mock screenshot

        app = tray_app.PhoenixTrayApp()

        # Setup WindowDetector behavior
        app.window_detector.get_focused_monitor_index.return_value = 0

        # 1. First capture call
        # Should initialize mss
        result1 = app.capture_screen_raw()

        self.assertIsNotNone(result1)
        mock_mss.mss.assert_called_once()
        self.assertEqual(app.sct, mock_sct_instance)

        # 2. Second capture call
        # Should reuse mss (no new call to mss.mss())
        result2 = app.capture_screen_raw()

        self.assertIsNotNone(result2)
        mock_mss.mss.assert_called_once() # Count should still be 1

        # 3. Stop tracking
        # Should close mss
        app.running = True # Pretend it's running so stop_tracking proceeds
        app.stop_tracking()

        mock_sct_instance.close.assert_called_once()
        self.assertIsNone(app.sct)

    @patch('tray_app.TokenManager')
    @patch('tray_app.WindowDetector')
    @patch('tray_app.ActivityDetector')
    @patch('tray_app.GamingDetector')
    @patch('tray_app.InferenceDetector')
    @patch('tray_app.settings_manager')
    def test_mss_error_recovery(self, mock_settings, mock_inf, mock_gaming, mock_activity, mock_window, mock_token):
        """Verify that mss is reset on error."""
        # First instance fails
        mock_sct_fail = MagicMock()
        mock_sct_fail.monitors = [{'left': 0, 'top': 0, 'width': 1920, 'height': 1080}]
        mock_sct_fail.grab.side_effect = Exception("Display lost")

        # Second instance succeeds
        mock_sct_ok = MagicMock()
        mock_sct_ok.monitors = [{'left': 0, 'top': 0, 'width': 1920, 'height': 1080}]
        mock_sct_ok.grab.return_value = MagicMock()

        mock_mss.mss.side_effect = [mock_sct_fail, mock_sct_ok]

        app = tray_app.PhoenixTrayApp()
        app.window_detector.get_focused_monitor_index.return_value = 0

        # 1. Capture fails
        result = app.capture_screen_raw()

        self.assertIsNone(result)
        # Should have called mss once
        self.assertEqual(mock_mss.mss.call_count, 1)

        # Verify close was called and sct reset
        mock_sct_fail.close.assert_called_once()
        self.assertIsNone(app.sct)

        # 2. Retry capture (should re-init)
        result2 = app.capture_screen_raw()

        self.assertIsNotNone(result2)
        self.assertEqual(mock_mss.mss.call_count, 2)
        self.assertEqual(app.sct, mock_sct_ok)

if __name__ == '__main__':
    unittest.main()
