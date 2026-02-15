import sys
import unittest
from unittest.mock import MagicMock

# Mock dependencies before importing the module under test
sys.modules['win32gui'] = MagicMock()
sys.modules['win32process'] = MagicMock()
sys.modules['psutil'] = MagicMock()

import ctypes
# Mock ctypes for WINDOWS_AVAILABLE check
# We need to ensure ctypes.windll exists so WINDOWS_AVAILABLE becomes True
if not hasattr(ctypes, 'windll'):
    class MockWindll:
        pass
    ctypes.windll = MockWindll()
    ctypes.windll.user32 = MagicMock()
    ctypes.windll.kernel32 = MagicMock()

# Now import the module
from phoenix.core import window_detector

class TestCacheEviction(unittest.TestCase):
    def setUp(self):
        # Reset cache before each test
        window_detector._pid_cache.clear()

    def test_cache_clears_on_overflow(self):
        # Fill cache with 100 items (PIDs 0-99)
        for i in range(100):
            window_detector._pid_cache[i] = f"App{i}"

        self.assertEqual(len(window_detector._pid_cache), 100)

        # Setup mocks for the 101st call (PID 100)
        mock_win32process = sys.modules['win32process']
        # Return (thread_id, process_id)
        mock_win32process.GetWindowThreadProcessId.return_value = (0, 100)

        mock_psutil = sys.modules['psutil']
        process_mock = MagicMock()
        process_mock.name.return_value = "App100"
        mock_psutil.Process.return_value = process_mock

        # Call get_active_window
        detector = window_detector.WindowDetector()
        detector.get_active_window()

        # Fixed behavior: Cache removes oldest item if > 100 items are present.
        # Logic in code:
        # _pid_cache[pid] = app_name  (len becomes 101)
        # if len > 100: pop(oldest) (len becomes 100)

        print(f"Cache size after overflow: {len(window_detector._pid_cache)}")
        self.assertEqual(len(window_detector._pid_cache), 100)

        # Verify FIFO behavior
        # PID 0 was the first inserted, so it should be evicted
        self.assertNotIn(0, window_detector._pid_cache)

        # PID 1 was the second inserted, so it should remain
        self.assertIn(1, window_detector._pid_cache)

        # PID 100 was just inserted, so it should be present
        self.assertIn(100, window_detector._pid_cache)

if __name__ == '__main__':
    unittest.main()
