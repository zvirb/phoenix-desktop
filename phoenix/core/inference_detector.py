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
    
    def _is_safe_path(self, path: str) -> bool:
        """
        Check if the path is a trusted system binary path.
        Prevents executing binaries from CWD or user-writable locations.
        """
        import os

        if not path:
            return False

        try:
            path = os.path.abspath(path)

            # 1. Check against CWD (Recursive)
            cwd = os.getcwd()
            # If path starts with cwd, it's inside cwd
            # Use os.path.commonpath to safely check prefix
            try:
                # Use normcase for consistent comparison
                p_cwd = os.path.normcase(cwd)
                p_path = os.path.normcase(path)

                if os.path.commonpath([p_cwd, p_path]) == p_cwd:
                    logger.warning(f"Security: Rejected path in CWD: {path}")
                    return False
            except ValueError:
                # commonpath raises ValueError if paths are on different drives
                pass

            # 2. Check against System Directories
            if os.name == 'nt':
                # Windows trusted paths
                system_root = os.environ.get('SystemRoot', r'C:\Windows')
                program_files = os.environ.get('ProgramFiles', r'C:\Program Files')
                program_files_x86 = os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')

                trusted_roots = [
                    os.path.normcase(system_root),
                    os.path.normcase(program_files),
                    os.path.normcase(program_files_x86)
                ]

                norm_path = os.path.normcase(path)
                is_trusted = False

                for root in trusted_roots:
                    try:
                        # Use commonpath to strictly validate that path is within root
                        if os.path.commonpath([root, norm_path]) == root:
                            is_trusted = True
                            break
                    except ValueError:
                        # commonpath raises if drives differ
                        continue

            else:
                # Unix trusted paths
                trusted_roots = [
                    "/bin/", "/usr/bin/", "/usr/local/bin/",
                    "/sbin/", "/usr/sbin/", "/opt/"
                ]
                is_trusted = any(path.startswith(root) for root in trusted_roots)

            if not is_trusted:
                logger.warning(f"Security: Rejected path outside trusted system directories: {path}")
                return False

            return True

        except Exception as e:
            logger.warning(f"Security: Path validation error for {path}: {e}")
            return False

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
    
    def _is_cgnat_ip(self, ip: str) -> bool:
        """
        Check if IP is in the Carrier Grade NAT (CGNAT) range used by Tailscale (100.64.0.0/10).
        Range: 100.64.0.0 to 100.127.255.255.

        Security: This prevents public IPs in the 100.0.0.0/8 block (which are valid public IPs)
        from being incorrectly identified as Tailscale/internal IPs.
        """
        try:
            if not ip or not ip.startswith('100.'):
                return False

            parts = ip.split('.')
            if len(parts) != 4:
                return False

            # Check 2nd octet
            # 100.64.0.0/10 covers 100.64.x.x to 100.127.x.x
            octet2 = int(parts[1])
            return 64 <= octet2 <= 127
        except (ValueError, IndexError):
            return False

    def _detect_tailscale_ip(self) -> Optional[str]:
        """
        Internal method to detect Tailscale IP using multiple approaches.
        
        Returns:
            Tailscale IP address or None if not found.
        """
        fallback_candidates = []

        # Optimization: Check network interfaces first (fast path)
        # Avoids expensive subprocess call if Tailscale interface is already up and detected.
        try:
            import psutil

            for iface_name, addrs in psutil.net_if_addrs().items():
                for addr in addrs:
                    if addr.family == socket.AF_INET:
                        ip = addr.address
                        # Strict validation of CGNAT range (100.64.0.0/10)
                        if self._is_cgnat_ip(ip):
                            # Strict check: only accept if interface name suggests Tailscale
                            # This prevents false positives from other CGNAT IPs (like ISP WAN)
                            is_preferred = "tailscale" in iface_name.lower() or "utun" in iface_name.lower()

                            if is_preferred:
                                # High confidence match - return immediately (fast path)
                                parts = ip.split('.')
                                masked = f"{parts[0]}.***.***.{parts[-1]}" if len(parts) == 4 else "100.***"
                                logger.debug(f"Tailscale IP from interface (fast path): {masked}")
                                return ip
                            else:
                                # Low confidence - store for fallback if CLI fails
                                fallback_candidates.append(ip)

        except ImportError:
            logger.debug("psutil not available for network interface detection")
        except Exception as e:
            logger.debug(f"Network interface detection error: {e}")

        # Method 2: Try using tailscale CLI (slower but authoritative)
        try:
            import shutil
            import os

            # Security: Check standard installation paths first to prevent path interception
            # or DLL hijacking from the current working directory.
            trusted_paths = [
                r"C:\Program Files\Tailscale\tailscale.exe",
                r"C:\Program Files (x86)\Tailscale\tailscale.exe",
                "/usr/bin/tailscale",
                "/usr/local/bin/tailscale",
                "/opt/tailscale/tailscale"
            ]

            tailscale_path = None

            # Check trusted paths first
            for path in trusted_paths:
                if os.path.exists(path) and os.access(path, os.X_OK):
                    tailscale_path = path
                    break

            # Fallback to PATH search if not found in standard locations
            if not tailscale_path:
                found_path = shutil.which('tailscale')

                if found_path:
                    if self._is_safe_path(found_path):
                        tailscale_path = found_path
                    else:
                        logger.warning(f"Security: Ignored unsafe tailscale path found in PATH: {found_path}")
                        tailscale_path = None

            if tailscale_path:
                result = subprocess.run(
                    [tailscale_path, 'ip', '--4'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
                )
                if result.returncode == 0:
                    ip = result.stdout.strip()
                    if self._is_cgnat_ip(ip):
                        # Mask IP in logs
                        parts = ip.split('.')
                        masked = f"{parts[0]}.***.***.{parts[-1]}" if len(parts) == 4 else "100.***"
                        logger.debug(f"Tailscale IP from CLI: {masked}")
                        return ip
            else:
                logger.debug("Tailscale CLI not found (checked trusted paths and PATH)")

        except FileNotFoundError:
            logger.debug("Tailscale CLI not found in PATH")
        except subprocess.TimeoutExpired:
            logger.debug("Tailscale CLI timed out")
        except Exception as e:
            logger.debug(f"Tailscale CLI error: {e}")
        
        # Method 3: Fallback - use any candidates found in Method 1 (loose matching)
        if fallback_candidates:
            ip = fallback_candidates[0]
            parts = ip.split('.')
            masked = f"{parts[0]}.***.***.{parts[-1]}" if len(parts) == 4 else "100.***"
            logger.debug(f"Tailscale IP from interface (fallback): {masked}")
            return ip
        
        # Method 4: Fallback - check socket connections
        try:
            # Try to find IPs by checking all IPs on the machine
            hostname = socket.gethostname()
            for ip in socket.gethostbyname_ex(hostname)[2]:
                if self._is_cgnat_ip(ip):
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
