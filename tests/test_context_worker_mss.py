
import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import importlib

# Add project root to path
sys.path.append(os.getcwd())

class TestContextWorkerMss(unittest.TestCase):
    def setUp(self):
        # Prepare mocks
        self.mock_mss_module = MagicMock()

        # Define the QThread mock so it can be inherited
        self.mock_qt_core = MagicMock()
        self.mock_qt_core.QThread = MagicMock
        self.mock_qt_core.pyqtSignal = MagicMock()
        self.mock_qt_core.QObject = MagicMock

        # Patch dict
        self.modules_patcher = patch.dict(sys.modules, {
            'mss': self.mock_mss_module,
            'phoenix.core.window_detector': MagicMock(),
            'phoenix.core.activity_detector': MagicMock(),
            'phoenix.core.gaming_detector': MagicMock(),
            'config': MagicMock(),
            'PyQt6': MagicMock(),
            'PyQt6.QtCore': self.mock_qt_core,
        })
        self.modules_patcher.start()

        # Now import the module under test
        # We need to make sure it's reloaded or imported fresh
        if 'phoenix.services.context_worker' in sys.modules:
            del sys.modules['phoenix.services.context_worker']

        import phoenix.services.context_worker
        self.context_worker_module = phoenix.services.context_worker

    def tearDown(self):
        self.modules_patcher.stop()

    def test_mss_reinitialization(self):
        """Verify that mss is initialized ONLY ONCE (optimized)."""
        ContextWorker = self.context_worker_module.ContextWorker
        worker = ContextWorker()

        # Setup mocks
        # Note: Since we mocked the imports, worker.window_detector is a MagicMock instance
        worker.window_detector.get_focused_monitor_index.return_value = 0

        mock_sct = MagicMock()
        # Since we removed the context manager usage, we set the return value directly
        self.mock_mss_module.mss.return_value = mock_sct

        mock_sct.monitors = [{'left': 0, 'top': 0, 'width': 100, 'height': 100}]

        # Mock the screenshot object returned by grab
        mock_screenshot = MagicMock()
        mock_screenshot.size = (100, 100)
        mock_screenshot.bgra = b'\x00' * (100 * 100 * 4)
        mock_sct.grab.return_value = mock_screenshot

        # We need to mock activity detector to return True so it proceeds
        worker.activity_detector.has_significant_change.return_value = True

        # Trigger capture twice
        worker._process_screenshot("app", "title")
        worker._process_screenshot("app", "title")

        # Assert mss() was called ONLY ONCE (optimized)
        print(f"mss.mss() call count: {self.mock_mss_module.mss.call_count}")
        self.assertEqual(self.mock_mss_module.mss.call_count, 1)

if __name__ == "__main__":
    unittest.main()
