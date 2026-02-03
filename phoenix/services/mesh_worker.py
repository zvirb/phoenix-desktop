import time
import logging
from PyQt6.QtCore import QThread, pyqtSignal

from phoenix.core.inference_detector import InferenceDetector
# from config import config # If needed

logger = logging.getLogger(__name__)

class MeshWorker(QThread):
    """
    Background worker for discovering Mesh capabilities.
    Checks for:
    1. Local Ollama instance (Inference)
    2. Tailscale Identity (Network)
    3. Phoenix Core Heartbeat (Connectivity)
    """
    # Signals
    inference_status = pyqtSignal(bool)   # ready/not ready
    network_status = pyqtSignal(bool)     # connected/disconnected
    mesh_info_ready = pyqtSignal(dict)    # Full status dict

    def __init__(self):
        super().__init__()
        self.running = True
        self.inference_detector = InferenceDetector() # Defaults to localhost:11450
        self.check_interval = 30 # Check every 30s

    def run(self):
        logger.info("MeshWorker started")
        while self.running:
            try:
                # 1. Check Inference
                status = self.inference_detector.get_inference_status()
                
                ollama_ok = status.get('ollama_available', False)
                tailscale_ip = status.get('tailscale_ip')
                
                # Emit simple boolean statuses for UI badges
                self.inference_status.emit(ollama_ok)
                self.network_status.emit(tailscale_ip is not None)
                
                # Emit full info
                self.mesh_info_ready.emit(status)

            except Exception as e:
                logger.error(f"Error in MeshWorker loop: {e}")
                
            # Sleep (chunked to allow fast stop)
            for _ in range(self.check_interval):
                if not self.running: break
                time.sleep(1)

    def stop(self):
        self.running = False
        self.wait()
