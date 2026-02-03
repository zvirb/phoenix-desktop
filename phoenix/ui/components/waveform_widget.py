from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QPainter, QColor, QBrush
import random

class EqualizerBar(QWidget):
    """A single vertical bar for the equalizer."""
    def __init__(self, color="#3b82f6"):
        super().__init__()
        self.setFixedWidth(4)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.max_height = 40
        self.current_height = 4
        self.target_height = 4
        self.color = color
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(self.color)))
        painter.setPen(Qt.PenStyle.NoPen)
        
        # Draw relative to widget height (bottom align)
        h = int(self.current_height)
        w = self.width()
        # x, y, w, h
        painter.drawRoundedRect(0, self.height() - h, w, h, 2, 2)
        
    def update_height(self):
        # Move towards target
        diff = self.target_height - self.current_height
        if abs(diff) < 1:
            self.current_height = self.target_height
        else:
            # Smooth interpolation
            self.current_height += diff * 0.2

        self.update()

class WaveformWidget(QFrame):
    """
    Visualizer for 'Audio Stream Analysis'.
    Simulates a live EQ or accepts real levels.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #0f172a;
                border: 1px solid #1e293b;
                border-radius: 12px;
            }
            QLabel { background: transparent; border: none; font-family: 'Segoe UI', sans-serif; }
        """)
        self.setFixedHeight(120) # Ensure it has height
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Header
        h_layout = QHBoxLayout()
        title = QLabel("Audio Stream Analysis")
        title.setStyleSheet("color: #f8fafc; font-weight: 700; font-size: 13px;")
        
        icon = QLabel("graphic_eq") # Material Icon text
        icon.setText("🎤") 
        icon.setStyleSheet("color: #94a3b8; font-size: 14px;")
        
        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(icon)
        layout.addLayout(h_layout)
        
        # Visualizer Area
        vis_container = QFrame()
        vis_container.setStyleSheet("background-color: #020617; border-radius: 8px;")
        vis_container.setFixedHeight(60)
        
        v_layout = QHBoxLayout(vis_container)
        v_layout.setContentsMargins(8, 8, 8, 8)
        v_layout.setSpacing(3)
        v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.bars = []
        for i in range(20):
            # Gradient colors from blue to purple
            color = "#3b82f6"
            if i > 10: color = "#8b5cf6"
            if i > 15: color = "#d946ef"
            
            bar = EqualizerBar(color)
            v_layout.addWidget(bar)
            self.bars.append(bar)
            
        layout.addWidget(vis_container)
        
        # Footer / Live Indicator
        f_layout = QHBoxLayout()
        self.dot = QLabel("●")
        self.dot.setStyleSheet("color: #334155; font-size: 10px;") # Default Inactive
        
        self.live_lbl = QLabel("Click to Record")
        self.live_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 700; text-transform: uppercase;")
        
        self.status_lbl = QLabel("Ready")
        self.status_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-style: italic;")
        
        f_layout.addWidget(self.dot)
        f_layout.addWidget(self.live_lbl)
        f_layout.addSpacing(8)
        f_layout.addWidget(self.status_lbl)
        f_layout.addStretch()
        
        layout.addLayout(f_layout)
        
        # Animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        
        self.dot_timer = QTimer(self)
        self.dot_timer.timeout.connect(self._pulse_dot)
        
        self.is_recording = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dot_visible = True # Initialize for _pulse_dot

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle_recording()
            
    def toggle_recording(self):
        self.is_recording = not self.is_recording
        
        # Emit signal to parent (MainWindow) to handle logic
        if self.parent() and hasattr(self.parent(), 'toggle_audio_recording'):
            self.parent().toggle_audio_recording(self.is_recording)
            
        self.update_ui_state()
        
    def update_ui_state(self):
        if self.is_recording:
            self.live_lbl.setText("REC")
            self.live_lbl.setStyleSheet("color: #ef4444; font-size: 10px; font-weight: bold;")
            self.status_lbl.setText("Listening...")
            self.dot_timer.start(500) # Fast pulse
            self.timer.start(30)
            self.dot.setStyleSheet("color: #ef4444; font-size: 10px;")
            # KEEP SUBTLE: No border change, just standard look
            self.setStyleSheet("""
                QFrame {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 12px;
                }
                QLabel { background: transparent; border: none; font-family: 'Segoe UI', sans-serif; }
            """)
        else:
            self.live_lbl.setText("Start")
            self.live_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 600;")
            self.status_lbl.setText("Ready")
            self.dot_timer.stop()
            self.timer.stop()
            self.dot.setStyleSheet("color: #334155; font-size: 10px;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #0f172a;
                    border: 1px solid #1e293b;
                    border-radius: 12px;
                }
                QLabel { background: transparent; border: none; font-family: 'Segoe UI', sans-serif; }
            """)
            # Reset Bars
            for bar in self.bars:
                bar.target_height = 4
                bar.current_height = 4
                bar.update()

    def set_levels(self, levels):
        # Only update if recording
        if not self.is_recording: return
        
        for i, level in enumerate(levels):
            if i >= len(self.bars): break
            h = max(4, level * 40)
            self.bars[i].target_height = h

    def set_active(self, active):
        # Deprecated: usage handled by toggle_recording
        pass

    def _animate(self):
        for bar in self.bars:
            bar.update_height()
        self.update()

    def _pulse_dot(self):
        self.dot_visible = not self.dot_visible
        # Toggle color transparency to keep layout stable
        color = "#ef4444" if self.dot_visible else "transparent"
        self.dot.setStyleSheet(f"color: {color}; font-size: 10px;")
