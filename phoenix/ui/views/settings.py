from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTabWidget, QWidget, 
    QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
import config

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Phoenix Settings")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog { background-color: #0f172a; color: #f8fafc; }
            QLabel { color: #f8fafc; font-size: 13px; }
            QLineEdit { 
                background-color: #1e293b; 
                border: 1px solid #334155; 
                color: white; 
                padding: 6px; 
                border-radius: 4px;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #2563eb; }
            QTabWidget::pane { border: 1px solid #334155; }
            QTabBar::tab {
                background: #1e293b;
                color: #94a3b8;
                padding: 8px 12px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #3b82f6;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Tabs
        tabs = QTabWidget()
        tabs.addTab(self._create_general_tab(), "General")
        tabs.addTab(self._create_connection_tab(), "Connection")
        tabs.addTab(self._create_debug_tab(), "Debug")
        layout.addWidget(tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: #475569;")
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def _create_general_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Autohide
        self.chk_autohide = QCheckBox("Auto-hide Sidebar")
        self.chk_autohide.setStyleSheet("color: white;")
        layout.addWidget(self.chk_autohide)
        
        # Start on Boot
        self.chk_boot = QCheckBox("Start on System Boot")
        self.chk_boot.setStyleSheet("color: white;")
        layout.addWidget(self.chk_boot)
        
        return widget

    def _create_connection_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        layout.addWidget(QLabel("Server URL:"))
        self.txt_url = QLineEdit(config.PHOENIX_API_URL)
        layout.addWidget(self.txt_url)
        
        layout.addSpacing(10)
        
        layout.addWidget(QLabel("Device ID (Read-only):"))
        lbl_device = QLineEdit(config.DEVICE_ID)
        lbl_device.setReadOnly(True)
        lbl_device.setStyleSheet("background-color: #0f172a; border: none; color: #64748b;")
        layout.addWidget(lbl_device)
        
        return widget

    def _create_debug_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        btn_test = QPushButton("Test API Connection")
        btn_test.clicked.connect(self._test_connection)
        layout.addWidget(btn_test)
        
        layout.addSpacing(10)
        
        btn_reset = QPushButton("Reset Local Database")
        btn_reset.setStyleSheet("background-color: #ef4444;")
        btn_reset.clicked.connect(lambda: QMessageBox.warning(self, "Reset", "Not implemented yet."))
        layout.addWidget(btn_reset)
        
        return widget

    def _test_connection(self):
        # TODO: Implement actual test
        QMessageBox.information(self, "Test", "Connection test triggered (check logs).")

    def save_settings(self):
        # TODO: Persist settings to registry
        new_url = self.txt_url.text()
        # config.update_url(new_url) ?
        QMessageBox.information(self, "Saved", "Settings saved. Restart required for some changes.")
        self.accept()
