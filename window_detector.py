"""
Platform-specific active window detection.
"""
import sys
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Try to import Windows-specific modules
try:
    import win32gui
    import win32process
    import psutil
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


class WindowDetector:
    """Detect active window and application."""
    
    def __init__(self):
        """Initialize window detector."""
        if not WINDOWS_AVAILABLE:
            logger.warning("Windows API not available. Window detection will be limited.")
    
    def get_active_window(self) -> Tuple[str, str]:
        """
        Get the active window information.
        
        Returns:
            Tuple of (app_name, window_title)
        """
        if WINDOWS_AVAILABLE:
            return self._get_windows_active_window()
        else:
            return self._get_fallback_window()
    
    def _get_windows_active_window(self) -> Tuple[str, str]:
        """Get active window on Windows."""
        try:
            # Get the foreground window handle
            hwnd = win32gui.GetForegroundWindow()
            
            # Get window title
            window_title = win32gui.GetWindowText(hwnd)
            
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Get process name
            try:
                process = psutil.Process(pid)
                app_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                app_name = "Unknown"
            
            return app_name, window_title
            
        except Exception as e:
            logger.debug(f"Failed to get active window: {e}")
            return "Unknown", "Unknown"
    
    def _get_fallback_window(self) -> Tuple[str, str]:
        """Fallback when Windows API is not available."""
        return "Unknown", "Platform not supported"
    
    def is_idle(self, idle_threshold: int = 300) -> bool:
        """
        Check if the user is idle (not implemented yet).
        
        Args:
            idle_threshold: Seconds of inactivity to consider idle
            
        Returns:
            False (placeholder - requires additional implementation)
        """
        # This would require win32api.GetLastInputInfo() or similar
        # For now, we always assume the user is active
        return False


# Convenience function
def get_current_window() -> Tuple[str, str]:
    """Get current active window information."""
    detector = WindowDetector()
    return detector.get_active_window()


if __name__ == "__main__":
    # Test the window detector
    detector = WindowDetector()
    app_name, window_title = detector.get_active_window()
    print(f"Active App: {app_name}")
    print(f"Window Title: {window_title}")
