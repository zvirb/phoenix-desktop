"""
Configuration management for Phoenix Desktop Tracker.
Loads settings from environment variables and .env file.
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""
    
    # API Settings
    PHOENIX_API_URL: str = os.getenv('PHOENIX_API_URL', 'https://localhost:8000')
    DEVICE_ID: str = os.getenv('DEVICE_ID', f'workstation-{os.getenv("COMPUTERNAME", "unknown")}')
    
    # Capture Settings
    CAPTURE_INTERVAL: int = int(os.getenv('CAPTURE_INTERVAL', '60'))
    HEARTBEAT_INTERVAL: int = int(os.getenv('HEARTBEAT_INTERVAL', '60'))
    SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.95'))
    
    # Gaming Process Blacklist
    GAMING_PROCESSES: List[str] = [
        p.strip().lower() 
        for p in os.getenv(
            'GAMING_PROCESSES', 
            'steam.exe,steamwebhelper.exe,dota2.exe,csgo.exe,cyberpunk2077.exe,valorant.exe'
        ).split(',')
    ]
    
    # Performance Settings
    MAX_IMAGE_WIDTH: int = int(os.getenv('MAX_IMAGE_WIDTH', '1024'))
    JPEG_QUALITY: int = int(os.getenv('JPEG_QUALITY', '70'))
    
    # Security Settings
    VERIFY_SSL: bool = os.getenv('VERIFY_SSL', 'true').lower() == 'true'
    REQUEST_TIMEOUT: int = int(os.getenv('REQUEST_TIMEOUT', '30'))
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # API Endpoints
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
            raise ValueError("PHOENIX_API_URL must be set")
        
        if not self.PHOENIX_API_URL.startswith('https://'):
            raise ValueError("PHOENIX_API_URL must use HTTPS protocol")
        
        if self.CAPTURE_INTERVAL < 10:
            raise ValueError("CAPTURE_INTERVAL must be at least 10 seconds")
        
        if not 0 <= self.SIMILARITY_THRESHOLD <= 1:
            raise ValueError("SIMILARITY_THRESHOLD must be between 0 and 1")
        
        if not 1 <= self.JPEG_QUALITY <= 100:
            raise ValueError("JPEG_QUALITY must be between 1 and 100")


# Global config instance
config = Config()
