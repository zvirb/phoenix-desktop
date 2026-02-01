import requests
from token_manager import get_auth_token
from datetime import datetime
from config import config

token = get_auth_token()
print("Step 1: Authenticating...")
auth_response = requests.post(
    config.auth_url,
    headers={'Authorization': f'Bearer {token}'}
)
jwt_token = auth_response.json()['access_token']
print(f"✅ Authenticated! JWT: {jwt_token[:30]}...")

print("\nStep 2: Sending heartbeat with ISO timestamp...")
heartbeat_payload = {
    'timestamp': datetime.utcnow().isoformat() + 'Z',
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
print(f"\nStatus: {heartbeat_response.status_code}")
print(f"Response: {heartbeat_response.text}")

if heartbeat_response.status_code == 200:
    print("\n✅ SUCCESS! Heartbeat working!")
else:
    print(f"\n❌ Error: {heartbeat_response.status_code}")
