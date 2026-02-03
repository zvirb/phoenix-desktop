from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt

class StatCard(QFrame):
    def __init__(self, title, icon, value, trend, trend_positive=True):
        super().__init__()
        self.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: 1px solid #334155;
                border-radius: 8px;
            }
            QLabel { background: transparent; border: none; font-family: 'Segoe UI', sans-serif; }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(12, 10, 12, 10)
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet("color: #3b82f6; font-size: 16px;")
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase;")
        
        header_layout.addWidget(icon_lbl)
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Value
        val_lbl = QLabel(value)
        # Use slightly smaller font or better line height to prevent clipping
        val_lbl.setStyleSheet("color: #f8fafc; font-size: 18px; font-weight: 800; padding-bottom: 2px;")
        layout.addWidget(val_lbl)
        
        # Trend
        trend_lbl = QLabel(trend)
        trend_color = "#10b981" if trend_positive else "#ef4444"
        trend_lbl.setStyleSheet(f"color: {trend_color}; font-size: 11px; font-weight: 700;")
        layout.addWidget(trend_lbl)

class StatsWidget(QFrame):
    """
    Displays 'Focus Reflection' stats: Deep Work, Flow State, and Daily Goal.
    Matches the 'Tech Variant' design.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: transparent; border: none; font-family: 'Segoe UI', sans-serif;")
        # self.setFixedHeight(180) # Removed fixed height to allow auto-grow
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 12, 16, 4)
        main_layout.setSpacing(10)
        
        # HEADER
        header = QLabel("Focus Reflection")
        header.setStyleSheet("color: #f8fafc; font-size: 14px; font-weight: 800; letter-spacing: 0.5px;")
        main_layout.addWidget(header)
        
        # CARDS ROW
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(8)
        
        self.card_deep_work = StatCard("Deep Work", "⚡", "4.5 hrs", "+15% vs yday")
        self.card_flow = StatCard("Flow State", "🌊", "2 sessions", "+1 streak")
        
        cards_layout.addWidget(self.card_deep_work)
        cards_layout.addWidget(self.card_flow)
        main_layout.addLayout(cards_layout)
        
        # PROGRESS SECTION
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(59, 130, 246, 0.1); 
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 8px;
            }
        """)
        p_layout = QVBoxLayout(progress_frame)
        p_layout.setContentsMargins(12, 10, 12, 10)
        p_layout.setSpacing(4)
        
        # Top Row
        top_row = QHBoxLayout()
        goal_title = QLabel("Daily Focus Goal")
        goal_title.setStyleSheet("color: #f8fafc; font-size: 12px; font-weight: 600; background: transparent; border: none;")
        
        goal_val = QLabel("6h 30m")
        goal_val.setStyleSheet("color: #3b82f6; font-size: 12px; font-weight: 800; background: transparent; border: none;")
        
        top_row.addWidget(goal_title)
        top_row.addStretch()
        top_row.addWidget(goal_val)
        p_layout.addLayout(top_row)
        
        # Bar
        self.bar = QProgressBar()
        self.bar.setFixedHeight(6)
        self.bar.setTextVisible(False)
        self.bar.setValue(75)
        self.bar.setStyleSheet("""
            QProgressBar {
                background-color: #334155;
                border-radius: 3px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #3b82f6;
                border-radius: 3px;
            }
        """)
        p_layout.addWidget(self.bar)
        
        # Subtitle
        sub = QLabel("75% of your daily goal achieved")
        sub.setStyleSheet("color: #94a3b8; font-size: 11px; background: transparent; border: none;")
        p_layout.addWidget(sub)
        
        main_layout.addWidget(progress_frame)
