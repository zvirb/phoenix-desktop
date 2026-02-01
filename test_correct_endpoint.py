import requests
from token_manager import get_auth_token

token = get_auth_token()
print(f"Testing device authentication with token: {token[:20]}...{token[-20:]}")
print()

# Test the CORRECT device authentication endpoint
print("=== Testing /api/v1/devices/authenticate ===")
try:
    response = requests.post(
        "https://phoenix.aiwfe.com/api/v1/devices/authenticate",
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✅ Authentication successful!")
        print(f"User ID: {data.get('user_id')}")
        print(f"Email: {data.get('email')}")
        print(f"Display Name: {data.get('display_name')}")
        print(f"Device Name: {data.get('device_name')}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)

# Now test the heartbeat endpoint (should work after auth)
print("\n=== Testing /api/v1/screentime/heartbeat ===")
import time
try:
    response = requests.post(
        "https://phoenix.aiwfe.com/api/v1/screentime/heartbeat",
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={
            'timestamp': time.time(),
            'app_name': 'TestApp',
            'window_title': 'Test Window',
            'is_idle': False
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
