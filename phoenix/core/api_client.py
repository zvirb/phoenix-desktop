"""
Secure API client for Phoenix backend with IAM authentication and offline queuing.
"""
import logging
import random
import time
import json
import requests
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urljoin
try:
    from phoenix_logging import sanitize_data
except ImportError:
    # Fallback if phoenix_logging is not in path
    def sanitize_data(data, depth=0): return data

from .request_queue import RequestQueue

logger = logging.getLogger(__name__)

class APIClient:
    """Client for Phoenix Digital Homestead API."""
    
    def __init__(self, base_url: str, device_id: str, verify_ssl: bool = True):
        self.base_url = base_url.rstrip('/')
        self.device_id = device_id
        self.verify_ssl = verify_ssl
        self.token = None
        self.device_token = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': f'PhoenixTracker/{device_id}',
            'X-Device-ID': device_id
        })
        self.queue = RequestQueue()
        
    def set_token(self, token: str):
        """Set authentication token for future requests."""
        self.token = token
        self.session.headers.update({
            'Authorization': f'Bearer {token}'
        })
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make an HTTP request with error handling and offline queuing.
        """
        url = urljoin(self.base_url, endpoint)
        
        # Use a longer default timeout (30s for general, can be overridden)
        timeout = kwargs.pop('timeout', 30)
        
        # Define the core request operation
        def operation():
            return self.session.request(
                method,
                url,
                verify=self.verify_ssl,
                timeout=timeout,
                **kwargs
            )
        
        try:
            # 1. Attempt request (retries on network errors and 5xx)
            response = self._retry_operation(operation, max_attempts=3, base_delay=1)
            
            # 2. Handle 401 Unauthorized (invalid/expired JWT)
            if response.status_code == 401:
                logger.info(f"Unauthorized (401) for {endpoint}, attempting re-authentication...")
                if self.ensure_authenticated():
                    # Retry once after refreshing token
                    logger.info("Re-authentication successful, retrying request...")
                    response = self._retry_operation(operation, max_attempts=2, base_delay=1)
            
            # 3. Check final status
            response.raise_for_status()
            
            # 4. Success -> process queue and return JSON
            self.process_queue()
            result = response.json()

            # Sanitize sensitive data before logging
            safe_result = sanitize_data(result)
            logger.debug(f"API Response from {endpoint}: {safe_result}")

            return result
            
        except requests.exceptions.HTTPError as e:
            # Sanitize error body to prevent leaking sensitive info
            try:
                error_body = e.response.text
                if error_body:
                    try:
                        error_json = json.loads(error_body)
                        sanitized_error = sanitize_data(error_json)
                        error_msg = json.dumps(sanitized_error)
                    except (json.JSONDecodeError, TypeError):
                        # Not JSON, truncate to avoid massive logs
                        if len(error_body) > 500:
                            error_msg = error_body[:500] + "..."
                        else:
                            error_msg = error_body
                else:
                    error_msg = ""
            except Exception:
                error_msg = "<Failed to process error body>"

            logger.error(f"HTTP Error for {endpoint}: {e.response.status_code} - {error_msg}")
            return {'status': 'failed', 'error': str(e), 'code': e.response.status_code}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request failed for {endpoint}: {e}")
            
            # 5. Queue heartbeats if they failed due to network issues
            if "heartbeat" in endpoint and kwargs.get('json'):
                logger.warning("Network error, queuing heartbeat for later.")
                self.queue.add(
                    endpoint=endpoint,
                    method=method,
                    data=kwargs.get('json')
                )
                return {'status': 'queued', 'error': str(e)}

            return {'status': 'failed', 'error': str(e)}
        except Exception as e:
            logger.error(f"Unexpected error in _make_request: {e}")
            return {'status': 'failed', 'error': str(e)}

    def process_queue(self):
        """Retry pending requests from the offline queue."""
        if self.queue.count() == 0:
            return

        # use a separate session or same session? Same is fine.
        pending = self.queue.peek(limit=5)
        
        for req in pending:
            try:
                data = json.loads(req['data']) if req['data'] else None
                url = urljoin(self.base_url, req['endpoint'])
                
                logger.info(f"Retrying queued item {req['id']}...")
                # NOTE: We don't pass req['headers'] here so it uses the current 
                # session headers (with the latest valid JWT token).
                self.session.request(
                    req['method'],
                    url,
                    json=data,
                    verify=self.verify_ssl,
                    timeout=15
                ).raise_for_status()
                
                self.queue.pop(req['id'])
                
            except Exception as e:
                logger.warning(f"Failed to retry item {req['id']}: {e}")
                break

    def authenticate(self, device_token: str) -> Dict[str, Any]:
        """
        Authenticate with the server using device token.
        
        The device token (phx_...) is sent in the Authorization header.
        Returns JWT access_token for subsequent API calls.
        """
        self.device_token = device_token
        url = f"{self.base_url}/api/v1/devices/authenticate"
        
        # Define the auth request operation
        def operation():
            return self.session.post(
                url,
                headers={'Authorization': f'Bearer {device_token}'},
                verify=self.verify_ssl,
                timeout=30
            )
        
        try:
            # Use retry with exponential backoff for network issues
            response = self._retry_operation(operation, max_attempts=4, base_delay=2)
            
            response.raise_for_status()
            data = response.json()
            
            # Update session with JWT for subsequent requests
            if data.get('access_token'):
                self.set_token(data['access_token'])
                self.jwt_expires_at = time.time() + data.get('expires_in', 600) - 60  # Refresh 1 min early
                logger.info(f"Authenticated successfully. JWT expires in {data.get('expires_in', 600)}s")
            
            return data
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return {'status': 'failed', 'error': str(e)}
    
    def ensure_authenticated(self, device_token: str = None) -> bool:
        """Re-authenticate if JWT is expired or about to expire."""
        if not hasattr(self, 'jwt_expires_at') or time.time() >= self.jwt_expires_at:
            logger.info("JWT expired or missing, re-authenticating...")
            token = device_token or getattr(self, 'device_token', None)
            if token is None:
                logger.error("Device token not available for re-authentication.")
                return False
            # Use retry logic for authentication as well
            result = self.authenticate(token)
            return result.get('access_token') is not None
        return True

    def send_heartbeat(
        self,
        app_name: str,
        window_title: str,
        is_idle: bool,
        ollama_available: bool = None,
        ollama_models: list = None,
        ollama_port: int = None,
        tailscale_ip: str = None
    ) -> Dict[str, Any]:
        """
        Send heartbeat data.
        """
        from datetime import datetime, timezone
        # Use ISO format with 'Z' for UTC
        timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        if not timestamp.endswith('Z'):
            timestamp += 'Z'

        data = {
            'timestamp': timestamp,
            'device_id': self.device_id,
            'app_name': app_name or "Unknown",
            'window_title': window_title or "Unknown",
            'is_idle': bool(is_idle)
        }
        
        # Add inference capabilities
        if ollama_available is not None:
            data['ollama_available'] = ollama_available
        if ollama_models is not None:
            data['ollama_models'] = ollama_models
            
        # Ensure ollama_port is an int and not None
        if ollama_port is not None:
            try:
                data['ollama_port'] = int(ollama_port)
            except (ValueError, TypeError):
                logger.warning(f"Invalid ollama_port: {ollama_port}")
        
        if tailscale_ip is not None:
            data['tailscale_ip'] = tailscale_ip
        
        # Mask sensitive data in logs
        safe_data = data.copy()
        title = safe_data.get('window_title') or ''
        if len(title) > 10:
            safe_data['window_title'] = f"{title[:10]}..."

        logger.debug(f"Heartbeat data: {safe_data}")
        return self._make_request('POST', '/api/v1/screentime/heartbeat', json=data)

    def upload_screenshot(self, image_bytes: bytes) -> Dict[str, Any]:
        """Upload a screenshot."""
        files = {
            'file': ('screenshot.jpg', image_bytes, 'image/jpeg')
        }
        data = {
            'device_id': self.device_id, 
            'timestamp': time.time()
        }
        
        logger.info(f"Uploading screenshot ({len(image_bytes)} bytes)...")
        return self._make_request(
            'POST', 
            '/api/v1/screentime/capture', 
            files=files, 
            data=data, 
            timeout=60
        )

    def upload_audio(self, audio_bytes: bytes) -> Dict[str, Any]:
        """Upload an audio note for STT."""
        files = {
            'file': ('voice_note.wav', audio_bytes, 'audio/wav')
        }
        data = {
            'device_id': self.device_id,
            'timestamp': time.time()
        }
        
        logger.info(f"Uploading audio note ({len(audio_bytes)} bytes)...")
        return self._make_request(
            'POST',
            '/api/v1/voice/capture',
            files=files,
            data=data,
            timeout=60
        )

    def get_gamification_profile(self) -> Dict[str, Any]:
        """Fetch user gamification profile (level, xp, etc)."""
        return self._make_request('GET', '/api/v1/gamification/profile')

    def start_focus_session(self, duration: int = 25, task: str = None) -> Dict[str, Any]:
        """Start a focus session."""
        params = {"duration_minutes": duration}
        if task:
            params["task_category"] = task
        return self._make_request('POST', '/api/v1/focus/session', params=params)

    def _retry_operation(self, func, max_attempts=3, base_delay=1):
        """Execute *func* with exponential backoff and jitter.
        Returns the successful result or raises the last exception.
        """
        attempt = 0
        while attempt < max_attempts:
            try:
                response = func()
                # Treat 5xx server errors as retriable (they raise HTTPError)
                if 500 <= response.status_code < 600:
                    response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                attempt += 1
                if attempt >= max_attempts:
                    logger.error(f"Operation failed after {attempt} attempts: {e}")
                    raise
                delay = base_delay * (2 ** (attempt - 1))
                jitter = random.uniform(0, delay * 0.1)
                sleep_time = delay + jitter
                logger.warning(f"Retrying operation in {sleep_time:.2f}s (attempt {attempt}/{max_attempts})")
                time.sleep(sleep_time)

def create_client(base_url: str, device_id: str, verify_ssl: bool = True) -> Optional[APIClient]:
    """Factory function."""
    try:
        return APIClient(base_url, device_id, verify_ssl)
    except Exception as e:
        logger.error(f"Failed to create client: {e}")
        return None

# Alias for backward compatibility
PhoenixApiClient = APIClient
