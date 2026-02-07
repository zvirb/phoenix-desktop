"""
Quick script to update the authentication token.
"""
import getpass
from token_manager import TokenManager

print("=" * 60)
print("Phoenix Desktop Tracker - Token Update")
print("=" * 60)
print()
print("To get your device token:")
print("1. Log into the Phoenix Web Dashboard")
print("2. Navigate to Settings > Devices")
print("3. Click 'Generate New Device Token'")
print("4. Name it: tufboi")
print("5. Copy the token and paste it below")
print()

token = getpass.getpass("Enter your new device token: ").strip()

if not token:
    print("❌ No token provided. Update cancelled.")
    exit(1)

# Basic validation
if len(token) < 20:
    print("❌ Token seems too short. Please check and try again.")
    exit(1)

manager = TokenManager()
if manager.save_token(token):
    print("✅ Token updated successfully!")
    print()
    print("Please restart the Phoenix Tracker for changes to take effect.")
else:
    print("❌ Failed to save token. Please check the error above.")
    exit(1)
