import sys
import ctypes
from ctypes import wintypes
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QTimer
# Status HUD Component would be imported here
# from components.status_hud import HeaderHUD

# Windows API Constants for AppBar
ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABE_RIGHT = 2
ABM_SETAUTOHIDEBAR = 0x00000008 # For future use

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", wintypes.RECT),
        ("lParam", wintypes.LPARAM),
    ]

class PhoenixSidebar(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dock_width = 350
        self.screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        self.screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        
        self.init_ui()
        self.register_appbar()
        
    def init_ui(self):
        self.setWindowTitle("Phoenix Sidebar")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #0b1210; color: white;")
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Placeholder Components
        header = QLabel("PHOENIX HUD CONTAINER")
        header.setStyleSheet("background-color: #111621; padding: 20px; font-weight: bold;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        content = QLabel("Activity Stream goes here...\n- Screenshot captured\n- Idle detected")
        content.setAlignment(Qt.AlignmentFlag.AlignTop)
        content.setStyleSheet("padding: 20px; color: #9da6b8;")
        layout.addWidget(content, 1) # Stretch factor 1
        
        footer = QPushButton("WAR ROOM")
        footer.setStyleSheet("""
            background-color: #1754cf; 
            color: white; 
            font-weight: bold; 
            padding: 15px; 
            border: none;
            border-top: 1px solid #2a3140;
        """)
        layout.addWidget(footer)

    def register_appbar(self):
        # 1. Prepare Data Structure
        self.abd = APPBARDATA()
        self.abd.cbSize = ctypes.sizeof(APPBARDATA)
        self.abd.hWnd = int(self.winId())
        self.abd.uEdge = ABE_RIGHT
        
        # 2. Register
        ctypes.windll.shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(self.abd))
        
        # 3. Set Position & Reserve Space
        self.update_appbar_pos()

    def update_appbar_pos(self):
        # Allow Windows to adjust the rect if needed
        self.abd.rc.left = self.screen_width - self.dock_width
        self.abd.rc.top = 0
        self.abd.rc.right = self.screen_width
        self.abd.rc.bottom = self.screen_height

        # Query acceptable position
        ctypes.windll.shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(self.abd))
        
        # Re-assert desired dock (Query might have changed it)
        self.abd.rc.left = self.screen_width - self.dock_width
        self.abd.rc.right = self.screen_width
        
        # Commit the position (Reserves the space!)
        ctypes.windll.shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(self.abd))
        
        # Move the QT Window to match
        self.setGeometry(
            self.abd.rc.left, 
            self.abd.rc.top, 
            self.abd.rc.right - self.abd.rc.left, 
            self.abd.rc.bottom - self.abd.rc.top
        )

    def closeEvent(self, event):
        # Unregister on close to give back screen space
        ctypes.windll.shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(self.abd))
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    sidebar = PhoenixSidebar()
    sidebar.show()
    sys.exit(app.exec())
