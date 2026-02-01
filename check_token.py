"""
Check what token is currently stored.
"""
from token_manager import TokenManager

manager = TokenManager()
token = manager.get_token()

if token:
    print(f"Token found: {len(token)} characters")
    print(f"First 20 chars: {token[:20]}")
    print(f"Last 20 chars: {token[-20:]}")
    print(f"Full token: {token}")
else:
    print("No token found!")
