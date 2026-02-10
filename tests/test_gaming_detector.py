
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock modules that might not be available or cause issues
sys.modules['win32gui'] = MagicMock()
sys.modules['win32process'] = MagicMock()
sys.modules['win32con'] = MagicMock()
sys.modules['win32api'] = MagicMock()
sys.modules['pywintypes'] = MagicMock()
sys.modules['winreg'] = MagicMock()
sys.modules['winshell'] = MagicMock()

# Mock config
mock_config_module = MagicMock()
mock_config_module.config.GAMING_PROCESSES = ['game.exe', 'dota2.exe']
sys.modules['config'] = mock_config_module

# Now install psutil if missing, or mock it
try:
    import psutil
except ImportError:
    psutil = MagicMock()
    sys.modules['psutil'] = psutil

from phoenix.core.gaming_detector import GamingDetector

class TestGamingDetector(unittest.TestCase):
    def setUp(self):
        # We mocked config at module level, but let's ensure instance uses it
        self.detector = GamingDetector()
        # Manually ensure list is set
        self.detector.gaming_processes = ['game.exe', 'dota2.exe']

    def test_is_gaming_fast_path_positive(self):
        """Test is_gaming with active_process_name matching a game."""
        # Should return True immediately without iterating processes
        with patch('psutil.process_iter') as mock_iter:
            result = self.detector.is_gaming(active_process_name='dota2.exe')
            self.assertTrue(result)
            mock_iter.assert_not_called()

    def test_is_gaming_fast_path_negative(self):
        """Test is_gaming with active_process_name NOT matching a game."""
        # Should return False immediately without iterating processes
        with patch('psutil.process_iter') as mock_iter:
            result = self.detector.is_gaming(active_process_name='chrome.exe')
            self.assertFalse(result)
            mock_iter.assert_not_called()

    def test_is_gaming_slow_path_positive(self):
        """Test is_gaming WITHOUT active_process_name (backward compat) - Game Running."""
        # Should iterate processes
        with patch('psutil.process_iter') as mock_iter:
            # Setup mock process
            mock_proc = MagicMock()
            mock_proc.info = {'name': 'dota2.exe'}
            # Iter should yield this process
            mock_iter.return_value = [mock_proc]

            result = self.detector.is_gaming(active_process_name=None)
            self.assertTrue(result)
            mock_iter.assert_called_once()

    def test_is_gaming_slow_path_negative(self):
        """Test is_gaming WITHOUT active_process_name (backward compat) - No Game."""
        # Should iterate processes
        with patch('psutil.process_iter') as mock_iter:
            # Setup mock process
            mock_proc = MagicMock()
            mock_proc.info = {'name': 'notepad.exe'}
            mock_iter.return_value = [mock_proc]

            result = self.detector.is_gaming(active_process_name=None)
            self.assertFalse(result)
            mock_iter.assert_called_once()

    def test_get_running_game_fast_path(self):
        result = self.detector.get_running_game(active_process_name='dota2.exe')
        self.assertEqual(result, 'dota2.exe')

        result = self.detector.get_running_game(active_process_name='chrome.exe')
        self.assertEqual(result, '')

if __name__ == '__main__':
    unittest.main()
