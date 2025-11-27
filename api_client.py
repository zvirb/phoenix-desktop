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

from data_cache import DataCache
from phoenix_logging import get_logger, log_exception

logger = get_logger(__name__)


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
        
        # Initialize data cache
        self.cache = DataCache()
    
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
            
            # Process pending uploads if connection is good
            self.process_pending_uploads()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("Authentication failed. Token may be invalid or expired.")
                raise
            log_exception(e, "Heartbeat failed")
            # Cache failed heartbeat (except for auth errors)
            if 500 <= e.response.status_code < 600:
                self.cache.add_item('heartbeat', payload)
            raise
        except requests.exceptions.RequestException as e:
            logger.warning(f"Heartbeat request failed: {e}. Caching for retry.")
            self.cache.add_item('heartbeat', payload)
            return {'status': 'cached', 'error': str(e)}
    
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
        
        data = metadata or {}
        data['device_id'] = config.DEVICE_ID
        data['timestamp'] = current_time
        
        try:
            # Prepare multipart form data
            files = {
                'file': ('screenshot.jpg', image_bytes, 'image/jpeg')
            }
            
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
            
            # Process pending uploads if connection is good
            self.process_pending_uploads()
            
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
            elif 500 <= e.response.status_code < 600:
                log_exception(e, "Server error. Caching for retry.")
                self.cache.add_item('screenshot', data, image_bytes)
                raise
            else:
                log_exception(e, "Upload failed")
                raise
                
        except requests.exceptions.RequestException as e:
            log_exception(e, "Upload request failed. Caching for retry.")
            self.cache.add_item('screenshot', data, image_bytes)
            return {'status': 'cached', 'error': str(e)}

    def process_pending_uploads(self):
        """Process pending uploads from the cache."""
        pending_items = self.cache.get_pending_items(limit=5)
        if not pending_items:
            return
            
        logger.info(f"Processing {len(pending_items)} pending uploads...")
        
        for item_id, item_type, data, file_data in pending_items:
            try:
                if item_type == 'heartbeat':
                    self.session.post(
                        config.heartbeat_url,
                        json=data,
                        timeout=config.REQUEST_TIMEOUT
                    ).raise_for_status()
                    logger.info(f"Processed pending heartbeat (ID: {item_id})")
                    
                elif item_type == 'screenshot':
                    files = {
                        'file': ('screenshot.jpg', file_data, 'image/jpeg')
                    }
                    self.session.post(
                        config.capture_url,
                        files=files,
                        data=data,
                        timeout=config.REQUEST_TIMEOUT
                    ).raise_for_status()
                    logger.info(f"Processed pending screenshot (ID: {item_id})")
                
                # Remove from cache on success
                self.cache.remove_item(item_id)
                
            except Exception as e:
                log_exception(e, f"Failed to process pending item {item_id}")
                # Stop processing to avoid hammering the server if it's still flaky
                break    
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
            log_exception(e, "Connection test failed")
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
