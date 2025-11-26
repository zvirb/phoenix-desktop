"""
Secure API client for Phoenix backend with IAM authentication.
"""
import logging
import time
from typing import Optional, Dict, Any
from io import BytesIO

import requests
from PIL import Image

from config import config
from token_manager import get_auth_token

logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with Phoenix backend."""
    
    def __init__(self):
        """Initialize API client."""
        self.token = get_auth_token()
        if not self.token:
            raise ValueError("No authentication token available. Run token setup first.")
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}',
            'X-Device-ID': config.DEVICE_ID,
            'User-Agent': f'PhoenixTracker/{config.DEVICE_ID}'
        })
        
        # Apply security settings
        self.session.verify = config.VERIFY_SSL
        
        # Track last request time for rate limiting
        self.last_capture_time = 0
        self.min_capture_interval = 30  # seconds - respect rate limiting
    
    def send_heartbeat(self, app_name: str, window_title: str, is_idle: bool = False) -> Dict[str, Any]:
        """
        Send heartbeat with current app usage data.
        
        Args:
            app_name: Name of the active application
            window_title: Title of the active window
            is_idle: Whether the user is idle
            
        Returns:
            Response data from the server
        """
        payload = {
            'timestamp': time.time(),
            'app_name': app_name,
            'window_title': window_title,
            'is_idle': is_idle
        }
        
        try:
            response = self.session.post(
                config.heartbeat_url,
                json=payload,
                timeout=config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            logger.info(f"Heartbeat sent: {app_name}")
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Authentication failed. Token may be invalid or expired.")
                raise
            logger.error(f"Heartbeat failed: {e}")
            raise
        except requests.exceptions.RequestException as e:
            logger.warning(f"Heartbeat request failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def upload_screenshot(self, image_bytes: bytes, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Upload screenshot to Phoenix backend.
        
        Args:
            image_bytes: JPEG image bytes
            metadata: Optional metadata to send with the image
            
        Returns:
            Response data from the server including context summary
        """
        # Check rate limiting
        current_time = time.time()
        time_since_last = current_time - self.last_capture_time
        
        if time_since_last < self.min_capture_interval:
            logger.warning(f"Rate limit: {self.min_capture_interval - time_since_last:.1f}s remaining")
            return {
                'status': 'rate_limited',
                'retry_after': self.min_capture_interval - time_since_last
            }
        
        try:
            # Prepare multipart form data
            files = {
                'file': ('screenshot.jpg', image_bytes, 'image/jpeg')
            }
            
            data = metadata or {}
            data['device_id'] = config.DEVICE_ID
            data['timestamp'] = current_time
            
            response = self.session.post(
                config.capture_url,
                files=files,
                data=data,
                timeout=config.REQUEST_TIMEOUT
            )
            
            self.last_capture_time = current_time
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Screenshot uploaded: {result.get('status')}")
            
            if result.get('context_summary'):
                logger.info(f"Context: {result['context_summary']}")
            
            return result
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Authentication failed. Token may be invalid or expired.")
                raise
            elif e.response.status_code == 422:
                logger.warning(f"Image processing failed: {e.response.json().get('message')}")
                return e.response.json()
            elif e.response.status_code == 413:
                logger.error("Image too large. Try reducing quality or resolution.")
                raise
            else:
                logger.error(f"Upload failed: {e}")
                raise
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Upload request failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def test_connection(self) -> bool:
        """
        Test the connection to Phoenix backend.
        
        Returns:
            True if connection successful and authenticated
        """
        try:
            # Try to send a test heartbeat
            result = self.send_heartbeat(
                app_name="PhoenixTracker",
                window_title="Connection Test",
                is_idle=True
            )
            return result.get('status') != 'failed'
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


def create_client() -> Optional[APIClient]:
    """
    Create and validate an API client.
    
    Returns:
        APIClient instance, or None if setup failed
    """
    try:
        client = APIClient()
        
        # Test the connection
        logger.info("Testing connection to Phoenix backend...")
        if client.test_connection():
            logger.info("✅ Connected to Phoenix backend")
            return client
        else:
            logger.error("❌ Connection test failed")
            return None
            
    except ValueError as e:
        logger.error(f"Client setup failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None
