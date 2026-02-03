from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

from phoenix.core.token_manager import TokenManager

class OnboardingView(QWidget):
    """
    Assistant wizard to help the user configure the device token.
    """
    token_saved = pyqtSignal() # Emitted when token is successfully saved

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 40, 20, 20)
        self.layout.setSpacing(15)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Title
        title = QLabel("Welcome to Phoenix")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin-bottom: 10px;")
        title.setWordWrap(True)
        self.layout.addWidget(title)

        # Instructions
        instr = QLabel(
            "To connect this device to your Digital Homestead, please enter your Device Token.\n\n"
            "1. Go to your Web Dashboard\n"
            "2. Settings > Devices\n"
            "3. Generate 'Device Token'"
        )
        instr.setStyleSheet("color: #94a3b8; font-size: 13px; line-height: 1.4;")
        instr.setWordWrap(True)
        self.layout.addWidget(instr)

        # Input
        self.txt_token = QLineEdit()
        self.txt_token.setPlaceholderText("Paste Token Here...")
        self.txt_token.setStyleSheet("""
            QLineEdit {
                background-color: #1e293b;
                border: 1px solid #334155;
                color: white;
                padding: 12px;
                border-radius: 6px;
                font-family: 'Consolas', monospace;
            }
            QLineEdit:focus { border-color: #3b82f6; }
        """)
        self.layout.addWidget(self.txt_token)

        # Button
        self.btn_save = QPushButton("Connect Device")
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2563eb; }
        """)
        self.btn_save.clicked.connect(self.save_token)
        self.layout.addWidget(self.btn_save)

        self.layout.addStretch()

    def save_token(self):
        token = self.txt_token.text().strip()
        if not token:
            QMessageBox.warning(self, "Input Error", "Please enter a valid token.")
            return

        manager = TokenManager()
        if manager.save_token(token):
            self.token_saved.emit()
        else:
            QMessageBox.critical(self, "Error", "Failed to save token to Secure Storage.")
