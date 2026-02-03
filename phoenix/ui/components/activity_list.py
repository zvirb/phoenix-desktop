from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QScrollArea, QSizePolicy, QPushButton
)
from PyQt6.QtGui import QFontMetrics, QPixmap, QColor
from PyQt6.QtCore import Qt, pyqtSignal

class ActivityCard(QFrame):
    """
    Rich event card inspired by 'Hero RPG' variant.
    Supports: Header, Body, Badges, Actions.
    """
    def __init__(self, title, subtitle, time_str, icon="📷", tags=None, image=None, parent=None):
        super().__init__(parent)
        self.setObjectName("ActivityCard")
        # Remove fixed height to allow expansion
        
        # Styles
        self.setStyleSheet("""
            QFrame#ActivityCard {
                background-color: #1c1f26;
                border: 1px solid #334155;
                border-radius: 12px;
            }
            QLabel { background: transparent; border: none; font-family: 'Segoe UI', sans-serif; }
        """)
        
        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 1. Optional Image Header
        if image:
            img_lbl = QLabel()
            img_lbl.setFixedHeight(80)
            img_lbl.setStyleSheet(f"background-image: url({image}); background-position: center; border-top-left-radius: 12px; border-top-right-radius: 12px;")
            main_layout.addWidget(img_lbl)
        
        # Content Container
        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(16, 12, 16, 12)
        c_layout.setSpacing(6)
        
        # 2. Header Row (Icon + Title + Time)
        h_row = QHBoxLayout()
        h_row.setSpacing(8)
        
        # Icon Badge
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(24, 24)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("""
            background-color: rgba(59, 130, 246, 0.15); 
            color: #60a5fa; 
            border-radius: 6px; 
            font-size: 14px;
        """)
        h_row.addWidget(icon_lbl)
        
        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #f8fafc; font-weight: 700; font-size: 13px;")
        h_row.addWidget(title_lbl)
        
        h_row.addStretch()
        
        # Time
        if time_str:
            time_lbl = QLabel(time_str)
            time_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 600;")
            h_row.addWidget(time_lbl)
            
        c_layout.addLayout(h_row)
        
        # 3. Subtitle
        sub_lbl = QLabel(subtitle)
        sub_lbl.setWordWrap(True)
        sub_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; line-height: 1.4;")
        c_layout.addWidget(sub_lbl)
        
        # 4. Tags Row (Optional)
        if tags:
            tag_row = QHBoxLayout()
            tag_row.setSpacing(6)
            for tag in tags:
                t_lbl = QLabel(tag)
                t_lbl.setStyleSheet("""
                    color: #10b981; 
                    background-color: rgba(16, 185, 129, 0.1); 
                    padding: 2px 6px; 
                    border-radius: 4px; 
                    font-size: 10px; font-weight: 700;
                """)
                tag_row.addWidget(t_lbl)
            tag_row.addStretch()
            c_layout.addLayout(tag_row)
            
        main_layout.addWidget(content)

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
        self.layout.setContentsMargins(12, 4, 12, 12) # Padding for shadow
        self.layout.setSpacing(12)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.setWidget(self.container)
        
        # Real-time data will be added via signals
        # self.add_event("System", "Phoenix Sidebar Ready", "", "🚀")

    def add_event(self, title, sub, time, icon, tags=None, image=None):
        card = ActivityCard(title, sub, time, icon, tags, image)
        self.layout.insertWidget(0, card) # Add to top
