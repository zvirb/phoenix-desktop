import logging
import time
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from phoenix.core.api_client import APIClient
from phoenix.core.token_manager import get_auth_token
from config import config

logger = logging.getLogger(__name__)

class SyncWorker(QThread):
    """
    Background worker for syncing data to Phoenix Core.
    Handles:
    - Heartbeats (periodic)
    - Screenshot Uploads (on demand)
    - Authentication Refresh
    """
    heartbeat_sent = pyqtSignal(bool) # True = success
    uploaded = pyqtSignal(bool)       # True = success
    gamification_update = pyqtSignal(dict) # Emits profile data

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.client = None
        self.heartbeat_interval = 60 # 60 seconds
        self.last_heartbeat = 0
        
        # State to hold for heartbeat
        self.current_state = {
            "app_name": "Phoenix",
            "window_title": "Initializing",
            "is_idle": False,
            "ollama_available": False,
            "ollama_models": [],
            "tailscale_ip": None
        }
        
        # Queue for screenshots to upload
        self.upload_queue = []
        self.queue_lock = False # Simple lock for this single thread loop
        
        self._init_client()

    def _init_client(self):
        try:
            token = get_auth_token()
            if token:
                base_url = config.PHOENIX_API_URL
                device_id = config.DEVICE_ID
                self.client = APIClient(base_url, device_id)
                self.client.token = token # Pre-set token
                # Verify/Auth
                self.client.ensure_authenticated(token)
                logger.info("SyncWorker: Client initialized")
            else:
                logger.warning("SyncWorker: No token available")
        except Exception as e:
            logger.error(f"SyncWorker init failed: {e}")

    def update_state(self, **kwargs):
        """Update local state for next heartbeat."""
        self.current_state.update(kwargs)

    def queue_upload(self, image_bytes):
        """Add image to upload queue."""
        self.upload_queue.append(image_bytes)

    def run(self):
        logger.info("SyncWorker started")
        while self.running:
            try:
                current_time = time.time()
                
                # 0. Check Client
                if not self.client:
                    self._init_client()
                    if not self.client:
                        time.sleep(5)
                        continue

                # 1. Process Uploads
                if self.upload_queue:
                    img_bytes = self.upload_queue.pop(0) # FIFO
                    self._upload_screenshot(img_bytes)

                # 2. Heartbeat (Periodic)
                if current_time - self.last_heartbeat >= self.heartbeat_interval:
                    self._send_heartbeat()
                    self._fetch_gamification() # Piggyback on heartbeat
                    self.last_heartbeat = current_time

            except Exception as e:
                logger.error(f"SyncWorker loop error: {e}")
            
            time.sleep(1) # Check queue every second

    def _fetch_gamification(self):
        try:
            data = self.client.get_gamification_profile()
            if data and 'profile' in data:
                self.gamification_update.emit(data['profile'])
        except Exception as e:
            logger.error(f"Gamification fetch error: {e}")

    def _send_heartbeat(self):
        try:
            res = self.client.send_heartbeat(
                app_name=self.current_state.get('app_name'),
                window_title=self.current_state.get('window_title'),
                is_idle=self.current_state.get('is_idle'),
                ollama_available=self.current_state.get('ollama_available'),
                ollama_models=self.current_state.get('ollama_models'),
                ollama_port=config.OLLAMA_PORT,
                tailscale_ip=self.current_state.get('tailscale_ip')
            )
            success = res.get('status') != 'failed'
            self.heartbeat_sent.emit(success)
        except Exception as e:
            logger.error(f"Heartbeat error: {e}")
            self.heartbeat_sent.emit(False)

    def _upload_screenshot(self, img_bytes):
        try:
            res = self.client.upload_screenshot(img_bytes)
            success = res.get('status') != 'failed'
            self.uploaded.emit(success)
        except Exception as e:
            logger.error(f"Upload error: {e}")
            self.uploaded.emit(False)

    def stop(self):
        self.running = False
        self.wait()
