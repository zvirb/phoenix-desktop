"""
Unit tests for windows_settings module.
Tests Windows Registry integration.
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from windows_settings import WindowsSettingsManager


class TestWindowsSettingsManager:
    """Test the WindowsSettingsManager class."""
    
    @pytest.fixture
    def settings_manager(self):
        """Create a settings manager instance for testing."""
        manager = WindowsSettingsManager()
        # Use a test prefix to avoid conflicts
        manager.REGISTRY_PATH = r"Software\PhoenixTrackerTest"
        manager._ensure_registry_key()
        yield manager
        # Cleanup after tests
        try:
            manager.clear_all_settings()
        except:
            pass
    
    def test_initialization(self, settings_manager):
        """Test settings manager initializes."""
        assert settings_manager is not None
        assert settings_manager.REGISTRY_PATH.endswith("Test")
    
    def test_save_and_get_string(self, settings_manager):
        """Test saving and retrieving string values."""
        settings_manager.save_setting("test_string", "Hello World")
        value = settings_manager.get_setting("test_string")
        
        assert value == "Hello World"
    
    def test_save_and_get_int(self, settings_manager):
        """Test saving and retrieving integer values."""
        settings_manager.save_setting("test_int", 42)
        value = settings_manager.get_setting("test_int")
        
        assert value == 42
        assert isinstance(value, int)
    
    def test_save_and_get_bool(self, settings_manager):
        """Test saving and retrieving boolean values."""
        settings_manager.save_setting("test_bool", True)
        value = settings_manager.get_setting("test_bool")
        
        assert value is True
        assert isinstance(value, (bool, int))
    
    def test_save_and_get_dict(self, settings_manager):
        """Test saving and retrieving dictionary values."""
        test_dict = {"key1": "value1", "key2": 123}
        settings_manager.save_setting("test_dict", test_dict)
        value = settings_manager.get_setting("test_dict")
        
        assert value == test_dict
        assert isinstance(value, dict)
    
    def test_save_and_get_list(self, settings_manager):
        """Test saving and retrieving list values."""
        test_list = [1, 2, 3, "four"]
        settings_manager.save_setting("test_list", test_list)
        value = settings_manager.get_setting("test_list")
        
        assert value == test_list
        assert isinstance(value, list)
    
    def test_get_setting_with_default(self, settings_manager):
        """Test getting non-existent setting returns default."""
        value = settings_manager.get_setting("nonexistent", "default_value")
        assert value == "default_value"
    
    def test_delete_setting(self, settings_manager):
        """Test deleting a setting."""
        settings_manager.save_setting("to_delete", "value")
        assert settings_manager.get_setting("to_delete") == "value"
        
        settings_manager.delete_setting("to_delete")
        value = settings_manager.get_setting("to_delete", "not_found")
        assert value == "not_found"
    
    def test_get_all_settings(self, settings_manager):
        """Test getting all settings."""
        settings_manager.save_setting("setting1", "value1")
        settings_manager.save_setting("setting2", 123)
        
        all_settings = settings_manager.get_all_settings()
        
        assert isinstance(all_settings, dict)
        assert "setting1" in all_settings or "setting2" in all_settings


class TestConvenienceMethods:
    """Test convenience methods for common settings."""
    
    @pytest.fixture
    def settings_manager(self):
        """Create a settings manager instance for testing."""
        manager = WindowsSettingsManager()
        manager.REGISTRY_PATH = r"Software\PhoenixTrackerTest"
        manager._ensure_registry_key()
        yield manager
        try:
            manager.clear_all_settings()
        except:
            pass
    
    def test_phoenix_url(self, settings_manager):
        """Test Phoenix URL convenience methods."""
        test_url = "https://phoenix.example.com"
        settings_manager.save_phoenix_url(test_url)
        
        retrieved_url = settings_manager.get_phoenix_url()
        assert retrieved_url == test_url
    
    def test_device_id(self, settings_manager):
        """Test Device ID convenience methods."""
        test_id = "test-device-123"
        settings_manager.save_device_id(test_id)
        
        retrieved_id = settings_manager.get_device_id()
        assert retrieved_id == test_id
    
    def test_capture_interval(self, settings_manager):
        """Test capture interval convenience methods."""
        settings_manager.save_capture_interval(120)
        
        interval = settings_manager.get_capture_interval()
        assert interval == 120
    
    def test_heartbeat_interval(self, settings_manager):
        """Test heartbeat interval convenience methods."""
        settings_manager.save_heartbeat_interval(90)
        
        interval = settings_manager.get_heartbeat_interval()
        assert interval == 90
    
    def test_similarity_threshold(self, settings_manager):
        """Test similarity threshold convenience methods."""
        settings_manager.save_similarity_threshold(0.85)
        
        threshold = settings_manager.get_similarity_threshold()
        assert abs(threshold - 0.85) < 0.01
    
    def test_verify_ssl(self, settings_manager):
        """Test SSL verification convenience methods."""
        settings_manager.save_verify_ssl(False)
        
        verify = settings_manager.get_verify_ssl()
        assert verify is False or verify == 0
    
    def test_log_level(self, settings_manager):
        """Test log level convenience methods."""
        settings_manager.save_log_level("DEBUG")
        
        level = settings_manager.get_log_level()
        assert level == "DEBUG"
    
    def test_is_configured_true(self, settings_manager):
        """Test is_configured returns True when configured."""
        settings_manager.save_phoenix_url("https://phoenix.test.com")
        settings_manager.save_device_id("device-123")
        
        assert settings_manager.is_configured() is True
    
    def test_is_configured_false(self, settings_manager):
        """Test is_configured returns False when not configured."""
        # Don't save any settings
        assert settings_manager.is_configured() is False


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.fixture
    def settings_manager(self):
        """Create a settings manager instance for testing."""
        manager = WindowsSettingsManager()
        manager.REGISTRY_PATH = r"Software\PhoenixTrackerTest"
        manager._ensure_registry_key()
        yield manager
        try:
            manager.clear_all_settings()
        except:
            pass
    
    def test_empty_string(self, settings_manager):
        """Test saving empty string."""
        settings_manager.save_setting("empty", "")
        value = settings_manager.get_setting("empty")
        assert value == ""
    
    def test_special_characters(self, settings_manager):
        """Test saving strings with special characters."""
        special_string = "Test!@#$%^&*()_+-={}[]|:;<>?,./~`"
        settings_manager.save_setting("special", special_string)
        value = settings_manager.get_setting("special")
        assert value == special_string
    
    def test_unicode_characters(self, settings_manager):
        """Test saving Unicode strings."""
        unicode_string = "Hello 世界 🌍"
        settings_manager.save_setting("unicode", unicode_string)
        value = settings_manager.get_setting("unicode")
        assert value == unicode_string
    
    def test_large_number(self, settings_manager):
        """Test saving large numbers."""
        large_num = 999999999
        settings_manager.save_setting("large", large_num)
        value = settings_manager.get_setting("large")
        assert value == large_num


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
