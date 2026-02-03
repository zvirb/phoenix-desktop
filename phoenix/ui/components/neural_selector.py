from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel, QFrame, QScrollArea
from PyQt6.QtCore import Qt, QSize

class NeuralCoreBtn(QPushButton):
    def __init__(self, name, icon, is_active=False):
        super().__init__()
        self.setFixedSize(80, 60)
        self.setCheckable(True)
        self.setChecked(is_active)
        
        # We use a layout for Icon + Text
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.icon_lbl = QLabel(icon)
        self.icon_lbl.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        self.icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.name_lbl = QLabel(name)
        self.name_lbl.setStyleSheet("font-size: 10px; font-weight: 600; background: transparent; border: none;")
        self.name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.icon_lbl)
        layout.addWidget(self.name_lbl)
        
        self.update_style()
        self.toggled.connect(self.update_style)

    def update_style(self):
        if self.isChecked():
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(59, 130, 246, 0.2);
                    border: 1px solid #3b82f6;
                    border-radius: 8px;
                }
                QLabel { color: #ffffff; }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    border: 1px solid #334155;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: #334155;
                }
                QLabel { color: #94a3b8; }
            """)

class NeuralSelector(QFrame):
    """
    Carousel for selecting the active 'Neural Core'.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self.setStyleSheet("background: transparent; border: none;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 0, 12, 12)
        main_layout.setSpacing(4)
        
        # Label
        lbl = QLabel("NEURAL CORE")
        lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 700; letter-spacing: 1px;")
        main_layout.addWidget(lbl)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.setSpacing(8)
        
        # Cores
        self.cores = [
            ("Logic", "🧠"),
            ("Creative", "🎨"),
            ("Focus", "⚡"),
            ("Comms", "💬"),
            ("Secure", "🛡️"),
        ]
        
        self.btns = []
        for i, (name, icon) in enumerate(self.cores):
            # First one active by default for demo
            btn = NeuralCoreBtn(name, icon, is_active=(i==0))
            # Logic to ensure only one is active?
            btn.clicked.connect(lambda ch, b=btn: self.on_core_selected(b))
            h_layout.addWidget(btn)
            self.btns.append(btn)
            
        h_layout.addStretch()
        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def on_core_selected(self, active_btn):
        # Mutually exclusive
        for btn in self.btns:
            if btn != active_btn:
                btn.blockSignals(True)
                btn.setChecked(False)
                btn.update_style()
                btn.blockSignals(False)
            else:
                btn.setChecked(True)
                btn.update_style()
from PyQt6.QtWidgets import QVBoxLayout
