"""
Unit tests for token_manager module.
Tests Windows Credential Manager integration.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestTokenManager:
    """Test the TokenManager class."""

    @patch('token_manager.win32cred')
    @patch('token_manager.config')
    def test_initialization(self, mock_config, mock_cred):
        """Test token manager initializes."""
        mock_config.DEVICE_ID = "test-device"
        from token_manager import TokenManager

        manager = TokenManager()
        assert manager is not None

    @patch('token_manager.win32cred')
    @patch('token_manager.win32con')
    @patch('token_manager.config')
    def test_store_token(self, mock_config, mock_win32con, mock_cred):
        """Test storing a token."""
        mock_config.DEVICE_ID = "test-device"
        mock_win32con.CRED_TYPE_GENERIC = 1
        mock_win32con.CRED_PERSIST_LOCAL_MACHINE = 2
        mock_cred.CredWrite = Mock(return_value=None)

        from token_manager import TokenManager

        manager = TokenManager()
        # store_token returns None, not a boolean
        manager.save_token("test_token_12345")

        mock_cred.CredWrite.assert_called_once()

    @patch('token_manager.win32cred')
    @patch('token_manager.win32con')
    @patch('token_manager.config')
    def test_get_token_success(self, mock_config, mock_win32con, mock_cred):
        """Test getting a token successfully."""
        mock_config.DEVICE_ID = "test-device"
        mock_win32con.CRED_TYPE_GENERIC = 1

        # Mock credential read - return bytes that will be decoded
        mock_cred_data = {
            'CredentialBlob': 'test_token_12345'
        }
        mock_cred.CredRead = Mock(return_value=mock_cred_data)

        from token_manager import TokenManager

        manager = TokenManager()
        token = manager.get_token()

        assert token == "test_token_12345"

    @patch('token_manager.win32cred')
    @patch('token_manager.win32con')
    @patch('token_manager.config')
    def test_get_token_not_found(self, mock_config, mock_win32con, mock_cred):
        """Test getting token when not found."""
        mock_config.DEVICE_ID = "test-device"
        mock_win32con.CRED_TYPE_GENERIC = 1

        # Mock credential not found - raises exception
        mock_cred.CredRead = Mock(side_effect=Exception("Element not found"))

        from token_manager import TokenManager

        manager = TokenManager()
        token = manager.get_token()

        assert token is None

    @patch('token_manager.win32cred')
    @patch('token_manager.win32con')
    @patch('token_manager.config')
    def test_delete_token(self, mock_config, mock_win32con, mock_cred):
        """Test deleting a token."""
        mock_config.DEVICE_ID = "test-device"
        mock_win32con.CRED_TYPE_GENERIC = 1
        mock_cred.CredDelete = Mock(return_value=None)

        from token_manager import TokenManager

        manager = TokenManager()
        # delete_token returns None, not a boolean
        manager.delete_token()

        mock_cred.CredDelete.assert_called_once()

    @patch('token_manager.win32cred')
    @patch('token_manager.win32con')
    @patch('token_manager.config')
    def test_has_token_true(self, mock_config, mock_win32con, mock_cred):
        """Test has_token returns True when token exists."""
        mock_config.DEVICE_ID = "test-device"
        mock_win32con.CRED_TYPE_GENERIC = 1
        mock_cred_data = {'CredentialBlob': 'token'}
        mock_cred.CredRead = Mock(return_value=mock_cred_data)

        from token_manager import TokenManager

        manager = TokenManager()
        assert manager.has_token() is True

    @patch('token_manager.win32cred')
    @patch('token_manager.win32con')
    @patch('token_manager.config')
    def test_has_token_false(self, mock_config, mock_win32con, mock_cred):
        """Test has_token returns False when no token."""
        mock_config.DEVICE_ID = "test-device"
        mock_win32con.CRED_TYPE_GENERIC = 1

        # Mock credential not found
        mock_cred.CredRead = Mock(side_effect=Exception("Element not found"))

        from token_manager import TokenManager

        manager = TokenManager()
        assert manager.has_token() is False


class TestTokenSecurity:
    """Test token security features."""

    @patch('token_manager.win32cred')
    @patch('token_manager.win32con')
    @patch('token_manager.config')
    def test_token_stored_with_credential_manager(self, mock_config, mock_win32con, mock_cred):
        """Test token is stored via Windows Credential Manager."""
        mock_config.DEVICE_ID = "test-device"
        mock_win32con.CRED_TYPE_GENERIC = 1
        mock_win32con.CRED_PERSIST_LOCAL_MACHINE = 2
        mock_cred.CredWrite = Mock()

        from token_manager import TokenManager

        manager = TokenManager()
        manager.save_token("my_token")

        # Verify CredWrite was called
        call_args = mock_cred.CredWrite.call_args
        assert call_args is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
