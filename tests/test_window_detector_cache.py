
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock dependencies before importing the module under test
sys.modules['win32gui'] = MagicMock()
sys.modules['win32process'] = MagicMock()
sys.modules['psutil'] = MagicMock()

# Import the class to test
# We need to make sure we import it correctly
from phoenix.core.window_detector import WindowDetector

class TestWindowDetectorCache(unittest.TestCase):
    def setUp(self):
        # Reset mocks
        sys.modules['win32gui'].reset_mock()
        sys.modules['win32process'].reset_mock()
        sys.modules['psutil'].reset_mock()

        # Setup specific mock behaviors
        self.mock_win32gui = sys.modules['win32gui']
        self.mock_win32process = sys.modules['win32process']
        self.mock_psutil = sys.modules['psutil']

        # Always return True for WINDOWS_AVAILABLE inside the module if we could manipulate it,
        # but since we mocked imports before import, it should be True.
        # However, we need to check if WindowDetector actually sees them.

    def test_cache_behavior(self):
        detector = WindowDetector()

        # Scenario 1: Window A (PID 100) -> Window B (PID 200) -> Window A (PID 100)

        # 1. Window A
        self.mock_win32gui.GetForegroundWindow.return_value = 12345 # Handle A
        self.mock_win32gui.GetWindowText.return_value = "Title A"
        self.mock_win32process.GetWindowThreadProcessId.return_value = (0, 100) # PID 100

        process_mock_100 = MagicMock()
        process_mock_100.name.return_value = "AppA.exe"
        self.mock_psutil.Process.side_effect = lambda pid: process_mock_100 if pid == 100 else process_mock_200

        app, title = detector.get_active_window()
        print(f"Call 1: {app}, {title}")

        # Verify psutil called for PID 100
        # self.mock_psutil.Process.assert_called_with(100)
        # We can count calls to .name()
        self.assertEqual(process_mock_100.name.call_count, 1)

        # 2. Window B
        self.mock_win32gui.GetForegroundWindow.return_value = 67890 # Handle B
        self.mock_win32gui.GetWindowText.return_value = "Title B"
        self.mock_win32process.GetWindowThreadProcessId.return_value = (0, 200) # PID 200

        process_mock_200 = MagicMock()
        process_mock_200.name.return_value = "AppB.exe"

        app, title = detector.get_active_window()
        print(f"Call 2: {app}, {title}")

        self.assertEqual(process_mock_200.name.call_count, 1)

        # 3. Window A again (Different HWND potentially, or same HWND but different time)
        # Even if same HWND, if we didn't cache by PID, we might re-fetch if we cleared cache?
        # The current implementation caches by Last HWND.
        # If we switch back to A (Handle A), it should hit the `_last_hwnd` cache if it wasn't overwritten.
        # BUT `_last_hwnd` is overwritten by Call 2 (Handle B).
        # So when we go back to Handle A, it's a cache MISS in current implementation.

        self.mock_win32gui.GetForegroundWindow.return_value = 12345 # Handle A again
        self.mock_win32gui.GetWindowText.return_value = "Title A"
        self.mock_win32process.GetWindowThreadProcessId.return_value = (0, 100) # PID 100

        app, title = detector.get_active_window()
        print(f"Call 3: {app}, {title}")

        # With optimization, this should NOT trigger another psutil call because PID 100 is in cache
        print(f"PID 100 calls: {process_mock_100.name.call_count}")
        self.assertEqual(process_mock_100.name.call_count, 1)

        # 4. Window C (Same PID as A, e.g. another Chrome tab)
        self.mock_win32gui.GetForegroundWindow.return_value = 11111 # Handle C
        self.mock_win32gui.GetWindowText.return_value = "Title C"
        self.mock_win32process.GetWindowThreadProcessId.return_value = (0, 100) # PID 100

        app, title = detector.get_active_window()
        print(f"Call 4: {app}, {title}")

        # With optimization, Handle C != Handle A, but PID 100 is in cache.
        # So it's a hit.
        # Total calls for PID 100 should still be 1.
        print(f"PID 100 calls after Call 4: {process_mock_100.name.call_count}")
        self.assertEqual(process_mock_100.name.call_count, 1)

if __name__ == '__main__':
    unittest.main()
