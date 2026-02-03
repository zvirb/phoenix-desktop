from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal

class ControlDeck(QFrame):
    """
    Bottom section for manual controls and gamification stats.
    """
    war_room_toggled = pyqtSignal(bool)
    no_distractions_toggled = pyqtSignal(bool)
    mission_control_clicked = pyqtSignal()
    # Alias for newer consumers
    zen_mode_toggled = no_distractions_toggled

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #0b1121; border-top: 1px solid #1e293b;")
        self.setFixedHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # XP Bar Section
        xp_layout = QHBoxLayout()
        self.lvl_lbl = QLabel("LVL 1")
        self.lvl_lbl.setStyleSheet("color: #3b82f6; font-weight: bold; font-family: 'Segoe UI';")
        
        self.xp_bar = QProgressBar()
        self.xp_bar.setFixedHeight(6)
        self.xp_bar.setTextVisible(False)
        self.xp_bar.setValue(0)
        self.xp_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e293b;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        
        xp_layout.addWidget(self.lvl_lbl)
        xp_layout.addWidget(self.xp_bar)
        layout.addLayout(xp_layout)
        
        layout.addSpacing(10)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_war_room = QPushButton("WAR ROOM")
        self.btn_war_room.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_war_room.setCheckable(True)
        self.btn_war_room.setStyleSheet("""
            QPushButton {
                background-color: #1d4ed8;
                color: white;
                font-weight: 800;
                border-radius: 6px;
                padding: 12px;
                font-size: 11px;
                letter-spacing: 1px;
            }
            QPushButton:hover { background-color: #2563eb; }
            QPushButton:checked {
                background-color: #ef4444; 
                border: 2px solid #fca5a5;
            }
        """)
        self.btn_war_room.toggled.connect(self._on_war_room_toggled)
        
        self.btn_distractions = QPushButton("NO DISTRACTIONS")
        self.btn_distractions.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_distractions.setCheckable(True)
        self.btn_distractions.setStyleSheet("""
            QPushButton {
                background-color: #334155;
                color: #e2e8f0;
                font-weight: 600;
                border-radius: 6px;
                padding: 12px;
                border: 1px solid #475569;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #475569; }
            QPushButton:checked {
                background-color: #475569;
                border: 1px solid #94a3b8;
                color: #fff;
            }
        """)
        self.btn_distractions.toggled.connect(self._on_no_distractions_toggled)
        
        btn_layout.addWidget(self.btn_war_room)
        btn_layout.addWidget(self.btn_distractions)
        
        # Mission Control Button
        self.btn_mission = QPushButton("MISSION CONTROL")
        self.btn_mission.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mission.setStyleSheet("""
            QPushButton {
                background-color: #2e3b55;
                color: #e2e8f0;
                font-weight: 800;
                border-radius: 6px;
                padding: 12px;
                font-size: 11px;
                border: 1px solid #475569;
            }
            QPushButton:hover { background-color: #475569; }
        """)
        self.btn_mission.clicked.connect(self.mission_control_clicked.emit)
        
        layout.addLayout(btn_layout)
        layout.addWidget(self.btn_mission)

    def _on_war_room_toggled(self, checked):
        if checked:
            self.btn_war_room.setText("EXIT WAR ROOM")
        else:
            self.btn_war_room.setText("WAR ROOM")
        self.war_room_toggled.emit(checked)

    def _on_no_distractions_toggled(self, checked):
        self.no_distractions_toggled.emit(checked)
        
    def set_distraction_text(self, text):
        """Update text of distraction button (e.g. for timer)."""
        self.btn_distractions.setText(text)

    def set_stats(self, level, points, next_level_points):
        """Update the XP bar and level label."""
        self.lvl_lbl.setText(f"LVL {level}")
        
        if next_level_points > 0:
            percentage = min(100, int((points / (points + next_level_points)) * 100))
            self.xp_bar.setValue(percentage)
            self.xp_bar.setToolTip(f"{points} / {points + next_level_points} XP")
        else:
            self.xp_bar.setValue(0)
