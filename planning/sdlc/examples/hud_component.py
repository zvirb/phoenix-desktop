from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPainter, QBrush, QIcon

class StatusBadge(QFrame):
    """
    A circular status indicator with pulsing effect.
    """
    def __init__(self, color="#10B981", parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.color = color
        self.setStyleSheet(f"""
            StatusBadge {{
                background-color: {color};
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
        """)

class HeaderHUD(QFrame):
    """
    Top status bar with Pulse, Eye, Brain, and Mesh indicators.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #111621; border-bottom: 1px solid #2a3140;")
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)
        
        # Branding
        title = QLabel("PHOENIX")
        title.setStyleSheet("color: #ffffff; font-weight: bold; font-family: 'Manrope'; letter-spacing: 2px;")
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Indicators
        self.pulse_ind = self._create_indicator("♥", "#EF4444") # Heartbeat
        self.eye_ind = self._create_indicator("👁", "#10B981")   # Visual
        self.brain_ind = self._create_indicator("🧠", "#8B5CF6")  # Inference
        self.mesh_ind = self._create_indicator("🌐", "#3B82F6")   # Network
        
        layout.addWidget(self.pulse_ind)
        layout.addWidget(self.eye_ind)
        layout.addWidget(self.brain_ind)
        layout.addWidget(self.mesh_ind)

    def _create_indicator(self, icon_text, active_color):
        lbl = QLabel(icon_text)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {active_color};
                font-size: 16px;
                padding: 4px;
                background-color: rgba(255,255,255,0.05);
                border-radius: 4px;
            }}
            QLabel:hover {{
                background-color: rgba(255,255,255,0.1);
            }}
        """)
        lbl.setFixedSize(30, 30)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl
