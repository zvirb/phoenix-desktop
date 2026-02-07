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
        self._last_hwnd = None
        self._last_app_name = None
        self._pid_cache = {}
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

            # Check cache
            if self._last_hwnd == hwnd and self._last_app_name:
                return self._last_app_name, window_title
            
            # Get process ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            # Check PID cache first
            if pid in self._pid_cache:
                app_name = self._pid_cache[pid]
            else:
                # Get process name
                try:
                    process = psutil.Process(pid)
                    app_name = process.name()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    app_name = "Unknown"

                # Update PID cache
                self._pid_cache[pid] = app_name

                # Prevent cache from growing too large
                if len(self._pid_cache) > 100:
                    self._pid_cache.clear()
            
            # Update cache
            self._last_hwnd = hwnd
            self._last_app_name = app_name

            return app_name, window_title
            
        except Exception as e:
            logger.debug(f"Failed to get active window: {e}")
            self._last_hwnd = None
            self._last_app_name = None
            return "Unknown", "Unknown"

    def _get_fallback_window(self) -> Tuple[str, str]:
        """Fallback when Windows API is not available."""
        return "Unknown", "Platform not supported"
    
    def is_idle(self, idle_threshold: int = 60) -> bool:
        """
        Check if the user is idle.
        
        Args:
            idle_threshold: Seconds of inactivity to consider idle
            
        Returns:
            True if user has been idle for longer than threshold
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            idle_time = self.get_idle_time()
            return idle_time > idle_threshold
        except Exception as e:
            logger.error(f"Error checking idle status: {e}")
            return False

    def get_idle_time(self) -> float:
        """Get number of seconds since last user input."""
        if not WINDOWS_AVAILABLE:
            return 0.0
            
        try:
            import ctypes
            
            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
                
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = ctypes.sizeof(LASTINPUTINFO)
            
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lastInputInfo)):
                millis = ctypes.windll.kernel32.GetTickCount() - lastInputInfo.dwTime
                return millis / 1000.0
            return 0.0
        except Exception:
            return 0.0

    def get_focused_monitor_index(self, mss_monitors: list) -> int:
        """
        Determine which monitor has the active window.
        
        Args:
            mss_monitors: List of monitor dicts from mss.monitors
            
        Returns:
            Index of the monitor in the list (1-based usually, 0 is all)
        """
        if not WINDOWS_AVAILABLE:
            return 1
            
        try:
            hwnd = win32gui.GetForegroundWindow()
            rect = win32gui.GetWindowRect(hwnd)
            win_left, win_top, win_right, win_bottom = rect
            
            # Calculate window center
            win_center_x = (win_left + win_right) / 2
            win_center_y = (win_top + win_bottom) / 2
            
            # Find which monitor contains the center
            # mss_monitors[0] is usually "All Monitors", so start from 1
            for i in range(1, len(mss_monitors)):
                m = mss_monitors[i]
                m_left = m['left']
                m_top = m['top']
                m_right = m_left + m['width']
                m_bottom = m_top + m['height']
                
                if (m_left <= win_center_x <= m_right and 
                    m_top <= win_center_y <= m_bottom):
                    return i
            
            # Fallback to primary
            return 1
        except Exception as e:
            logger.error(f"Error determining focused monitor: {e}")
            return 1


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
