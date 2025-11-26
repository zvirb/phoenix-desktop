"""
Configuration management for Phoenix Desktop Tracker.
Now loads settings from Windows Registry via WindowsSettingsManager.
"""
import os
import socket
from typing import List
from windows_settings import settings_manager

class Config:
    """Application configuration loaded from Windows Registry."""
    
    @property
    def PHOENIX_API_URL(self) -> str:
        """Get Phoenix API URL from Windows settings."""
        url = settings_manager.get_phoenix_url()
        if not url:
            # Fallback to localhost for development
            return os.getenv('PHOENIX_API_URL', 'https://localhost:8000')
        return url
    
    @property
    def DEVICE_ID(self) -> str:
        """Get Device ID from Windows settings."""
        device_id = settings_manager.get_device_id()
        if not device_id:
            # Generate default
            hostname = socket.gethostname().lower()
            hostname = ''.join(c if c.isalnum() or c == '-' else '-' for c in hostname)
            return f'desktop-{hostname}'
        return device_id
    
    @property
    def CAPTURE_INTERVAL(self) -> int:
        """Get capture interval in seconds."""
        return settings_manager.get_capture_interval()
    
    @property
    def HEARTBEAT_INTERVAL(self) -> int:
        """Get heartbeat interval in seconds."""
        return settings_manager.get_heartbeat_interval()
    
    @property
    def SIMILARITY_THRESHOLD(self) -> float:
        """Get similarity threshold (0-1)."""
        return settings_manager.get_similarity_threshold()
    
    @property
    def GAMING_PROCESSES(self) -> List[str]:
        """Get gaming process blacklist."""
        processes = settings_manager.get_setting(
            'gaming_processes',
            ['steam.exe', 'steamwebhelper.exe', 'dota2.exe', 'csgo.exe', 
             'cyberpunk2077.exe', 'valorant.exe']
        )
        if isinstance(processes, str):
            # If stored as comma-separated string
            return [p.strip().lower() for p in processes.split(',')]
        return [p.lower() for p in processes]
    
    @property
    def MAX_IMAGE_WIDTH(self) -> int:
        """Get max image width in pixels."""
        return settings_manager.get_setting('max_image_width', 1024)
    
    @property
    def JPEG_QUALITY(self) -> int:
        """Get JPEG quality (1-100)."""
        return settings_manager.get_setting('jpeg_quality', 70)
    
    @property
    def VERIFY_SSL(self) -> bool:
        """Get SSL verification preference."""
        return settings_manager.get_verify_ssl()
    
    @property
    def REQUEST_TIMEOUT(self) -> int:
        """Get request timeout in seconds."""
        return settings_manager.get_setting('request_timeout', 30)
    
    @property
    def LOG_LEVEL(self) -> str:
        """Get log level."""
        return settings_manager.get_log_level()
    
    @property
    def heartbeat_url(self) -> str:
        """Get the heartbeat API endpoint."""
        return f"{self.PHOENIX_API_URL.rstrip('/')}/api/screentime/heartbeat"
    
    @property
    def capture_url(self) -> str:
        """Get the capture API endpoint."""
        return f"{self.PHOENIX_API_URL.rstrip('/')}/api/screentime/capture"
    
    def validate(self) -> None:
        """Validate configuration settings."""
        if not self.PHOENIX_API_URL:
            raise ValueError("PHOENIX_API_URL must be set in Windows Settings")
        
        if not self.PHOENIX_API_URL.startswith('https://') and 'localhost' not in self.PHOENIX_API_URL:
            raise ValueError("PHOENIX_API_URL must use HTTPS protocol (or localhost for testing)")
        
        if self.CAPTURE_INTERVAL < 10:
            raise ValueError("CAPTURE_INTERVAL must be at least 10 seconds")
        
        if not 0 <= self.SIMILARITY_THRESHOLD <= 1:
            raise ValueError("SIMILARITY_THRESHOLD must be between 0 and 1")
        
        if not 1 <= self.JPEG_QUALITY <= 100:
            raise ValueError("JPEG_QUALITY must be between 1 and 100")


# Global config instance
config = Config()
