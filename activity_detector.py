"""
Activity detection using SSIM (Structural Similarity Index) to detect screen changes.
"""
import logging
from typing import Optional
import numpy as np
import cv2
from PIL import Image

from config import config

logger = logging.getLogger(__name__)


class ActivityDetector:
    """Detect significant changes in screen content."""
    
    def __init__(self, similarity_threshold: float = None):
        """
        Initialize activity detector.
        
        Args:
            similarity_threshold: Threshold for considering images similar (0-1)
                                Higher values mean images must be more similar
        """
        self.similarity_threshold = similarity_threshold or config.SIMILARITY_THRESHOLD
        self.previous_image: Optional[np.ndarray] = None
    
    def has_significant_change(self, current_image: Image.Image) -> bool:
        """
        Check if the current image has changed significantly from the previous one.
        
        Args:
            current_image: PIL Image to compare
            
        Returns:
            True if there is a significant change, False otherwise
        """
        # Convert PIL Image to numpy array
        current_array = np.array(current_image)
        
        # If this is the first image, consider it significant
        if self.previous_image is None:
            self.previous_image = current_array
            return True
        
        # Calculate similarity
        similarity = self._calculate_similarity(self.previous_image, current_array)
        
        logger.debug(f"Image similarity: {similarity:.4f} (threshold: {self.similarity_threshold})")
        
        # Significant change if similarity is below threshold
        has_change = similarity < self.similarity_threshold
        
        if has_change:
            self.previous_image = current_array
            logger.info(f"Significant change detected (similarity: {similarity:.4f})")
        
        return has_change
    
    def _calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate SSIM between two images.
        
        Args:
            img1: First image as numpy array
            img2: Second image as numpy array
            
        Returns:
            Similarity score (0-1, where 1 is identical)
        """
        try:
            # Ensure images are the same size
            if img1.shape != img2.shape:
                # Resize img2 to match img1
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert to grayscale for faster processing
            if len(img1.shape) == 3:
                gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
            else:
                gray1 = img1
            
            if len(img2.shape) == 3:
                gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
            else:
                gray2 = img2
            
            # Resize to a smaller size for faster comparison
            small_size = (320, 240)
            gray1_small = cv2.resize(gray1, small_size)
            gray2_small = cv2.resize(gray2, small_size)
            
            # Calculate SSIM
            from cv2 import quality
            score = quality.QualitySSIM_compute(gray1_small, gray2_small)[0]
            
            # Average the score across channels
            return float(np.mean(score))
            
        except Exception as e:
            logger.warning(f"SSIM calculation failed, using histogram comparison: {e}")
            # Fallback to histogram comparison
            return self._calculate_histogram_similarity(img1, img2)
    
    def _calculate_histogram_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Fallback similarity calculation using histogram comparison.
        
        Args:
            img1: First image as numpy array
            img2: Second image as numpy array
            
        Returns:
            Similarity score (0-1)
        """
        try:
            # Ensure images are the same size
            if img1.shape != img2.shape:
                img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
            
            # Convert to grayscale
            if len(img1.shape) == 3:
                gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
                gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
            else:
                gray1 = img1
                gray2 = img2
            
            # Calculate histograms
            hist1 = cv2.calcHist([gray1], [0], None, [256], [0, 256])
            hist2 = cv2.calcHist([gray2], [0], None, [256], [0, 256])
            
            # Normalize histograms
            hist1 = cv2.normalize(hist1, hist1).flatten()
            hist2 = cv2.normalize(hist2, hist2).flatten()
            
            # Calculate correlation
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            # Correlation ranges from -1 to 1, normalize to 0-1
            return (correlation + 1) / 2
            
        except Exception as e:
            logger.error(f"Histogram similarity calculation failed: {e}")
            # If all else fails, assume images are different
            return 0.0
    
    def reset(self) -> None:
        """Reset the detector (clear previous image)."""
        self.previous_image = None
        logger.debug("Activity detector reset")


if __name__ == "__main__":
    # Test the activity detector
    import mss
    from io import BytesIO
    
    logging.basicConfig(level=logging.DEBUG)
    
    detector = ActivityDetector()
    
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        
        # Capture first screenshot
        sct_img = sct.grab(monitor)
        img1 = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        print(f"First capture - Change detected: {detector.has_significant_change(img1)}")
        
        # Wait a bit
        import time
        time.sleep(2)
        
        # Capture second screenshot
        sct_img = sct.grab(monitor)
        img2 = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        print(f"Second capture - Change detected: {detector.has_significant_change(img2)}")
