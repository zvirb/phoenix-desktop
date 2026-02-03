from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class StatusBadge(QLabel):
    """
    A unified status icon with hover effects.
    """
    def __init__(self, icon_text, object_name="StatusBadge", tooltip=""):
        super().__init__(icon_text)
        self.setObjectName(object_name)
        self.setToolTip(tooltip)
        self.setFixedSize(32, 32)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 6px;
                color: #94a3b8;
                font-size: 14px;
            }
            QLabel:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255,255,255, 0.2);
            }
        """)

class HeaderHUD(QFrame):
    """
    Top-level status bar containing the Pulse, Eye, Brain, and Mesh indicators.
    """
    toggled = pyqtSignal() # Signal emitted when collapse toggled

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.setStyleSheet("background-color: #0b1121; border-bottom: 1px solid #1e293b;")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        
        # Toggle Button
        self.btn_toggle = QPushButton("≡")
        self.btn_toggle.setFixedSize(30, 30)
        self.btn_toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #94a3b8;
                font-size: 18px;
                border: none;
            }
            QPushButton:hover { color: white; }
        """)
        self.btn_toggle.clicked.connect(self.toggled.emit)
        layout.addWidget(self.btn_toggle)

        layout.addSpacing(10)

        # Branding / Title
        title = QLabel("PHOENIX")
        title.setStyleSheet("""
            font-family: 'Segoe UI Variable Display', sans-serif;
            font-weight: 800;
            font-size: 14px;
            letter-spacing: 2px;
            color: #f8fafc;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Indicators
        # 1. Heartbeat (System Alive)
        self.pulse = StatusBadge("♥", tooltip="Core Connection: Active")
        self.pulse.setStyleSheet(self.pulse.styleSheet().replace("#94a3b8", "#ef4444")) # Red heart
        
        # 2. Visual (Camera/Screen)
        self.eye = StatusBadge("👁", tooltip="Visual Context: Monitoring")
        
        # 3. Brain (Local Inference)
        self.brain = StatusBadge("🧠", tooltip="Ollama Inference: Ready")
        
        # 4. Mesh (Network)
        self.mesh = StatusBadge("🌐", tooltip="Tailscale Mesh: Connected")
        
        layout.addWidget(self.pulse)
        layout.addWidget(self.eye)
        layout.addWidget(self.brain)
        layout.addWidget(self.mesh)

    def set_badge_status(self, badge, active: bool):
        if active:
            # Greenish for active
            badge.setStyleSheet(badge.styleSheet().replace("#94a3b8", "#10b981").replace("#ef4444", "#10b981"))
        else:
            # Gray for inactive
            badge.setStyleSheet(badge.styleSheet().replace("#10b981", "#94a3b8").replace("#ef4444", "#94a3b8"))

    def update_brain(self, active: bool):
        self.set_badge_status(self.brain, active)

    def update_mesh(self, active: bool):
        self.set_badge_status(self.mesh, active)
    
    def update_visual(self, active: bool):
        self.set_badge_status(self.eye, active)
