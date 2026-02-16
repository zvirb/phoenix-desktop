import sys
import unittest
from unittest.mock import MagicMock
import os

# Mock winreg before importing anything else
sys.modules['winreg'] = MagicMock()
sys.modules['winshell'] = MagicMock()

# Also mock mss because it might try to load platform specific things
sys.modules['mss'] = MagicMock()

# Ensure we can import from phoenix root
sys.path.append(os.getcwd())

from phoenix.core.activity_detector import ActivityDetector
import numpy as np
from PIL import Image

class TestActivityDetector(unittest.TestCase):
    def setUp(self):
        self.detector = ActivityDetector(similarity_threshold=0.95)

    def test_identical_images(self):
        # Create two identical images
        img1 = Image.new('RGB', (100, 100), color='white')
        img2 = Image.new('RGB', (100, 100), color='white')

        # First call sets baseline, returns True (initially)
        self.assertTrue(self.detector.has_significant_change(img1))

        # Second call should find no change (high similarity)
        self.assertFalse(self.detector.has_significant_change(img2))

    def test_different_images(self):
        img1 = Image.new('RGB', (100, 100), color='white')
        img2 = Image.new('RGB', (100, 100), color='black')

        self.detector.has_significant_change(img1)
        self.assertTrue(self.detector.has_significant_change(img2))

    def test_mse_calculation_logic(self):
        # Direct test of _calculate_similarity_mse to verify the math
        # Create random float32 arrays
        arr1 = np.ones((10, 10), dtype=np.float32) * 100
        arr2 = np.ones((10, 10), dtype=np.float32) * 100

        sim = self.detector._calculate_similarity_mse(arr1, arr2)
        self.assertEqual(sim, 1.0)

        # Max difference
        arr3 = np.zeros((10, 10), dtype=np.float32)
        arr4 = np.ones((10, 10), dtype=np.float32) * 255

        sim = self.detector._calculate_similarity_mse(arr3, arr4)
        self.assertAlmostEqual(sim, 0.0, places=4)

    def test_mss_object_support(self):
        """Test the fast path for mss-like screenshot objects."""
        # Mock mss.tools.ScreenShot
        class MockScreenShot:
            def __init__(self, bgra, size):
                self.bgra = bgra
                self.size = size
                self.width, self.height = size

        width, height = 320, 240
        # White image (BGRA: 255, 255, 255, 255)
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
