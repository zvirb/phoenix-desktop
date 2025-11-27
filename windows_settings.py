"""
Windows Settings Manager for Phoenix Desktop Tracker.
Securely stores settings in Windows Registry.
"""
import winreg
import json
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WindowsSettingsManager:
    """Manages application settings in Windows Registry."""
    
    # Registry path
    REGISTRY_PATH = r"Software\PhoenixTracker"
    
    def __init__(self):
        """Initialize the settings manager."""
        self._ensure_registry_key()
    
    def _ensure_registry_key(self) -> None:
        """Ensure the registry key exists."""
        try:
            winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
        except Exception as e:
            logger.error(f"Failed to create registry key: {e}")
    
    def save_setting(self, name: str, value: Any) -> bool:
        """
        Save a setting to Windows Registry.
        
        Args:
            name: Setting name
            value: Setting value (str, int, bool, or dict/list as JSON)
        
        Returns:
            True if successful
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            )
            
            # Convert value based on type
            if isinstance(value, bool):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, int(value))
            elif isinstance(value, int):
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            elif isinstance(value, str):
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
            elif isinstance(value, (dict, list)):
                # Store complex types as JSON
                json_str = json.dumps(value)
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, json_str)
            else:
                # Default to string representation
                winreg.SetValueEx(key, name, 0, winreg.REG_SZ, str(value))
            
            winreg.CloseKey(key)
            logger.debug(f"Saved setting: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save setting {name}: {e}")
            return False
    
    def get_setting(self, name: str, default: Any = None) -> Any:
        """
        Get a setting from Windows Registry.

        Args:
            name: Setting name
            default: Default value if not found

        Returns:
            Setting value or default
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )

            value, value_type = winreg.QueryValueEx(key, name)
            winreg.CloseKey(key)

            # Try to parse JSON for complex types
            if value_type == winreg.REG_SZ and isinstance(value, str):
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass

            logger.debug(f"Retrieved setting: {name}")
            return value

        except FileNotFoundError:
            logger.debug(f"Setting not found: {name}, using default: {default}")
            return default
        except Exception as e:
            logger.error(f"Failed to get setting {name}: {e}")
            return default
    
    def delete_setting(self, name: str) -> bool:
        """
        Delete a setting from Windows Registry.
        
        Args:
            name: Setting name
        
        Returns:
            True if successful
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_PATH,
                0,
                winreg.KEY_WRITE
            )
            
            winreg.DeleteValue(key, name)
            winreg.CloseKey(key)
            logger.debug(f"Deleted setting: {name}")
            return True
            
        except FileNotFoundError:
            logger.debug(f"Setting not found: {name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete setting {name}: {e}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all settings as a dictionary.
        
        Returns:
            Dictionary of all settings
        """
        settings = {}
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )
            
            # Enumerate all values
            index = 0
            while True:
                try:
                    name, value, value_type = winreg.EnumValue(key, index)
                    
                    # Try to parse JSON for complex types
                    if value_type == winreg.REG_SZ and isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            pass
                    
                    settings[name] = value
                    index += 1
                    
                except OSError:
                    break
            
            winreg.CloseKey(key)
            
        except Exception as e:
            logger.error(f"Failed to enumerate settings: {e}")
        
        return settings
    
    def clear_all_settings(self) -> bool:
        """
        Clear all settings from Windows Registry.
        
        Returns:
            True if successful
        """
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, self.REGISTRY_PATH)
            self._ensure_registry_key()
            logger.info("Cleared all settings")
            return True
        except Exception as e:
            logger.error(f"Failed to clear settings: {e}")
            return False
    
    # Convenience methods for common settings
    
    def save_phoenix_url(self, url: str) -> bool:
        """Save Phoenix API URL."""
        return self.save_setting("phoenix_api_url", url)
    
    def get_phoenix_url(self) -> Optional[str]:
        """Get Phoenix API URL."""
        return self.get_setting("phoenix_api_url")
    
    def save_device_id(self, device_id: str) -> bool:
        """Save Device ID."""
        return self.save_setting("device_id", device_id)
    
    def get_device_id(self) -> Optional[str]:
        """Get Device ID."""
        return self.get_setting("device_id")
    
    def save_capture_interval(self, interval: int) -> bool:
        """Save capture interval in seconds."""
        return self.save_setting("capture_interval", interval)
    
    def get_capture_interval(self) -> int:
        """Get capture interval, default 60 seconds."""
        return self.get_setting("capture_interval", 60)
    
    def save_heartbeat_interval(self, interval: int) -> bool:
        """Save heartbeat interval in seconds."""
        return self.save_setting("heartbeat_interval", interval)
    
    def get_heartbeat_interval(self) -> int:
        """Get heartbeat interval, default 60 seconds."""
        return self.get_setting("heartbeat_interval", 60)
    
    def save_similarity_threshold(self, threshold: float) -> bool:
        """Save similarity threshold (0-1)."""
        return self.save_setting("similarity_threshold", threshold)
    
    def get_similarity_threshold(self) -> float:
        """Get similarity threshold, default 0.95."""
        return self.get_setting("similarity_threshold", 0.95)
    
    def save_autostart(self, enabled: bool) -> bool:
        """Save autostart preference."""
        return self.save_setting("autostart", enabled)
    
    def get_autostart(self) -> bool:
        """Get autostart preference, default False."""
        return self.get_setting("autostart", False)
    
    def save_verify_ssl(self, verify: bool) -> bool:
        """Save SSL verification preference."""
        return self.save_setting("verify_ssl", verify)
    
    def get_verify_ssl(self) -> bool:
        """Get SSL verification preference, default True."""
        return self.get_setting("verify_ssl", True)
    
    def save_log_level(self, level: str) -> bool:
        """Save log level."""
        return self.save_setting("log_level", level)
    
    def get_log_level(self) -> str:
        """Get log level, default INFO."""
        return self.get_setting("log_level", "INFO")
    
    def is_configured(self) -> bool:
        """Check if the app has been configured."""
        url = self.get_phoenix_url()
        device_id = self.get_device_id()
        return bool(url and device_id and url != "https://your-phoenix-server.com")


# Global instance
settings_manager = WindowsSettingsManager()
