from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class PhoenixSettings(BaseModel):
    """
    Pydantic model for validating application settings.
    Ensures that all configuration going into the application is valid.
    """
    # Server Settings
    phoenix_url: str = Field(default="https://phoenix.example.com")
    device_id: str = Field(min_length=3)
    
    # Capture Settings
    capture_interval: int = Field(default=60, ge=10, le=3600)
    heartbeat_interval: int = Field(default=60, ge=10, le=3600)
    similarity_threshold: float = Field(default=0.95, ge=0.0, le=1.0)
    
    # Performance Settings
    max_image_width: int = Field(default=1024, ge=100, le=3840)
    jpeg_quality: int = Field(default=70, ge=1, le=100)
    
    # Security Settings
    verify_ssl: bool = Field(default=True)
    
    # Ollama Settings
    ollama_port: int = Field(default=11450, ge=1, le=65535)
    
    # Advanced
    log_level: str = Field(default="INFO")

    @field_validator('phoenix_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL cannot be empty")
        # Allow localhost for testing, otherwise require https
        if v.startswith("http://localhost") or v.startswith("http://127.0.0.1"):
            return v
        if not v.startswith("https://"):
            raise ValueError("URL must start with https:// (unless localhost)")
        return v

    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            return "INFO"
        return v.upper()

def validate_settings(settings_dict: dict) -> tuple[bool, Optional[str], Optional[PhoenixSettings]]:
    """
    Validate a dictionary of settings.
    Returns: (is_valid, error_message, settings_object)
    """
    try:
        model = PhoenixSettings(**settings_dict)
        return True, None, model
    except Exception as e:
        logger.error(f"Settings validation failed: {e}")
        return False, str(e), None
