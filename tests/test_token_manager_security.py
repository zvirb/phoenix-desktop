import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mock Windows-specific modules for Linux environment
sys.modules['winreg'] = MagicMock()
sys.modules['win32cred'] = MagicMock()
sys.modules['win32con'] = MagicMock()

# Add repo root to path so we can import phoenix
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phoenix.core.token_manager import TokenManager

class TestTokenManagerSecurity(unittest.TestCase):

    @patch('builtins.input')
    @patch('getpass.getpass')
    @patch.object(TokenManager, 'save_token')
    def test_setup_wizard_uses_getpass(self, mock_save_token, mock_getpass, mock_input):
        """Verify that setup_wizard uses getpass for sensitive token entry."""

        # Setup mocks
        mock_getpass.return_value = "secure_token_123_very_long_indeed"
        mock_input.return_value = "should_not_be_used_for_token"
        mock_save_token.return_value = True

        # Initialize manager
        manager = TokenManager()

        # Run wizard
        print("\nRunning TokenManager.setup_wizard()...")
        result = manager.setup_wizard()

        # Verify
        self.assertTrue(result)

        # Check that getpass was called
        # In the vulnerable code, this will fail because input() is used instead
        if mock_getpass.call_count == 0:
             print("\n⚠️  VULNERABILITY DETECTED: getpass.getpass was not called!")
        else:
             print("\n✅ SECURE: getpass.getpass was called.")

        mock_getpass.assert_called_once()

        # Check that builtins.input was NOT called
        mock_input.assert_not_called()

if __name__ == '__main__':
    unittest.main()
