"""
Entry point for the Settings GUI.
Redirects to the new CustomTkinter implementation in gui/main_window.py
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.main_window import ModernSettingsWindow

if __name__ == "__main__":
    app = ModernSettingsWindow()
    app.mainloop()
