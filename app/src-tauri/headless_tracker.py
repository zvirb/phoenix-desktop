"""
Phoenix Desktop Sidecar (Headless)
Refactored logic for usage with Tauri (or other hosts).
Handles telemetry sensing, logic separation, and stdout/json-ipc.
"""
import sys
import os
import json
import time
import logging
import threading
from pathlib import Path

# Add parent directory to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from windows_settings import settings_manager
from token_manager import TokenManager
from api_client import create_client
from window_detector import WindowDetector
from activity_detector import ActivityDetector
from gaming_detector import GamingDetector
from inference_detector import InferenceDetector
import mss
from PIL import Image
from io import BytesIO

# Configure basic logging to file, but NOT to stdout (stdout is for IPC)
app_data_dir = Path(os.path.expandvars('%LOCALAPPDATA%')) / "PhoenixTracker"
log_dir = app_data_dir / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "phoenix_sidecar.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler(str(log_file))]
)
logger = logging.getLogger("Sidecar")

def emit_event(event_type: str, data: dict):
    """Emit a JSON event to Stdout."""
    payload = {
        "event": event_type,
        "payload": data,
        "timestamp": time.time()
    }
    # Print JSON line for the host process to read
    print(json.dumps(payload), flush=True)

def get_active_window_title():
    try:
        import win32gui
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except Exception:
        return "Unknown"

class SessionContext:
    """Manages the current user session context for filtering."""
    def __init__(self):
        self.status = "active"
        self.active_time_start = time.time()
        self.cumulative_active_seconds = 0
        self.last_input_time = time.time()
        self.is_agent_activity = False # Default: Human
        self.current_window = "Unknown"

    def update_input(self, is_active: bool, is_simulated: bool):
        """Update context based on input activity."""
        now = time.time()
        self.current_window = get_active_window_title()

        if is_active:
            if self.status == "idle":
                self.status = "active"
                self.active_time_start = now # Reset active time for new active period
                emit_event("session_resumed", {"window": self.current_window})
            self.cumulative_active_seconds += (now - self.last_input_time) if self.status == "active" else 0
            self.last_input_time = now
            self.is_agent_activity = is_simulated
        else:
            if self.status == "active":
                # check if truly idle
                if (now - self.last_input_time) > 45: # 45s hardcoded idle trigger
                    self.status = "idle"
                    emit_event("session_paused", {"duration": self.cumulative_active_seconds})

    def get_snapshot(self):
        return {
            "status": self.status,
            "active_time_seconds": int(self.cumulative_active_seconds),
            "is_agent_activity": self.is_agent_activity
        }

class HeadlessTracker:
    def __init__(self):
        self.running = False
        self.token_manager = TokenManager()
        self.api_client = None
        
        # Detectors
        self.window_detector = WindowDetector()
        self.activity_detector = ActivityDetector()
        self.gaming_detector = GamingDetector()
        self.inference_detector = InferenceDetector(
             ollama_host=f"http://localhost:{settings_manager.get_ollama_port()}"
        )
        
        self.context = SessionContext()
        self.last_heartbeat = 0
        self.last_capture = 0
    
    def initialize(self):
        """Prepare client connection."""
        try:
            # Need to verify if we can run without settings UI flow
            # Retrieve token
            token = self.token_manager.get_token()
            if not token:
                emit_event("error", {"code": "AUTH_REQUIRED", "message": "No token found"})
                return False
                
            # Get Configured URL
            base_url = settings_manager.get_phoenix_url()
            if not base_url:
                base_url = "http://localhost:8000" # Fallback
                
            self.api_client = create_client(
                 base_url=base_url,
                 device_id=settings_manager.get_device_id(),
                 verify_ssl=settings_manager.get_verify_ssl()
            )
            # Authenticate - API Client stores access_token internally
            auth = self.api_client.authenticate(token)
            if auth.get('status') == 'failed':
                 emit_event("error", {"code": "AUTH_FAILED", "message": auth.get('error')})
                 return False
            
            # Extract JWT from auth response or client state
            jwt_token = auth.get("access_token")
            # If not in response (fallback), check client
            if not jwt_token and self.api_client.token:
                jwt_token = self.api_client.token
                 
            logger.info(f"Authenticated successfully. API: {base_url}")
            emit_event("ready", {
                "username": auth.get("display_name", "User"), 
                "token": jwt_token, # Send JWT, not device token
                "api_url": base_url,
                "user_id": auth.get("user_id")
            })

            # Start Input Listener
            self.start_input_listener()
            return True
        except Exception as e:
            logger.error(f"Init failed: {e}", exc_info=True)
            import traceback
            emit_event("error", {"code": "INIT_CRASH", "message": f"{str(e)} | {traceback.format_exc()}"})
            return False

    def start_input_listener(self):
        """Listen for commands from Host (Rust) via Stdin."""
        def listen():
            while self.running:
                try:
                    line = sys.stdin.readline()
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        cmd = json.loads(line)
                        cmd_type = cmd.get("command")

                        # Log command type only, not full payload which may contain PII
                        logger.info(f"Received command: {cmd_type}")

                        if cmd_type == "capture":
                            self.process_screenshot(is_manual=True)
                        elif cmd_type == "decompose":
                            text = cmd.get("text", "")
                            self.decompose_task(text)
                    except json.JSONDecodeError:
                        logger.warning("Invalid JSON command")
                except Exception as e:
                    logger.error(f"Stdin error: {e}")

        t = threading.Thread(target=listen, daemon=True)
        t.start()

    def decompose_task(self, text):
        """Calls the decomposition API via the sidecar client."""
        try:
             # Basic Validation
             if not text or len(text) > 500:
                 emit_event("decomposition_result", {"success": False, "error": "Input too long or empty"})
                 return

             # Construct URL. Assuming /api/v1/preview-decompose exists on the stack
             # If using configured URL with path, we should be careful.
             # self.api_client.base_url might be "https://phoenix.aiwfe.com"
             url = f"{self.api_client.base_url.rstrip('/')}/api/v1/preview-decompose"
             
             # Mask text in logs
             masked_text = f"{text[:10]}..." if len(text) > 10 else "***"
             logger.info(f"Decomposing: {masked_text} to {url}")
             
             import requests
             # Use the JWT token if available, else device token (fallback, though likely to fail)
             token = self.api_client.token or self.token_manager.get_token()
             
             headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
             payload = {"task_title": text, "user_id": "current_user"}
             
             res = requests.post(url, json=payload, headers=headers, timeout=10,
                                 verify=settings_manager.get_verify_ssl())
                                 
             if res.status_code in [200, 201]:
                 data = res.json()
                 emit_event("decomposition_result", {"success": True, "data": data})
             else:
                 emit_event("decomposition_result", {"success": False, "error": f"Status {res.status_code}"})
                 
        except Exception as e:
            logger.error(f"Decompose Error: {e}")
            emit_event("decomposition_result", {"success": False, "error": str(e)})

    def connect_intervention_socket(self):
        """Connects to the Adaptive Intervention service via WebSocket."""
        def on_message(ws, message):
            try:
                data = json.loads(message)
                # Emit to Host
                emit_event("health_nudge", data)
                logger.info(f"Intervention received: {data}")
            except Exception as e:
                logger.error(f"WS Msg Error: {e}")

        def on_error(ws, error):
            logger.error(f"WS Error: {error}")
            # Reconnect logic should be here (e.g. wait and retry)

        def on_close(ws, close_status_code, close_msg):
            logger.info("WS Closed")

        def run_socket():
             # Derive WS URL from API URL
             # http://host:port -> ws://host:port
             # https://host:port -> wss://host:port
             base = self.api_client.base_url
             if base.startswith("http"):
                  ws_base = base.replace("http", "ws", 1)
             else:
                  ws_base = f"wss://{base}"
             
             # Assuming endpoint is /ws/{user_id} or just /ws
             # Let's try /ws/current_user or just /ws if gateway handles it
             # Integration guide says: ws://phoenix-adaptive-intervention:8000/ws/{user_id}
             # If using Gateway: likely /api/v1/interventions/ws or similar?
             # Or just /ws base on the intervention service port?
             
             # If using config, we might need a dedicated setting for WS or Interventions URL if not same as API.
             # User said "Old method" worked. 
             # Let's try constructing it from the base.
             
             ws_url = f"{ws_base.rstrip('/')}/ws/current_user"
             logger.info(f"Connecting WS: {ws_url}")
             
             import websocket
             ws = websocket.WebSocketApp(ws_url,
                                         on_message=on_message,
                                         on_error=on_error,
                                         on_close=on_close)
             while self.running:
                 try:
                     ws.run_forever()
                     time.sleep(5) # Reconnect delay
                 except Exception:
                     time.sleep(10)

        t = threading.Thread(target=run_socket, daemon=True)
        t.start()
        
    def loop(self):
        """Main blocking loop."""
        self.running = True
        logger.info("Starting headless loop")
        
        # Start WS for interventions
        try:
             import websocket
             self.connect_intervention_socket()
        except ImportError:
             logger.warning("websocket-client not installed. Adaptive Interventions disabled.")
        except Exception as e:
             logger.error(f"Failed to start WS: {e}")
        
        while self.running:
            try:
                now = time.time()
                
                # 1. Update Context (Active/Idle) using WindowDetector
                # Note: window_detector uses GetLastInputInfo which is global (human) usage
                # But it doesn't distinguish simulated vs real unless we hook LL hooks.
                # For now, we trust GetLastInputInfo as "Activity", and default is_agent_activity=False
                # future: integration with 'pyautogui' hooks to detect self-injection?
                is_idle = self.window_detector.is_idle(idle_threshold=15)
                self.context.update_input(not is_idle, is_simulated=False)
                
                # Emit Context Update (The NEW Requirement)
                # We emit this frequently (every 5s? or only on change?)
                # Requirement implies strict compliance, doing it on heartbeat cadence matching 'context_update'
                
                # 2. Check Gaming
                if self.gaming_detector.is_gaming():
                     emit_event("status", {"mode": "gaming", "game": self.gaming_detector.get_running_game()})
                     time.sleep(60)
                     continue
                
                # 3. Heartbeat / Context Update
                # We replace the old "Heartbeat" with logic that sends the new payload if requested
                # or we default to the old heartbeat for `api_client` compatibility?
                # Ideally, we send the new WebSocket payload if a WS client was implemented.
                # Since we don't have the WS client in Python yet, we just emit to Tauri.
                # TAURI will handle the WebSocket connection to `phoenix-adaptive-intervention`.
                emit_event("context_update", self.context.get_snapshot())
                
                # 4. Old API Heartbeat (Legacy compatibility for phoenix-core)
                if (now - self.last_heartbeat) > settings_manager.get_heartbeat_interval():
                     self.perform_legacy_heartbeat()
                     self.last_heartbeat = now
                
                # 5. Screenshot Logic
                if (now - self.last_capture) > settings_manager.get_capture_interval():
                     if not is_idle:
                         self.process_screenshot()
                         self.last_capture = now
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                self.running = False
                break
            except Exception as e:
                logger.error(f"Loop error: {e}")
                emit_event("log", {"level": "error", "message": str(e)})
                time.sleep(5)

    def perform_legacy_heartbeat(self):
         app, title = self.window_detector.get_active_window()
         self.api_client.send_heartbeat(
             app_name=app,
             window_title=title,
             is_idle=False, # We are active if we are here?
             ollama_available=False,
             ollama_models=[],
             ollama_port=11434,
             tailscale_ip="unknown"
         )

    def process_screenshot(self, is_manual: bool = False):
        try:
            with mss.mss() as sct:
                # Capture all monitors (monitor 0) roughly for now, or just primary
                monitor = sct.monitors[1] # Primary
                # Capture
                img = sct.grab(monitor)
                # Convert to PIL
                pil_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
                
                # Save to buffer
                buf = BytesIO()
                pil_img.save(buf, format="JPEG", quality=60)
                buf.seek(0)
                
                # If manual, send to Media Processor (OCR)
                if is_manual:
                     emit_event("ocr_status", {"status": "processing"})
                     # Sending to Phoenix Media Processor
                     # http://phoenix-media-processor:8000/capture/ocr
                     # We use 'localhost:8002' mapping via forward_services.bat
                     url = f"http://localhost:8002/capture/ocr"
                     files = {'file': ('screenshot.jpg', buf, 'image/jpeg')}
                     # We need the token for this? Media processor might be internal only or need auth.
                     # Assuming no auth for internal sidecar or same token.
                     # Let's try without first.
                     try:
                         import requests
                         res = requests.post(url, files=files, timeout=10)
                         if res.status_code == 200:
                             text = res.json().get("text", "")
                             emit_event("ocr_result", {"text": text})
                         else:
                             emit_event("error", {"code": "OCR_FAIL", "message": f"Status {res.status_code}"})
                     except Exception as e:
                         emit_event("error", {"code": "OCR_NET_FAIL", "message": str(e)})

        except Exception as e:
            logger.error(f"Screenshot failed: {e}")

if __name__ == "__main__":
    tracker = HeadlessTracker()
    if tracker.initialize():
        tracker.loop()
