
import logging
import json
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, pyqtSignal, Qt

from phoenix.core.token_manager import TokenManager
from config import config

logger = logging.getLogger(__name__)

class OnboardingPage(QWebEnginePage):
    """Custom Page to intercept console messages."""
    token_signal = pyqtSignal(dict)

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if message.startswith("PHOENIX_ONBOARDING_SAVE:"):
            try:
                json_str = message.replace("PHOENIX_ONBOARDING_SAVE:", "", 1)
                data = json.loads(json_str)
                self.token_signal.emit(data)
            except Exception as e:
                logger.error(f"Failed to parse onboarding signal: {e}")
        # super().javaScriptConsoleMessage(level, message, lineNumber, sourceID) # Optional: Forward to stdout

class OnboardingView(QWidget):
    """
    Web-based Onboarding Wizard providing "Full Concept" fidelity.
    Integrates with TokenManager via Console Bridge.
    """
    token_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Web View
        self.view = QWebEngineView()
        self.page = OnboardingPage(self.view)
        self.view.setPage(self.page)
        
        # Set Dark Background
        self.view.page().setBackgroundColor(Qt.GlobalColor.black)
        
        self.layout.addWidget(self.view)
        
        # Connect Signals
        self.page.token_signal.connect(self.on_token_received)
        
        # Load Content
        self.load_interface()

    def load_interface(self):
        base_path = Path(__file__).parent.parent.parent / "assets" / "web"
        file_path = base_path / "phoenix_desktop_onboarding" / "code.html"
        
        if file_path.exists():
            url = QUrl.fromLocalFile(str(file_path.absolute()))
            self.view.load(url)
        else:
            self.view.setHtml("<h1>Error: Onboarding Interface Not Found</h1>")

    def on_token_received(self, data):
        """Handle token data received from JS."""
        logger.info("Received Onboarding Token Signal")
        
        token = data.get('token') # This is the session token (JWT)
        device_token = data.get('device_token') # The permanent device token
        core_url = data.get('core_url')
        
        if not device_token:
            return

        # 1. Save Device Token Securely
        manager = TokenManager()
        if manager.save_token(device_token):
             logger.info("Device Token Saved Securely")
             self.token_saved.emit()
        else:
             logger.error("Failed to save device token")
        
        # 2. Save Phoenix URL
        if core_url:
             try:
                 from windows_settings import settings_manager
                 settings_manager.save_phoenix_url(core_url)
                 logger.info(f"Saved Phoenix URL: {core_url}")
             except Exception as e:
                 logger.error(f"Failed to save URL: {e}")
