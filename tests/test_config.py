"""
Unit tests for config module.
Tests configuration management.
"""
import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestConfig:
    """Test the Config class."""
    
    @patch('config.settings_manager')
    def test_phoenix_api_url(self, mock_settings):
        """Test PHOENIX_API_URL property."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = "https://test.phoenix.com"
        
        config = Config()
        assert config.PHOENIX_API_URL == "https://test.phoenix.com"
    
    @patch('config.settings_manager')
    def test_device_id(self, mock_settings):
        """Test DEVICE_ID property."""
        from config import Config
        
        mock_settings.get_device_id.return_value = "test-device-123"
        
        config = Config()
        assert config.DEVICE_ID == "test-device-123"
    
    @patch('config.settings_manager')
    def test_capture_interval(self, mock_settings):
        """Test CAPTURE_INTERVAL property."""
        from config import Config
        
        mock_settings.get_capture_interval.return_value = 60
        
        config = Config()
        assert config.CAPTURE_INTERVAL == 60
    
    @patch('config.settings_manager')
    def test_heartbeat_interval(self, mock_settings):
        """Test HEARTBEAT_INTERVAL property."""
        from config import Config
        
        mock_settings.get_heartbeat_interval.return_value = 120
        
        config = Config()
        assert config.HEARTBEAT_INTERVAL == 120
    
    @patch('config.settings_manager')
    def test_similarity_threshold(self, mock_settings):
        """Test SIMILARITY_THRESHOLD property."""
        from config import Config
        
        mock_settings.get_similarity_threshold.return_value = 0.95
        
        config = Config()
        assert config.SIMILARITY_THRESHOLD == 0.95
    
    @patch('config.settings_manager')
    def test_gaming_processes(self, mock_settings):
        """Test GAMING_PROCESSES property."""
        from config import Config
        
        mock_settings.get_setting.return_value = ['steam.exe', 'game.exe']
        
        config = Config()
        processes = config.GAMING_PROCESSES
        
        assert 'steam.exe' in processes
        assert 'game.exe' in processes
    
    @patch('config.settings_manager')
    def test_max_image_width(self, mock_settings):
        """Test MAX_IMAGE_WIDTH property."""
        from config import Config
        
        mock_settings.get_setting.return_value = 1024
        
        config = Config()
        assert config.MAX_IMAGE_WIDTH == 1024
    
    @patch('config.settings_manager')
    def test_jpeg_quality(self, mock_settings):
        """Test JPEG_QUALITY property."""
        from config import Config
        
        mock_settings.get_setting.return_value = 70
        
        config = Config()
        assert config.JPEG_QUALITY == 70
    
    @patch('config.settings_manager')
    def test_verify_ssl(self, mock_settings):
        """Test VERIFY_SSL property."""
        from config import Config
        
        mock_settings.get_verify_ssl.return_value = True
        
        config = Config()
        assert config.VERIFY_SSL is True
    
    @patch('config.settings_manager')
    def test_heartbeat_url(self, mock_settings):
        """Test heartbeat_url property."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = "https://test.com"
        
        config = Config()
        assert config.heartbeat_url == "https://test.com/api/screentime/heartbeat"
    
    @patch('config.settings_manager')
    def test_capture_url(self, mock_settings):
        """Test capture_url property."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = "https://test.com/"
        
        config = Config()
        assert config.capture_url == "https://test.com/api/screentime/capture"


class TestConfigValidation:
    """Test configuration validation."""
    
    @patch('config.settings_manager')
    def test_validate_success(self, mock_settings):
        """Test successful validation."""
        from config import Config
        
        # Set up valid config
        mock_settings.get_phoenix_url.return_value = "https://valid.com"
        mock_settings.get_capture_interval.return_value = 60
        mock_settings.get_similarity_threshold.return_value = 0.95
        mock_settings.get_setting.side_effect = lambda key, default: {
            'jpeg_quality': 70
        }.get(key, default)
        
        config = Config()
        # Should not raise
        config.validate()
    
    @patch('config.settings_manager')
    def test_validate_missing_url(self, mock_settings):
        """Test validation fails with missing URL."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = None
        
        config = Config()
        with pytest.raises(ValueError, match="PHOENIX_API_URL must be set"):
            config.validate()
    
    @patch('config.settings_manager')
    def test_validate_non_https(self, mock_settings):
        """Test validation fails with non-HTTPS URL."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = "http://insecure.com"
        
        config = Config()
        with pytest.raises(ValueError, match="must use HTTPS"):
            config.validate()
    
    @patch('config.settings_manager')
    def test_validate_allows_localhost(self, mock_settings):
        """Test validation allows localhost HTTP."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = "http://localhost:8000"
        mock_settings.get_capture_interval.return_value = 60
        mock_settings.get_similarity_threshold.return_value = 0.95
        mock_settings.get_setting.side_effect = lambda key, default: {
            'jpeg_quality': 70
        }.get(key, default)
        
        config = Config()
        # Should not raise
        config.validate()
    
    @patch('config.settings_manager')
    def test_validate_low_capture_interval(self, mock_settings):
        """Test validation fails with low capture interval."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = "https://valid.com"
        mock_settings.get_capture_interval.return_value = 5
        
        config = Config()
        with pytest.raises(ValueError, match="at least 10 seconds"):
            config.validate()
    
    @patch('config.settings_manager')
    def test_validate_invalid_threshold(self, mock_settings):
        """Test validation fails with invalid threshold."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = "https://valid.com"
        mock_settings.get_capture_interval.return_value = 60
        mock_settings.get_similarity_threshold.return_value = 1.5
        
        config = Config()
        with pytest.raises(ValueError, match="between 0 and 1"):
            config.validate()
    
    @patch('config.settings_manager')
    def test_validate_invalid_jpeg_quality(self, mock_settings):
        """Test validation fails with invalid JPEG quality."""
        from config import Config
        
        mock_settings.get_phoenix_url.return_value = "https://valid.com"
        mock_settings.get_capture_interval.return_value = 60
        mock_settings.get_similarity_threshold.return_value = 0.95
        mock_settings.get_setting.side_effect = lambda key, default: {
            'jpeg_quality': 150
        }.get(key, default)
        
        config = Config()
        with pytest.raises(ValueError, match="between 1 and 100"):
            config.validate()


class TestGlobalConfigInstance:
    """Test the global config instance."""
    
    def test_config_instance_exists(self):
        """Test that global config instance exists."""
        from config import config
        
        assert config is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
