import requests
from token_manager import get_auth_token
import time

token = get_auth_token()
print(f"Testing token: {token[:20]}...{token[-20:]}")
print()

# Test 1: Minimal request
print("=== Test 1: Minimal Headers ===")
try:
    response = requests.post(
        "https://phoenix.aiwfe.com/api/screentime/heartbeat",
        json={
            'timestamp': time.time(),
            'app_name': "TestApp",
            'window_title': "Test Window",
            'is_idle': False
        },
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 2: With device_id header
print("=== Test 2: With X-Device-ID Header ===")
try:
    response = requests.post(
        "https://phoenix.aiwfe.com/api/screentime/heartbeat",
        json={
            'timestamp': time.time(),
            'app_name': "TestApp",
            'window_title': "Test Window",
            'is_idle': False
        },
        headers={
            'Authorization': f'Bearer {token}',
            'X-Device-ID': 'tufboi',
            'Content-Type': 'application/json'
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")

print()

# Test 3: With device_id in payload
print("=== Test 3: With device_id in JSON Payload ===")
try:
    response = requests.post(
        "https://phoenix.aiwfe.com/api/screentime/heartbeat",
        json={
            'timestamp': time.time(),
            'app_name': "TestApp",
            'window_title': "Test Window",  
            'is_idle': False,
            'device_id': 'tufboi'
        },
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
