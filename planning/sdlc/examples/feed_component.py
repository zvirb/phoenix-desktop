from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal

class ActivityCard(QFrame):
    """
    A single event item in the feed (Screenshot, Alert, etc.)
    """
    deleted = pyqtSignal(str) # Emits ID when deleted

    def __init__(self, event_id, title, subtitle, timestamp, icon="📷", parent=None):
        super().__init__(parent)
        self.event_id = event_id
        self.setStyleSheet("""
            ActivityCard {
                background-color: #1c212e;
                border: 1px solid #2a3140;
                border-radius: 8px;
            }
            ActivityCard:hover {
                border-color: #1754cf;
            }
        """)
        self.setFixedHeight(80)
        
        layout = QVBoxLayout(self)
        
        # Header Row
        row1 = QWidget()
        r1_layout = QVBoxLayout(row1) # Simplified for example
        
        self.lbl_title = QLabel(f"{icon}  {title}")
        self.lbl_title.setStyleSheet("color: white; font-weight: bold;")
        
        self.lbl_sub = QLabel(subtitle)
        self.lbl_sub.setStyleSheet("color: #9da6b8; font-size: 11px;")
        
        layout.addWidget(self.lbl_title)
        layout.addWidget(self.lbl_sub)
        
        # Delete Button (Hidden usually, shown on hover/actions)
        # For simplicity, just right click logic would go here

class ActivityFeed(QScrollArea):
    """
    Virtualized stream of context events.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { width: 4px; background: #111621; }
            QScrollBar::handle:vertical { background: #2a3140; border-radius: 2px; }
        """)
        
        self.container = QWidget()
        self.container.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(self.container)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.setSpacing(10)
        
        self.setWidget(self.container)
        
        # Add some mock data
        self.add_card("1", "Screen Capture", "Visual context synced", "10:42 AM")
        self.add_card("2", "App Switch", "Focus: VS Code", "10:45 AM", "💻")
        self.add_card("3", "Idle Detected", "User away for 5m", "11:00 AM", "💤")

    def add_card(self, id, title, sub, time, icon="📷"):
        card = ActivityCard(id, title, sub, time, icon)
        self.layout.insertWidget(0, card) # Add to top
