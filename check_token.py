"""
Check what token is currently stored.
"""
import sys
import os
from pathlib import Path

# Add phoenix/core to path
sys.path.insert(0, str(Path(__file__).parent / "phoenix" / "core"))

from token_manager import TokenManager

manager = TokenManager()
token = manager.get_token()

if token:
    print(f"Token found: {len(token)} characters")
    # Mask the token for security
    masked = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
    print(f"Token: {masked}")
else:
    print("No token found!")
