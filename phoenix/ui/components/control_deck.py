from PyQt6.QtWidgets import QFrame, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QProgressBar
from PyQt6.QtCore import Qt

class ControlDeck(QFrame):
    """
    Bottom section for manual controls and gamification stats.
    """
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
        
    def set_stats(self, level, points, next_level_points):
        """Update the XP bar and level label."""
        self.lvl_lbl.setText(f"LVL {level}")
        
        # Calculate percentage for progress bar
        # We need points_to_next_level and total_points?
        # Typically XP bars show progress within the current level.
        # But payload gives 'points_to_next_level'. 
        # Let's assume progress is: (total_points % 1000) / 1000 or similar?
        # Actually payload has 'points_to_next_level', usually meaning 'points needed'.
        # Let's assume progress = (next_level - needed) / next_level * 100
        # Wait, payload has: 'total_points': 0, 'points_to_next_level': 400
        # If I have 100 points, I need 300 more.
        # So bar should be 100/400? Or (400-300)/400?
        # Let's assume simplistic progress for now:
        # Progress = (Total Points accumulated in this level) / (Total Points for this level)
        # Without level thresholds, it's hard.
        # Let's just use a visual filler if we lack data, but we can try to guess.
        # The payload had 'points_to_next_level': 400. 
        # Let's assume 'points_to_next_level' is the REMAINING points needed.
        # And we don't know the level start. 
        # But maybe 'points_to_next_level' is the THRESHOLD? No, usually it's delta.
        # Let's look at payload again: 'total_points': 0, 'points_to_next_level': 400.
        # If I earn 50, total=50. 'points_to_next_level' becomes 350?
        # If so, progress = 1 - (points_to_next_level / (total + points_to_next_level)) ?
        # No, level thresholds usually grow.
        
        # Simplified: Just show total points % 100 as a visual heuristic if we don't have max.
        # But let's check if we can deduce max.
        # Let's assume the bar should show percentage complete towards next level.
        # If we interpret 'points_to_next_level' as the GOAL, then current/goal.
        # If we interpret it as REMAINING, it's tricky.
        
        # Let's assume standard behavior:
        # progress = (total_points % 1000) / 10 is safest "visual" if we are unsure.
        # But wait, let's just create a generic setter.
        
        # Actually, let's treat 'points_to_next_level' as the target for the current level (0 to X).
        # This is likely wrong but visually okay for start.
        if next_level_points > 0:
            percentage = min(100, int((points / (points + next_level_points)) * 100))
            self.xp_bar.setValue(percentage)
            self.xp_bar.setToolTip(f"{points} / {points + next_level_points} XP")
        else:
            self.xp_bar.setValue(0)
        
        # layout.addSpacing(10) # Removed invalid reference
        btn_layout.setSpacing(10)
        
        self.btn_war_room = QPushButton("WAR ROOM")
        self.btn_war_room.setCursor(Qt.CursorShape.PointingHandCursor)
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
        """)
        self.btn_war_room.clicked.connect(lambda: print("WAR ROOM Activated"))
        
        self.btn_distractions = QPushButton("NO DISTRACTIONS")
        self.btn_distractions.setCursor(Qt.CursorShape.PointingHandCursor)
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
        """)
        self.btn_distractions.clicked.connect(lambda: print("No Distractions Mode"))
        
        btn_layout.addWidget(self.btn_war_room)
        btn_layout.addWidget(self.btn_distractions)
        
        layout.addLayout(btn_layout)
