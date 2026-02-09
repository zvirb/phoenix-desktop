import time
import logging
import mss
from io import BytesIO
from PIL import Image

from PyQt6.QtCore import QThread, pyqtSignal, QObject

from phoenix.core.activity_detector import ActivityDetector
from phoenix.core.window_detector import WindowDetector
from phoenix.core.gaming_detector import GamingDetector
from config import config

logger = logging.getLogger(__name__)

class ContextWorker(QThread):
    """
    Background worker for capturing screen context and window state.
    Runs in a separate thread to avoid freezing the UI.
    """
    # Signals
    screenshot_taken = pyqtSignal(bytes)  # Emits raw JPEG bytes
    activity_detected = pyqtSignal(dict)  # Emits metadata (app, title, etc)
    status_changed = pyqtSignal(dict)     # Emits {idle: bool, gaming: bool}

    def __init__(self):
        super().__init__()
        self.running = True
        self.window_detector = WindowDetector()
        self.activity_detector = ActivityDetector()
        self.gaming_detector = GamingDetector()
        
        self.last_capture_time = 0
        self.capture_interval = 20  # Default 20s
        self.idle_threshold = 60    # Default 60s
        self.is_idle_state = False
        self.is_gaming_state = False

    def run(self):
        logger.info("ContextWorker started")
        while self.running:
            try:
                # 1. Check Window State
                app_name, window_title = self.window_detector.get_active_window()
                is_idle = self.window_detector.is_idle(self.idle_threshold)
                # Pass app_name to optimize gaming check (skips full process scan)
                is_gaming = self.gaming_detector.is_gaming(app_name)

                # Emit Status Change if needed
                if is_idle != self.is_idle_state or is_gaming != self.is_gaming_state:
                    self.is_idle_state = is_idle
                    self.is_gaming_state = is_gaming
                    self.status_changed.emit({
                        "idle": is_idle,
                        "gaming": is_gaming
                    })

                # 2. Activity / Screenshot (if not idle and not gaming)
                # Note: We might still want to track gaming, but usually we pause screenshots
                if not is_idle and not is_gaming:
                    current_time = time.time()
                    if current_time - self.last_capture_time >= self.capture_interval:
                        self._process_screenshot(app_name, window_title)
                        self.last_capture_time = current_time

            except Exception as e:
                logger.error(f"Error in ContextWorker loop: {e}")
            
            # Sleep to prevent CPU spinning
            time.sleep(1)

    def _process_screenshot(self, app_name, window_title):
        try:
            with mss.mss() as sct:
                # Get focused monitor
                monitor_idx = self.window_detector.get_focused_monitor_index(sct.monitors)
                monitor = sct.monitors[monitor_idx]
                
                # Capture
                sct_img = sct.grab(monitor)
                img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                # Resize (Standardize)
                max_width = 1024
                img.thumbnail((max_width, max_width))
                
                # Check for significant change (MSE)
                if self.activity_detector.has_significant_change(img):
                    # Convert to JPEG
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=70)
                    jpeg_bytes = buffer.getvalue()
                    
                    # Emit signals
                    self.screenshot_taken.emit(jpeg_bytes)
                    
                    self.activity_detected.emit({
                        "type": "screen_capture",
                        "app_name": app_name,
                        "window_title": window_title,
                        "timestamp": time.time()
                    })
                    logger.debug(f"Significant change detected in {app_name}")
                
        except Exception as e:
            logger.error(f"Screenshot processing failed: {e}")

    def stop(self):
        self.running = False
        self.wait()
