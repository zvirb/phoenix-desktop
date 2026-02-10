"""
Phoenix Desktop Tracker - System Tray Application
Modern Windows 11 system tray application with GUI settings.
"""
import sys
import os
import threading
import time
import logging
from pathlib import Path
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as Item
import tkinter as tk
from tkinter import messagebox
import subprocess
try:
    from plyer import notification
except ImportError:
    notification = None

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from windows_settings import settings_manager
# gui_settings is now a redirect, but we launch it via subprocess
from phoenix.core.token_manager import TokenManager
from phoenix.core.api_client import create_client
from phoenix.core.window_detector import WindowDetector
from phoenix.core.activity_detector import ActivityDetector
from phoenix.core.gaming_detector import GamingDetector
from phoenix.core.inference_detector import InferenceDetector
import mss
from io import BytesIO

# Setup logging
# Setup logging paths
app_data_dir = Path(os.path.expandvars('%LOCALAPPDATA%')) / "PhoenixTracker"
log_dir = app_data_dir / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "phoenix_tracker.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(str(log_file))
    ]
)
logger = logging.getLogger(__name__)


def create_icon_image():
    """Create a simple icon for the system tray."""
    # Create a 64x64 icon with a Phoenix-like design
    size = 64
    image = Image.new('RGB', (size, size), '#0078D4')  # Blue background
    draw = ImageDraw.Draw(image)
    
    # Draw a simple "P" for Phoenix
    draw.rectangle([10, 10, 54, 54], fill='#FFFFFF', outline='#0078D4')
    draw.rectangle([15, 15, 25, 49], fill='#0078D4')  # Vertical line
    draw.ellipse([20, 15, 45, 30], fill='#0078D4')  # Top curve
    
    return image


class PhoenixTrayApp:
    """System tray application for Phoenix Desktop Tracker."""
    
    def __init__(self):
        """Initialize the system tray application."""
        self.icon = None
        self.running = False
        self.tracker_thread = None
        self.token_manager = TokenManager()
        
        # Tracking state
        self.api_client = None
        self.window_detector = WindowDetector()
        self.activity_detector = ActivityDetector()
        self.gaming_detector = GamingDetector()
        self.inference_detector = InferenceDetector(
            ollama_host=f"http://localhost:{settings_manager.get_ollama_port()}"
        )
        
        self.last_heartbeat = 0
        self.last_capture = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # Check if first-time setup is needed
        if not settings_manager.is_configured():
            self.show_first_time_setup()
    
    def show_first_time_setup(self):
        """Show first-time setup wizard."""
        try:
            # Run the new Wizard using argument dispatch
            cmd = [sys.executable]
            if not getattr(sys, 'frozen', False):
                cmd.append(sys.argv[0])
            cmd.append("--wizard")
            subprocess.Popen(cmd)
        except Exception as e:
            logger.error(f"Failed to launch wizard: {e}")

    def notify(self, title, message):
        """Send a native toast notification."""
        if notification:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Phoenix Tracker",
                    app_icon=None, 
                    timeout=5
                )
            except Exception as e:
                logger.error(f"Notification failed: {e}")
        else:
            logger.warning(f"Notification skipped (plyer not found): {title} - {message}")
    
    def create_menu(self):
        """Create the system tray menu."""
        status_text = "🟢 Running" if self.running else "🔴 Stopped"
        
        return pystray.Menu(
            Item(status_text, lambda: None, enabled=False),
            Item("", lambda: None, enabled=False),  # Separator
            Item("⚙️ Settings", self.open_settings),
            Item("🪄 Setup Wizard", self.show_first_time_setup),
            Item("🔑 Setup Token", self.setup_token),
            Item("", lambda: None, enabled=False),  # Separator
            Item("▶️ Start Tracking" if not self.running else "⏸️ Stop Tracking", self.toggle_tracking),
            Item("📊 View Logs", self.view_logs),
            Item("", lambda: None, enabled=False),  # Separator
            Item("📖 About", self.show_about),
            Item("🚪 Exit", self.exit_app)
        )
    
    def update_menu(self):
        """Update the system tray menu."""
        if self.icon:
            self.icon.menu = self.create_menu()
    
    def open_settings(self, icon=None, item=None):
        """Open the settings window in a separate process."""
        def run_settings_process():
            try:
                logger.info("Launching settings window in separate process...")
                # Run settings using argument dispatch
                cmd = [sys.executable]
                if not getattr(sys, 'frozen', False):
                    cmd.append(sys.argv[0])
                cmd.append("--settings")
                subprocess.Popen(cmd)
                
            except Exception as e:
                logger.error(f"Failed to run settings process: {e}")

        # Run in a separate thread to avoid blocking the tray icon
        # Note: subprocess.Popen is non-blocking anyway, but keeping the thread wrapper is fine
        threading.Thread(target=run_settings_process, daemon=True).start()
    
    def setup_token(self, icon=None, item=None):
        """Setup authentication token via GUI."""
        # We reuse the wizard or a simple dialog. 
        # For now, let's trigger the wizard but maybe we should have a dedicated token dialog?
        # Let's use the new Wizard as it has a token step.
        self.show_first_time_setup()
    
    def on_settings_saved(self):
        """Callback when settings are saved."""
        was_running = self.running
        if was_running:
            self.stop_tracking()
        
        if was_running:
            self.start_tracking()
        
        self.update_menu()
    
    def toggle_tracking(self, icon=None, item=None):
        """Toggle tracking on/off."""
        if self.running:
            self.stop_tracking()
        else:
            self.start_tracking()
        
        self.update_menu()
    
    def start_tracking(self):
        """Start the tracking thread."""
        if self.running:
            return
        
        # Check configuration
        if not settings_manager.is_configured():
            self.notify("Setup Required", "Please configure settings first.")
            self.show_first_time_setup()
            return
        
        if not self.token_manager.get_token():
            self.notify("Token Required", "Please setup your device token.")
            self.show_first_time_setup()
            return
        
        # Initialize API client
        try:
            self.api_client = create_client(
                base_url=settings_manager.get_phoenix_url(),
                device_id=settings_manager.get_device_id(),
                verify_ssl=settings_manager.get_verify_ssl()
            )
            
            if not self.api_client:
                raise Exception("Failed to create API client")
            
            # Authenticate to get JWT token
            device_token = self.token_manager.get_token()
            auth_result = self.api_client.authenticate(device_token)
            
            if auth_result.get('status') == 'failed':
                raise Exception(f"Authentication failed: {auth_result.get('error')}")
            
            if not auth_result.get('access_token'):
                raise Exception("No access token received from server")
                
            logger.info("✅ Authenticated successfully")
                
        except Exception as e:
            logger.error(f"Failed to initialize: {e}")
            self.notify("Startup Failed", f"Could not initialize tracker: {e}")
            return
        
        self.running = True
        self.tracker_thread = threading.Thread(target=self.tracker_loop, daemon=True)
        self.tracker_thread.start()
        
        logger.info("✅ Tracker started")
        self.notify("Phoenix Tracker", "Tracking started in background")
        self.update_menu()
    
    def stop_tracking(self):
        """Stop the tracking thread."""
        if not self.running:
            return

        self.running = False
        if self.tracker_thread:
            self.tracker_thread.join(timeout=5)
        
        logger.info("⏸️ Tracker stopped")
        self.notify("Phoenix Tracker", "Tracking stopped")
        self.update_menu()
    
    def tracker_loop(self):
        """Main tracking loop."""
        logger.info("Tracker loop started")
        device_token = self.token_manager.get_token()
        
        while self.running:
            try:
                current_time = time.time()
                
                # Ensure JWT is valid (refresh if expired - every ~10 min)
                if not self.api_client.ensure_authenticated(device_token):
                    logger.error("Failed to refresh authentication")
                    self.consecutive_errors += 1
                    time.sleep(30)
                    continue
                
                # Check for gaming mode
                if self.gaming_detector.is_gaming():
                    game = self.gaming_detector.get_running_game()
                    logger.info(f"🎮 Gaming detected ({game}), pausing for 5 minutes")
                    time.sleep(300)
                    continue
                
                # Send heartbeat
                heartbeat_interval = settings_manager.get_heartbeat_interval()
                if current_time - self.last_heartbeat >= heartbeat_interval:
                    if self.send_heartbeat():
                        self.last_heartbeat = current_time
                        self.consecutive_errors = 0
                    else:
                        self.consecutive_errors += 1
                
                # Capture and upload screenshot
                capture_interval = settings_manager.get_capture_interval()
                if current_time - self.last_capture >= capture_interval:
                    # check for user activity (keyboard/mouse)
                    # Use 30s threshold or dynamic
                    if self.window_detector.is_idle(idle_threshold=15):
                        logger.debug("User is idle, skipping capture")
                    else:
                        if self.process_screenshot():
                            self.last_capture = current_time
                            self.consecutive_errors = 0
                        else:
                            self.consecutive_errors += 1
                
                # Check for too many errors
                if self.consecutive_errors >= self.max_consecutive_errors:
                    msg = f"Too many errors ({self.consecutive_errors}). Pausing for 5 minutes."
                    logger.error(msg)
                    self.notify("Tracker Paused", "Too many network errors. Pausing for 5m.")
                    time.sleep(300)
                    self.consecutive_errors = 0
                
                time.sleep(5)  # Main loop interval
                
            except Exception as e:
                logger.error(f"Error in tracker loop: {e}", exc_info=True)
                time.sleep(60)
        
        logger.info("Tracker loop stopped")
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat with current app usage."""
        if not self.api_client:
            return False
        
        try:
            app_name, window_title = self.window_detector.get_active_window()
            # 60s threshold for "Away" status in heartbeat
            is_idle = self.window_detector.is_idle(idle_threshold=60)
            
            # Get inference and network status
            inference_status = self.inference_detector.get_inference_status()
            
            result = self.api_client.send_heartbeat(
                app_name=app_name,
                window_title=window_title,
                is_idle=is_idle,
                ollama_available=inference_status.get('ollama_available'),
                ollama_models=inference_status.get('ollama_models'),
                ollama_port=settings_manager.get_ollama_port(),
                tailscale_ip=inference_status.get('tailscale_ip')
            )
            
            return result.get('status') != 'failed'
        except Exception as e:
            logger.error(f"Heartbeat failed: {e}")
            return False
    
    def process_screenshot(self) -> bool:
        """Capture and upload screenshot if there's significant activity."""
        if not self.api_client:
            return False
        
        try:
            # Capture screen
            screenshot_bytes = self.capture_screen()
            if not screenshot_bytes:
                logger.warning("Screenshot capture returned empty")
                return False
            
            logger.debug(f"Captured screenshot: {len(screenshot_bytes)} bytes")
            
            # Check for significant change
            img = Image.open(BytesIO(screenshot_bytes))
            if not self.activity_detector.has_significant_change(img):
                logger.debug("No significant change detected, skipping upload")
                return True
            
            # Upload screenshot
            logger.info("Uploading screenshot...")
            result = self.api_client.upload_screenshot(screenshot_bytes)
            logger.info(f"Screenshot upload result: {result}")
            
            if result.get('status') == 'rate_limited':
                logger.warning(f"Rate limited, retry in {result.get('retry_after', 0):.0f}s")
                return True
            
            # Check for success - backend might return various formats
            if result.get('status') == 'failed':
                return False
            
            return True  # Assume success if no explicit failure
        except Exception as e:
            logger.error(f"Screenshot processing failed: {e}")
            return False
            return False
    
    def capture_screen(self):
        """Capture the current screen (focused monitor) and return as JPEG bytes."""
        try:
            with mss.mss() as sct:
                # Detect which monitor has the active window
                monitor_idx = self.window_detector.get_focused_monitor_index(sct.monitors)
                monitor = sct.monitors[monitor_idx]
                
                screenshot = sct.grab(monitor)
                
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Resize for efficiency
                max_width = settings_manager.get_setting('max_image_width', 1024)
                img.thumbnail((max_width, max_width))
                
                # Convert to JPEG bytes
                img_byte_arr = BytesIO()
                jpeg_quality = settings_manager.get_setting('jpeg_quality', 70)
                img.save(img_byte_arr, format='JPEG', quality=jpeg_quality)
                
                return img_byte_arr.getvalue()
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return None
    
    def view_logs(self, icon=None, item=None):
        """Open the log file."""
        if log_file.exists():
            os.startfile(log_file)
        else:
            self.notify("Logs", f"No log file found at: {log_file}")
    
    def show_about(self, icon=None, item=None):
        """Show about dialog."""
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showinfo(
            "About Phoenix Tracker",
            "Phoenix Desktop Screen Time Tracker\n"
            "Version 2.0 (Modern UI)\n\n"
            "A secure desktop agent that captures screen context\n"
            "and usage data for the Phoenix Digital Homestead.\n\n"
            "Features:\n"
            "• Smart screenshot capture with MSE detection\n"
            "• Secure token storage in Windows Credential Manager\n"
            "• Gaming mode auto-pause\n"
            "• Active window tracking\n"
            "• Modern Windows 11 GUI & Notifications\n"
            "• Offline Data Queue",
            parent=root
        )
        
        root.destroy()
    
    def exit_app(self, icon=None, item=None):
        """Exit the application."""
        self.stop_tracking()
        if self.icon:
            self.icon.stop()
    
    def run(self):
        """Run the system tray application."""
        # Create and run the system tray icon
        image = create_icon_image()
        
        self.icon = pystray.Icon(
            "phoenix_tracker",
            image,
            "Phoenix Tracker",
            menu=self.create_menu()
        )
        
        # Auto-start if configured
        if settings_manager.is_configured() and self.token_manager.get_token():
            self.start_tracking()
        
        logger.info("Phoenix Tracker system tray app started")
        self.icon.run()


def main():
    """Entry point for the application."""
    # Freeze support for PyInstaller
    import multiprocessing
    multiprocessing.freeze_support()
    
    # Argument Dispatcher
    if len(sys.argv) > 1:
        if "--settings" in sys.argv:
            from gui.main_window import main as run_settings
            run_settings()
            return
        elif "--wizard" in sys.argv:
            from gui.wizard import main as run_wizard
            run_wizard()
            return

    # Default: Run Tray App
    try:
        app = PhoenixTrayApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
