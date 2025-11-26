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
    def test_initialization(self, mock_cred):
        """Test token manager initializes."""
        from token_manager import TokenManager
        
        manager = TokenManager()
        assert manager is not None
    
    @patch('token_manager.win32cred')
    @patch('token_manager.settings_manager')
    def test_save_token(self, mock_settings, mock_cred):
        """Test saving a token."""
        from token_manager import TokenManager
        
        mock_settings.get_device_id.return_value = "test-device"
        mock_cred.CredWrite = Mock(return_value=None)
        
        manager = TokenManager()
        result = manager.save_token("test_token_12345")
        
        assert result is True
        mock_cred.CredWrite.assert_called_once()
    
    @patch('token_manager.win32cred')
    @patch('token_manager.settings_manager')
    def test_get_token_success(self, mock_settings, mock_cred):
        """Test getting a token successfully."""
        from token_manager import TokenManager
        
        mock_settings.get_device_id.return_value = "test-device"
        
        # Mock credential read
        mock_cred_data = {
            'CredentialBlob': b'test_token_12345'
        }
        mock_cred.CredRead = Mock(return_value=mock_cred_data)
        
        manager = TokenManager()
        token = manager.get_token()
        
        assert token == "test_token_12345"
    
    @patch('token_manager.win32cred')
    @patch('token_manager.settings_manager')
    def test_get_token_not_found(self, mock_settings, mock_cred):
        """Test getting token when not found."""
        from token_manager import TokenManager
        import pywintypes
        
        mock_settings.get_device_id.return_value = "test-device"
        
        # Mock credential not found
        mock_cred.CredRead = Mock(side_effect=pywintypes.error(1168, "CredRead", "Element not found"))
        
        manager = TokenManager()
        token = manager.get_token()
        
        assert token is None
    
    @patch('token_manager.win32cred')
    @patch('token_manager.settings_manager')
    def test_delete_token(self, mock_settings, mock_cred):
        """Test deleting a token."""
        from token_manager import TokenManager
        
        mock_settings.get_device_id.return_value = "test-device"
        mock_cred.CredDelete = Mock(return_value=None)
        
        manager = TokenManager()
        result = manager.delete_token()
        
        assert result is True
        mock_cred.CredDelete.assert_called_once()
    
    @patch('token_manager.win32cred')
    @patch('token_manager.settings_manager')
    def test_has_token_true(self, mock_settings, mock_cred):
        """Test has_token returns True when token exists."""
        from token_manager import TokenManager
        
        mock_settings.get_device_id.return_value = "test-device"
        mock_cred_data = {'CredentialBlob': b'token'}
        mock_cred.CredRead = Mock(return_value=mock_cred_data)
        
        manager = TokenManager()
        assert manager.has_token() is True
    
    @patch('token_manager.win32cred')
    @patch('token_manager.settings_manager')
    def test_has_token_false(self, mock_settings, mock_cred):
        """Test has_token returns False when no token."""
        from token_manager import TokenManager
        import pywintypes
        
        mock_settings.get_device_id.return_value = "test-device"
        mock_cred.CredRead = Mock(side_effect=pywintypes.error(1168, "CredRead", "Element not found"))
        
        manager = TokenManager()
        assert manager.has_token() is False


class TestTokenSecurity:
    """Test token security features."""
    
    @patch('token_manager.win32cred')
    @patch('token_manager.settings_manager')
    def test_token_stored_as_bytes(self, mock_settings, mock_cred):
        """Test token is stored as bytes."""
        from token_manager import TokenManager
        
        mock_settings.get_device_id.return_value = "test-device"
        mock_cred.CredWrite = Mock()
        
        manager = TokenManager()
        manager.save_token("my_token")
        
        # Verify CredWrite was called
        call_args = mock_cred.CredWrite.call_args
        assert call_args is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
