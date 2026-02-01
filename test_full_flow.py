import requests
from token_manager import get_auth_token
import time
from config import config

token = get_auth_token()
print("Step 1: Authenticating with device token...")
auth_response = requests.post(
    config.auth_url,
    headers={'Authorization': f'Bearer {token}'}
)
print(f"Auth Status: {auth_response.status_code}")
auth_data = auth_response.json()
print(f"Auth Response: {auth_data}")

jwt_token = auth_data['access_token']
print(f"\nJWT Token: {jwt_token[:50]}...")

print("\nStep 2: Sending heartbeat with JWT...")
heartbeat_payload = {
    'timestamp': time.time(),
    'app_name': 'TestApp',
    'window_title': 'Test Window',
    'is_idle': False
}
print(f"Payload: {heartbeat_payload}")

heartbeat_response = requests.post(
    config.heartbeat_url,
    headers={'Authorization': f'Bearer {jwt_token}'},
    json=heartbeat_payload
)
print(f"\nHeartbeat Status: {heartbeat_response.status_code}")
print(f"Heartbeat Response: {heartbeat_response.text}")
