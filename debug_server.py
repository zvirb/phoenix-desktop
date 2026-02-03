import sys
from pathlib import Path
import time
import requests

# Add phoenix/core to path
sys.path.insert(0, str(Path(__file__).parent / "phoenix" / "core"))

from config import config
from token_manager import get_auth_token

def debug_connection():
    token = get_auth_token()
    if not token:
        print("No token found.")
        return

    headers = {
        'Authorization': f'Bearer {token}',
        'X-Device-ID': config.DEVICE_ID,
        'User-Agent': f'PhoenixTracker/{config.DEVICE_ID}'
    }
    
    payload = {
        'timestamp': time.time(),
        'app_name': "DebugScript",
        'window_title': "Debug Window",
        'is_idle': False
    }
    
    print(f"Sending heartbeat to: {config.heartbeat_url}")

    # Create safe headers for logging
    safe_headers = headers.copy()
    if 'Authorization' in safe_headers:
        # Mask the token
        safe_headers['Authorization'] = f"Bearer {token[:4]}...{token[-4:]}" if len(token) > 8 else "***"

    print(f"Headers: {safe_headers}")
    
    try:
        response = requests.post(
            config.heartbeat_url,
            json=payload,
            headers=headers,
            verify=config.VERIFY_SSL
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print("Response Body:")
        print(response.text)
        
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    debug_connection()
