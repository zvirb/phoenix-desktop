import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger(__name__)

# Constants
ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABE_RIGHT = 2

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]

class AppBarManager:
    """
    Manages the Windows Application Desktop Toolbar (AppBar) registration.
    This class handles the low-level Windows API calls to reserve screen space.
    """
    def __init__(self, hwnd):
        self.hwnd = int(hwnd)
        self.dock_width = 350
        self.abd = APPBARDATA()
        self.abd.cbSize = ctypes.sizeof(APPBARDATA)
        self.abd.hWnd = self.hwnd
        self.abd.uEdge = ABE_RIGHT
        
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        self.registered = False

    def register(self):
        """Register the window as an AppBar."""
        if not self.registered:
            logger.info(f"Registering AppBar for HWND: {self.hwnd}")
            ctypes.windll.shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(self.abd))
            self.registered = True
            self.update_position()

    def update_position(self):
        """Update the position and reserve space."""
        if not self.registered:
            return

        # 1. Propose an area
        self.abd.rc.left = self.screen_width - self.dock_width
        self.abd.rc.top = 0
        self.abd.rc.right = self.screen_width
        self.abd.rc.bottom = self.screen_height

        # 2. Query the system if this area is okay
        ctypes.windll.shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(self.abd))
        
        # 3. Re-assert our desired width (Query might have shrunk it)
        self.abd.rc.left = self.screen_width - self.dock_width
        self.abd.rc.right = self.screen_width
        
        # 4. Commit the position
        ctypes.windll.shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(self.abd))
        
        return self.abd.rc

    def set_appbar_width(self, width):
        """Dynamically change the width of the AppBar."""
        self.dock_width = width
        return self.update_position()

    def unregister(self):
        """Unregister the AppBar, releasing screen space."""
        if self.registered:
            logger.info("Unregistering AppBar")
            ctypes.windll.shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(self.abd))
            self.registered = False
