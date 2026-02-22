import sys
import unittest
from unittest.mock import MagicMock
import os
import numpy as np
from PIL import Image

# Mock winreg before importing anything else
sys.modules['winreg'] = MagicMock()
sys.modules['winshell'] = MagicMock()

# Also mock mss because it might try to load platform specific things
sys.modules['mss'] = MagicMock()

# Patch windows_settings to avoid actual registry calls
sys.modules['windows_settings'] = MagicMock()
sys.modules['windows_settings'].settings_manager = MagicMock()

# Ensure we can import from phoenix root
sys.path.append(os.getcwd())

from phoenix.core.activity_detector import ActivityDetector

class TestActivityDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ActivityDetector(similarity_threshold=0.95)

    def test_identical_images(self):
        # Create two identical images
        # Use RGB tuple instead of color string for compatibility
        img1 = Image.new('RGB', (100, 100), color=(255, 255, 255))
        img2 = Image.new('RGB', (100, 100), color=(255, 255, 255))

        # First call sets baseline, returns True (initially)
        self.assertTrue(self.detector.has_significant_change(img1))

        # Second call should find no change (high similarity)
        # 1.0 similarity > 0.95 threshold -> No change
        self.assertFalse(self.detector.has_significant_change(img2))

    def test_different_images(self):
        img1 = Image.new('RGB', (100, 100), color=(255, 255, 255))
        # Use different color (black)
        img2 = Image.new('RGB', (100, 100), color=(0, 0, 0))

        # First call baseline
        self.assertTrue(self.detector.has_significant_change(img1))

        # Second call should find change
        # Similarity approx 0 < 0.95 -> Change
        self.assertTrue(self.detector.has_significant_change(img2))

    def test_mse_calculation_logic(self):
        """Direct test of _calculate_similarity_mse to verify the math."""
        # Create float32 arrays
        h, w = 10, 10
        # Identical arrays
        arr1 = np.ones((h, w), dtype=np.float32) * 100
        arr2 = np.ones((h, w), dtype=np.float32) * 100

        # Note: _calculate_similarity_mse expects float32
        sim = self.detector._calculate_similarity_mse(arr1, arr2)
        self.assertEqual(sim, 1.0)

        # Max difference (0 vs 255)
        arr3 = np.zeros((h, w), dtype=np.float32)
        arr4 = np.ones((h, w), dtype=np.float32) * 255

        sim = self.detector._calculate_similarity_mse(arr3, arr4)
        # Should be near 0.0
        self.assertAlmostEqual(sim, 0.0, places=4)

    def test_mss_object_support(self):
        """Test the fast path for mss-like screenshot objects."""
        # Mock mss.tools.ScreenShot (duck typing)
        class MockScreenShot:
            def __init__(self, bgra, size):
                self.bgra = bgra
                self.size = size
                self.width, self.height = size

        width, height = 320, 240
        # White image (BGRA: 255, 255, 255, 255)
        # 4 bytes per pixel * width * height
        white_pixel = b'\xff\xff\xff\xff'
        bgra_white = white_pixel * (width * height)

        # Black image (BGRA: 0, 0, 0, 255)
        black_pixel = b'\x00\x00\x00\xff'
        bgra_black = black_pixel * (width * height)

        sct_white = MockScreenShot(bgra_white, (width, height))
        sct_white2 = MockScreenShot(bgra_white, (width, height))
        sct_black = MockScreenShot(bgra_black, (width, height))

        # 1. Baseline (white) -> True
        self.assertTrue(self.detector.has_significant_change(sct_white))

        # 2. Compare identical (white) -> False
        self.assertFalse(self.detector.has_significant_change(sct_white2))

        # 3. Compare different (black) -> True
        self.assertTrue(self.detector.has_significant_change(sct_black))

if __name__ == '__main__':
    unittest.main()
