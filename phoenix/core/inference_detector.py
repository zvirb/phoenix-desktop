"""
Inference and Network Detection for Phoenix Desktop Tracker.

Detects:
- Ollama availability for local inference
- Tailscale IP address for peer network connectivity
"""
import logging
import socket
import subprocess
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class InferenceDetector:
    """Detect local inference capabilities and network information."""
    
    def __init__(self, ollama_host: str = "http://localhost:11450"):
        """
        Initialize the inference detector.
        
        Args:
            ollama_host: Base URL for Ollama API (default: http://localhost:11450)
        """
        # Security: Validate Ollama host to prevent SSRF
        # Ensure it points to localhost only
        try:
            parsed = urlparse(ollama_host)
            if parsed.scheme not in ('http', 'https') or parsed.hostname not in ('localhost', '127.0.0.1'):
                logger.warning(f"Security: Invalid Ollama host '{ollama_host}'. Resetting to default.")
                self.ollama_host = "http://localhost:11450"
            else:
                self.ollama_host = ollama_host.rstrip('/')
        except Exception as e:
            logger.warning(f"Security: Failed to parse Ollama host '{ollama_host}': {e}. Resetting to default.")
            self.ollama_host = "http://localhost:11450"

        self._ollama_cache = None
        self._ollama_cache_time = 0
        self._tailscale_cache = None
        self._tailscale_cache_time = 0
        self.cache_duration = 60  # Cache results for 60 seconds
    
    def is_ollama_available(self) -> bool:
        """
        Check if Ollama is running and available for inference.
        
        Returns:
            True if Ollama API is responding, False otherwise.
        """
        import time
        current_time = time.time()
        
        # Use cached result if still valid
        if self._ollama_cache is not None and (current_time - self._ollama_cache_time) < self.cache_duration:
            return self._ollama_cache
        
        try:
            # Check Ollama health endpoint
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=2)
            is_available = response.status_code == 200
            
            # Cache the result
            self._ollama_cache = is_available
            self._ollama_cache_time = current_time
            
            if is_available:
                logger.debug(f"Ollama is available at {self.ollama_host}")
            else:
                logger.debug(f"Ollama returned status {response.status_code}")
            
            return is_available
            
        except requests.exceptions.RequestException as e:
            logger.debug(f"Ollama not available: {e}")
            self._ollama_cache = False
            self._ollama_cache_time = current_time
            return False
    
    def get_ollama_models(self) -> list:
        """
        Get list of available Ollama models.
        
        Returns:
            List of model names, or empty list if Ollama is not available.
        """
        if not self.is_ollama_available():
            return []
        
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model.get('name', '') for model in data.get('models', [])]
                logger.debug(f"Available Ollama models: {models}")
                return models
            return []
        except Exception as e:
            logger.debug(f"Failed to get Ollama models: {e}")
            return []
    
    def get_tailscale_ip(self) -> Optional[str]:
        """
        Get the Tailscale IP address of this device.
        
        Returns:
            Tailscale IP address (100.x.x.x format) or None if not connected.
        """
        import time
        current_time = time.time()
        
        # Use cached result if still valid (even if None)
        if self._tailscale_cache_time > 0 and (current_time - self._tailscale_cache_time) < self.cache_duration:
            return self._tailscale_cache
        
        tailscale_ip = self._detect_tailscale_ip()
        
        # Cache the result
        self._tailscale_cache = tailscale_ip
        self._tailscale_cache_time = current_time
        
        return tailscale_ip
    
    def _detect_tailscale_ip(self) -> Optional[str]:
        """
        Internal method to detect Tailscale IP using multiple approaches.
        
        Returns:
            Tailscale IP address or None if not found.
        """
        # Method 1: Try using tailscale CLI (most reliable)
        try:
            result = subprocess.run(
                ['tailscale', 'ip', '--4'],
                capture_output=True,
                text=True,
                timeout=5,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            if result.returncode == 0:
                ip = result.stdout.strip()
                if ip and ip.startswith('100.'):
                    # Mask IP in logs
                    parts = ip.split('.')
                    masked = f"{parts[0]}.***.***.{parts[-1]}" if len(parts) == 4 else "100.***"
                    logger.debug(f"Tailscale IP from CLI: {masked}")
                    return ip
        except FileNotFoundError:
            logger.debug("Tailscale CLI not found in PATH")
        except subprocess.TimeoutExpired:
            logger.debug("Tailscale CLI timed out")
        except Exception as e:
            logger.debug(f"Tailscale CLI error: {e}")
        
        # Method 2: Check network interfaces for Tailscale IP range
        try:
            import psutil
            for iface_name, addrs in psutil.net_if_addrs().items():
                # Tailscale interface is often named "Tailscale" on Windows
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        # Tailscale uses the 100.x.y.z CGNAT range
                        if ip.startswith('100.'):
                            parts = ip.split('.')
                            masked = f"{parts[0]}.***.***.{parts[-1]}" if len(parts) == 4 else "100.***"
                            logger.debug(f"Tailscale IP from interface {iface_name}: {masked}")
                            return ip
        except ImportError:
            logger.debug("psutil not available for network interface detection")
        except Exception as e:
            logger.debug(f"Network interface detection error: {e}")
        
        # Method 3: Fallback - check socket connections
        try:
            # Try to find IPs by checking all IPs on the machine
            hostname = socket.gethostname()
            for ip in socket.gethostbyname_ex(hostname)[2]:
                if ip.startswith('100.'):
                    parts = ip.split('.')
                    masked = f"{parts[0]}.***.***.{parts[-1]}" if len(parts) == 4 else "100.***"
                    logger.debug(f"Tailscale IP from hostname resolution: {masked}")
                    return ip
        except Exception as e:
            logger.debug(f"Hostname IP resolution error: {e}")
        
        logger.debug("Tailscale IP not found")
        return None
    
    def is_tailscale_connected(self) -> bool:
        """
        Check if device is connected to Tailscale network.
        
        Returns:
            True if Tailscale IP is available, False otherwise.
        """
        return self.get_tailscale_ip() is not None
    
    def get_inference_status(self) -> Dict[str, Any]:
        """
        Get comprehensive inference and network status.
        
        Returns:
            Dictionary containing:
            - ollama_available: bool
            - ollama_models: list of model names
            - tailscale_ip: str or None
            - tailscale_connected: bool
        """
        ollama_available = self.is_ollama_available()
        ollama_models = self.get_ollama_models() if ollama_available else []
        tailscale_ip = self.get_tailscale_ip()
        
        status = {
            'ollama_available': ollama_available,
            'ollama_models': ollama_models,
            'tailscale_ip': tailscale_ip,
            'tailscale_connected': tailscale_ip is not None
        }
        
        logger.debug(f"Inference status: {status}")
        return status
    
    def clear_cache(self):
        """Clear cached detection results."""
        self._ollama_cache = None
        self._ollama_cache_time = 0
        self._tailscale_cache = None
        self._tailscale_cache_time = 0


# Module-level singleton for convenience
_detector = None


def get_detector(ollama_host: str = "http://localhost:11450") -> InferenceDetector:
    """Get or create the singleton InferenceDetector instance."""
    global _detector
    if _detector is None:
        _detector = InferenceDetector(ollama_host)
    return _detector
