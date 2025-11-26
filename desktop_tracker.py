"""
Phoenix Desktop Tracker - Main Application
Captures screen context and usage data for the Phoenix Digital Homestead.
"""
import time
import logging
import sys
from io import BytesIO
from typing import Optional

import mss
from PIL import Image

from config import config
from api_client import create_client, APIClient
from token_manager import TokenManager
from window_detector import WindowDetector
from activity_detector import ActivityDetector
from gaming_detector import GamingDetector

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('phoenix_tracker.log')
    ]
)
logger = logging.getLogger(__name__)


class DesktopTracker:
    """Main desktop tracking application."""
    
    def __init__(self):
        """Initialize the tracker."""
        logger.info("=" * 60)
        logger.info("Phoenix Desktop Tracker Starting")
        logger.info("=" * 60)
        
        # Validate configuration
        try:
            config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            sys.exit(1)
        
        # Initialize components
        logger.info(f"Device ID: {config.DEVICE_ID}")
        logger.info(f"API URL: {config.PHOENIX_API_URL}")
        
        self.api_client: Optional[APIClient] = None
        self.window_detector = WindowDetector()
        self.activity_detector = ActivityDetector()
        self.gaming_detector = GamingDetector()
        
        # State tracking
        self.last_heartbeat = 0
        self.last_capture = 0
        self.running = True
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
    
    def initialize_api_client(self) -> bool:
        """
        Initialize and test the API client.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("Initializing API client...")
        
        self.api_client = create_client()
        if not self.api_client:
            logger.error("Failed to initialize API client")
            return False
        
        return True
    
    def capture_screen(self) -> Optional[bytes]:
        """
        Capture the current screen and return as JPEG bytes.
        
        Returns:
            JPEG image bytes, or None if capture failed
        """
        try:
            with mss.mss() as sct:
                # Grab the primary monitor
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes(
                    "RGB",
                    screenshot.size,
                    screenshot.bgra,
                    "raw",
                    "BGRX"
                )
                
                # Resize for efficiency (LLM doesn't need full resolution)
                img.thumbnail((config.MAX_IMAGE_WIDTH, config.MAX_IMAGE_WIDTH))
                
                # Convert to JPEG bytes
                img_byte_arr = BytesIO()
                img.save(img_byte_arr, format='JPEG', quality=config.JPEG_QUALITY)
                
                return img_byte_arr.getvalue()
                
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None
    
    def send_heartbeat(self) -> bool:
        """
        Send heartbeat with current app usage.
        
        Returns:
            True if successful
        """
        if not self.api_client:
            return False
        
        try:
            app_name, window_title = self.window_detector.get_active_window()
            is_idle = self.window_detector.is_idle()
            
            result = self.api_client.send_heartbeat(
                app_name=app_name,
                window_title=window_title,
                is_idle=is_idle
            )
            
            return result.get('status') != 'failed'
            
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            return False
    
    def process_screenshot(self) -> bool:
        """
        Capture and upload screenshot if there's significant activity.
        
        Returns:
            True if successful or skipped, False if failed
        """
        if not self.api_client:
            return False
        
        try:
            # Capture screen
            screenshot_bytes = self.capture_screen()
            if not screenshot_bytes:
                return False
            
            # Check for significant change
            img = Image.open(BytesIO(screenshot_bytes))
            if not self.activity_detector.has_significant_change(img):
                logger.debug("No significant change detected, skipping upload")
                return True
            
            # Upload screenshot
            result = self.api_client.upload_screenshot(screenshot_bytes)
            
            if result.get('status') == 'rate_limited':
                logger.warning(f"Rate limited, retry in {result.get('retry_after', 0):.0f}s")
                return True
            
            return result.get('status') in ['success', 'processed']
            
        except Exception as e:
            logger.error(f"Screenshot processing failed: {e}")
            return False
    
    def run_cycle(self) -> None:
        """Run one tracking cycle."""
        current_time = time.time()
        
        # Check for gaming mode
        if self.gaming_detector.is_gaming():
            game = self.gaming_detector.get_running_game()
            logger.info(f"🎮 Gaming detected ({game}), pausing tracker for 5 minutes")
            time.sleep(300)  # Wait 5 minutes
            return
        
        # Send heartbeat
        if current_time - self.last_heartbeat >= config.HEARTBEAT_INTERVAL:
            if self.send_heartbeat():
                self.last_heartbeat = current_time
                self.consecutive_errors = 0
            else:
                self.consecutive_errors += 1
        
        # Capture and upload screenshot
        if current_time - self.last_capture >= config.CAPTURE_INTERVAL:
            if self.process_screenshot():
                self.last_capture = current_time
                self.consecutive_errors = 0
            else:
                self.consecutive_errors += 1
        
        # Check for too many errors
        if self.consecutive_errors >= self.max_consecutive_errors:
            logger.error(f"Too many consecutive errors ({self.consecutive_errors}). Pausing for 5 minutes.")
            time.sleep(300)
            self.consecutive_errors = 0
    
    def run(self) -> None:
        """Main tracking loop."""
        # Initialize API client
        if not self.initialize_api_client():
            logger.error("Failed to initialize. Please check your configuration and token.")
            sys.exit(1)
        
        logger.info("✅ Tracker initialized successfully")
        logger.info(f"Capture interval: {config.CAPTURE_INTERVAL}s")
        logger.info(f"Heartbeat interval: {config.HEARTBEAT_INTERVAL}s")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        try:
            while self.running:
                self.run_cycle()
                time.sleep(5)  # Main loop interval
                
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
            self.running = False
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            raise
        
        finally:
            logger.info("Phoenix Desktop Tracker stopped")


def main():
    """Entry point for the application."""
    # Check if we're setting up token
    if len(sys.argv) > 1 and sys.argv[1] == '--setup-token':
        from token_manager import TokenManager
        manager = TokenManager()
        manager.setup_wizard()
        sys.exit(0)
    
    # Check if initial setup is needed
    from setup_wizard import needs_setup, run_wizard
    if needs_setup():
        print()
        print("=" * 70)
        print("  First-time setup required")
        print("=" * 70)
        print()
        if not run_wizard():
            print("\n❌ Setup was cancelled or failed. Please run 'python setup_wizard.py' to try again.")
            sys.exit(1)
        
        print("\n" + "=" * 70)
        print("  Setup complete! Starting tracker...")
        print("=" * 70 + "\n")
        
        # Reload config after setup
        from importlib import reload
        import config as config_module
        reload(config_module)
    
    # Run the tracker
    tracker = DesktopTracker()
    tracker.run()


if __name__ == "__main__":
    main()
