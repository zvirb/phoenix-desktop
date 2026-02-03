
import logging
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStackedWidget, QFrame
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, Qt

logger = logging.getLogger(__name__)

from phoenix.core.token_manager import TokenManager
from config import config

class MissionControlWindow(QMainWindow):
    """
    The Mission Control Interface.
    Integrates the rich HTML/JS prototypes for War Room, Gamification, and Cognitive Cockpit.
    Auto-injects authentication from the main desktop app.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Phoenix Mission Control")
        self.resize(1280, 800)
        self.token_manager = TokenManager()
        
        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # Navigation Sidebar using Native Widgets
        self.sidebar = QFrame()
        self.sidebar.setObjectName("MissionSidebar")
        self.sidebar.setFixedWidth(80)
        self.sidebar.setStyleSheet("""
            QFrame#MissionSidebar {
                background-color: #0f172a; /* Slate 900 */
                border-right: 1px solid #1e293b;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 10px;
                padding: 10px;
                color: #64748b;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #1e293b;
                color: #f8fafc;
            }
            QPushButton:checked {
                background-color: #2563eb; /* Primary Blue */
                color: #ffffff;
            }
        """)
        
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(10, 20, 10, 20)
        self.sidebar_layout.setSpacing(15)
        
        # Buttons
        self.btn_war_room = self.create_nav_button("War Room", "shield")
        self.btn_rpg = self.create_nav_button("Hero Loop", "swords") 
        self.btn_focus = self.create_nav_button("Cognitive", "psychology") 
        
        self.sidebar_layout.addWidget(self.btn_war_room)
        self.sidebar_layout.addWidget(self.btn_rpg)
        self.sidebar_layout.addWidget(self.btn_focus)
        self.sidebar_layout.addStretch()
        
        self.main_layout.addWidget(self.sidebar)
        
        # Content Area (WebStack)
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        # Initialize Views
        self.views = {}
        self.add_web_view("war_room", "war_room__stack_variant/code.html")
        self.add_web_view("rpg", "hero_rpg__cyber_variant/code.html")
        self.add_web_view("focus", "cognitive_cockpit__pro_variant/code.html")
        
        # Connect Signals
        self.btn_war_room.clicked.connect(lambda: self.switch_tab("war_room"))
        self.btn_rpg.clicked.connect(lambda: self.switch_tab("rpg"))
        self.btn_focus.clicked.connect(lambda: self.switch_tab("focus"))
        
        # Default View
        self.btn_war_room.click()

    def create_nav_button(self, tooltip, icon_name):
        btn = QPushButton()
        btn.setToolTip(tooltip)
        btn.setCheckable(True)
        # Using simple text for now, could use icon later if Material Symbols font is loaded in Qt
        # Or simple unicode
        icons = {
            "shield": "🛡️",
            "swords": "⚔️",
            "psychology": "🧠"
        }
        btn.setText(icons.get(icon_name, "?"))
        btn.setFont(btn.font()) 
        f = btn.font()
        f.setPointSize(20)
        btn.setFont(f)
        return btn

    def add_web_view(self, key, relative_path):
        """Add a web view to the stack."""
        view = QWebEngineView()
        # Set Dark Background to avoid white flash
        view.page().setBackgroundColor(Qt.GlobalColor.black)
        
        # Load File
        base_path = Path(__file__).parent.parent.parent / "assets" / "web"
        file_path = base_path / relative_path
        
        if file_path.exists():
            url = QUrl.fromLocalFile(str(file_path.absolute()))
            view.load(url)
            # Inject Token on Load
            view.loadFinished.connect(lambda: self.inject_auth(view))
        else:
            logger.error(f"HTML file not found: {file_path}")
            view.setHtml(f"<h1 style='color:white'>Error: File not found: {relative_path}</h1>")
            
        self.stack.addWidget(view)
        self.views[key] = view

    def switch_tab(self, key):
        """Switch the active view."""
        # Uncheck all
        self.btn_war_room.setChecked(False)
        self.btn_rpg.setChecked(False)
        self.btn_focus.setChecked(False)
        
        # Check active
        if key == "war_room": self.btn_war_room.setChecked(True)
        if key == "rpg": self.btn_rpg.setChecked(True)
        if key == "focus": self.btn_focus.setChecked(True)
        
        # Switch Interface
        if key in self.views:
            self.stack.setCurrentWidget(self.views[key])

    def inject_auth(self, view):
        """Inject the current session token into the web view's localStorage."""
        token = self.token_manager.get_token()
        if token:
            js = f"""
            localStorage.setItem('phoenix_access_token', '{token}');
            localStorage.setItem('phoenix_core_url', '{config.PHOENIX_API_URL}');
            console.log('Phoenix Desktop: Token injected successfully for {config.PHOENIX_API_URL}');
            if (window.phoenixAPI) {{
                window.phoenixAPI.token = '{token}';
            }}
            """
            view.page().runJavaScript(js)
