import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock dependencies before importing gui_settings
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.font'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()
sys.modules['tkinter.simpledialog'] = MagicMock()
sys.modules['windows_settings'] = MagicMock()
sys.modules['token_manager'] = MagicMock()
sys.modules['phoenix_logging'] = MagicMock()

# Now import the module under test
# We need to reload it if it was already imported, but for a fresh process it's fine.
# However, since we are mocking modules that are imported at top level, we need to be careful.
# gui_settings imports:
# from windows_settings import settings_manager
# from token_manager import TokenManager
# from phoenix_logging import get_logger, logged_method, log_exception

# So we need to set up the mocks to have these attributes
sys.modules['windows_settings'].settings_manager = MagicMock()
sys.modules['token_manager'].TokenManager = MagicMock()
sys.modules['phoenix_logging'].get_logger = MagicMock()
sys.modules['phoenix_logging'].logged_method = lambda x: x # Identity decorator
sys.modules['phoenix_logging'].log_exception = MagicMock()

import gui_settings

class TestModernSettingsWindow(unittest.TestCase):
    def setUp(self):
        # Reset the class if needed, but we are creating a new instance
        self.window = gui_settings.ModernSettingsWindow()
        # Mock the window object
        self.window.window = MagicMock()
        # Ensure colors are set (they are set in __init__)
        
    def test_create_text_field_stores_var(self):
        parent = MagicMock()
        self.window.settings_state = {}
        
        # Mock StringVar to verify it's the one being stored
        mock_var = MagicMock()
        
        # We need to patch tkinter.StringVar inside gui_settings
        # But gui_settings imports tkinter as tk
        # So we patch gui_settings.tk.StringVar
        
        with patch('gui_settings.tk.StringVar', return_value=mock_var):
            self.window._create_text_field(parent, "Label", "test_field")
            
        # Check if var is stored in text_vars
        self.assertTrue(hasattr(self.window, 'text_vars'), "text_vars attribute should exist")
        self.assertIn("test_field", self.window.text_vars)
        self.assertEqual(self.window.text_vars["test_field"], mock_var)
        
    def test_create_checkbox_stores_var(self):
        parent = MagicMock()
        self.window.settings_state = {}
        
        mock_var = MagicMock()
        with patch('gui_settings.tk.BooleanVar', return_value=mock_var):
            self.window._create_checkbox(parent, "Label", "test_check")
            
        self.assertTrue(hasattr(self.window, 'checkboxes'))
        self.assertIn("test_check", self.window.checkboxes)
        self.assertEqual(self.window.checkboxes["test_check"], mock_var)

    def test_create_dropdown_stores_var(self):
        parent = MagicMock()
        self.window.settings_state = {}
        
        mock_var = MagicMock()
        with patch('gui_settings.tk.StringVar', return_value=mock_var):
            # Dropdown also needs ttk.Combobox
            with patch('gui_settings.ttk.Combobox'):
                self.window._create_dropdown(parent, "Label", "test_drop", ["A", "B"])
            
        self.assertTrue(hasattr(self.window, 'dropdowns'))
        self.assertIn("test_drop", self.window.dropdowns)
        self.assertEqual(self.window.dropdowns["test_drop"], mock_var)

if __name__ == '__main__':
    unittest.main()
