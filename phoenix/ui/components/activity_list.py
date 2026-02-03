from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QScrollArea, QSizePolicy
from PyQt6.QtGui import QFontMetrics
from PyQt6.QtCore import Qt, pyqtSignal

class ActivityCard(QFrame):
    """
    Represents a single event in the feed.
    """
    def __init__(self, title, subtitle, time_str, icon="📷", parent=None):
        super().__init__(parent)
        self.setObjectName("ActivityCard")
        self.setFixedHeight(70)
        
        layout = QHBoxLayout(self) # Change to HBox for Icon + Text
        layout.setContentsMargins(12, 10, 12, 10)
        
        # Icon Column
        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 18px; color: #64748b; background: transparent;")
        icon_lbl.setFixedWidth(30)
        layout.addWidget(icon_lbl)
        
        # Text Column (Expandable)
        text_col = QWidget()
        text_col.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        text_col.setStyleSheet("background: transparent; border: none;")
        t_layout = QVBoxLayout(text_col)
        t_layout.setContentsMargins(5, 0, 5, 0)
        t_layout.setSpacing(2)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #e2e8f0; font-weight: 600; font-size: 13px; border: none; background: transparent;")
        
        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet("color: #94a3b8; font-size: 11px; border: none; background: transparent;")
        # Elide long text
        font = lbl_sub.font()
        font_metrics = QFontMetrics(font)
        elided_text = font_metrics.elidedText(subtitle, Qt.TextElideMode.ElideRight, 200) # Approx width
        lbl_sub.setText(elided_text)
        # Note: Dynamic eliding requires resizeEvent handling, this is a static approx
        
        t_layout.addWidget(lbl_title)
        t_layout.addWidget(lbl_sub)
        t_layout.addStretch()
        
        layout.addWidget(text_col, 1) # Stretch factor 1
        
        # Time Column (Fixed width)
        if time_str:
            lbl_time = QLabel(time_str)
            lbl_time.setFixedWidth(40) # Fix width to prevent it being crushed
            lbl_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
            lbl_time.setStyleSheet("color: #475569; font-size: 10px; font-weight: bold; padding-top: 2px; border: none; background: transparent;")
            layout.addWidget(lbl_time)

from PyQt6.QtWidgets import QHBoxLayout

class ActivityList(QScrollArea):
    """
    The main scrolling list of activities.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QWidget#scrollContents { background: transparent; }
        """)
        
        self.container = QWidget()
        self.container.setObjectName("scrollContents")
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(8)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setWidget(self.container)
        
        # Real-time data will be added via signals
        # self.add_event("System", "Phoenix Sidebar Ready", "", "🚀")

    def add_event(self, title, sub, time, icon):
        card = ActivityCard(title, sub, time, icon)
        self.layout.insertWidget(0, card) # Add to top
