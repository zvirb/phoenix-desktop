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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from windows_settings import settings_manager
from gui_settings import SettingsWindow
from token_manager import TokenManager
from api_client import create_client
from window_detector import WindowDetector
from activity_detector import ActivityDetector
from gaming_detector import GamingDetector
import mss
from io import BytesIO

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('phoenix_tracker.log')
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
        
        self.last_heartbeat = 0
        self.last_capture = 0
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        # Check if first-time setup is needed
        if not settings_manager.is_configured():
            self.show_first_time_setup()
    
    def show_first_time_setup(self):
        """Show first-time setup wizard."""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        result = messagebox.askquestion(
            "Welcome to Phoenix Tracker",
            "It looks like this is your first time running Phoenix Tracker.\n\n"
            "Would you like to configure your settings now?",
            icon='question'
        )
        
        root.destroy()
        
        if result == 'yes':
            self.open_settings()
    
    def create_menu(self):
        """Create the system tray menu."""
        status_text = "🟢 Running" if self.running else "🔴 Stopped"
        
        return pystray.Menu(
            Item(status_text, lambda: None, enabled=False),
            Item("", lambda: None, enabled=False),  # Separator
            Item("⚙️ Settings", self.open_settings),
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
        """Open the settings window."""
        def callback():
            settings = SettingsWindow(on_save=self.on_settings_saved)
            settings.show()
        
        # Run in main thread for GUI
        if threading.current_thread() is threading.main_thread():
            callback()
        else:
            # Schedule on main thread
            tk.Tk().after(0, callback)
    
    def setup_token(self, icon=None, item=None):
        """Setup authentication token via GUI."""
        root = tk.Tk()
        root.withdraw()
        
        token = tk.simpledialog.askstring(
            "Setup Token",
            "Enter your device token from Phoenix Dashboard:",
            parent=root
        )
        
        if token:
            if self.token_manager.save_token(token.strip()):
                messagebox.showinfo("Success", "Token saved successfully!", parent=root)
            else:
                messagebox.showerror("Error", "Failed to save token", parent=root)
        
        root.destroy()
    
    def on_settings_saved(self):
        """Callback when settings are saved."""
        # Restart tracker if it was running
        was_running = self.running
        if was_running:
            self.stop_tracking()
        
        # Reinitialize with new settings
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
            logger.warning("Tracker already running")
            return
        
        # Check configuration
        if not settings_manager.is_configured():
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "Configuration Required",
                "Please configure your settings before starting the tracker.",
                parent=root
            )
            root.destroy()
            self.open_settings()
            return
        
        # Check token
        if not self.token_manager.get_token():
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askquestion(
                "Token Required",
                "No authentication token found. Would you like to set it up now?",
                parent=root
            )
            root.destroy()
            
            if result == 'yes':
                self.setup_token()
            return
        
        # Initialize API client
        self.api_client = create_client(
            base_url=settings_manager.get_phoenix_url(),
            device_id=settings_manager.get_device_id(),
            verify_ssl=settings_manager.get_verify_ssl()
        )
        
        if not self.api_client:
            logger.error("Failed to initialize API client")
            return
        
        self.running = True
        self.tracker_thread = threading.Thread(target=self.tracker_loop, daemon=True)
        self.tracker_thread.start()
        
        logger.info("✅ Tracker started")
        self.update_menu()
    
    def stop_tracking(self):
        """Stop the tracking thread."""
        self.running = False
        if self.tracker_thread:
            self.tracker_thread.join(timeout=5)
        
        logger.info("⏸️ Tracker stopped")
        self.update_menu()
    
    def tracker_loop(self):
        """Main tracking loop."""
        logger.info("Tracker loop started")
        
        while self.running:
            try:
                current_time = time.time()
                
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
        """Capture and upload screenshot if there's significant activity."""
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
    
    def capture_screen(self):
        """Capture the current screen and return as JPEG bytes."""
        try:
            with mss.mss() as sct:
                monitor = sct.monitors[1]
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
        log_path = Path(__file__).parent / "phoenix_tracker.log"
        if log_path.exists():
            os.startfile(log_path)
        else:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo("Info", "No log file found yet.", parent=root)
            root.destroy()
    
    def show_about(self, icon=None, item=None):
        """Show about dialog."""
        root = tk.Tk()
        root.withdraw()
        
        messagebox.showinfo(
            "About Phoenix Tracker",
            "Phoenix Desktop Screen Time Tracker\n"
            "Version 2.0\n\n"
            "A secure desktop agent that captures screen context\n"
            "and usage data for the Phoenix Digital Homestead.\n\n"
            "Features:\n"
            "• Smart screenshot capture with SSIM detection\n"
            "• Secure token storage in Windows Credential Manager\n"
            "• Gaming mode auto-pause\n"
            "• Active window tracking\n"
            "• Modern Windows 11 GUI",
            parent=root
        )
        
        root.destroy()
    
    def exit_app(self, icon=None, item=None):
        """Exit the application."""
        self.stop_tracking()
        if self.icon:
            self.icon.stop()
        sys.exit(0)
    
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
    """Entry point for the system tray application."""
    try:
        app = PhoenixTrayApp()
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start Phoenix Tracker:\n{e}")
        root.destroy()
        sys.exit(1)


if __name__ == "__main__":
    main()
