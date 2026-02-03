
import logging
from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QWidget, QMessageBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtCore import QUrl, pyqtSignal, Qt

from config import config

logger = logging.getLogger(__name__)

class SettingsPage(QWebEnginePage):
    close_signal = pyqtSignal()
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if message.startswith("PHOENIX_DIALOG_CLOSE:TRUE"):
            self.close_signal.emit()
            
class SettingsDialog(QDialog):
    """
    Web-based Settings Dialog.
    Replaces native UI with "Full Concept" HTML.
    Currently View-Only for complex settings, but functional for closing.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Phoenix Settings")
        self.setFixedSize(500, 700) # Increased size for HTML content
        self.setStyleSheet("background-color: #111621;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.view = QWebEngineView()
        self.page = SettingsPage(self.view)
        self.view.setPage(self.page)
        self.view.page().setBackgroundColor(Qt.GlobalColor.black)
        
        self.layout.addWidget(self.view)
        
        self.page.close_signal.connect(self.accept)
        
        self.load_interface()

    def load_interface(self):
        base_path = Path(__file__).parent.parent.parent / "assets" / "web"
        file_path = base_path / "phoenix_agent_settings" / "code.html"
        
        if file_path.exists():
            url = QUrl.fromLocalFile(str(file_path.absolute()))
            self.view.load(url)
        else:
            self.view.setHtml("<h1>Error: Settings Interface Not Found</h1>")
