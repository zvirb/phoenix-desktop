"""
Secure token management for Phoenix Desktop Tracker.
Uses Windows Credential Manager to securely store authentication tokens.
"""
import sys
from typing import Optional

try:
    import win32cred
    import win32con
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False
    import base64
    from cryptography.fernet import Fernet
    from pathlib import Path

from config import config


class TokenManager:
    """Secure token storage and retrieval."""
    
    TARGET_NAME = f"PhoenixTracker_{config.DEVICE_ID}"
    FALLBACK_FILE = ".phoenix_token.enc"
    
    def __init__(self):
        """Initialize token manager."""
        if not WINDOWS_AVAILABLE:
            print("⚠️  Warning: pywin32 not available. Using encrypted file storage as fallback.")
            self._init_fallback_encryption()
    
    def _init_fallback_encryption(self):
        """Initialize fallback encryption key."""
        key_file = Path.home() / ".phoenix_key"
        if key_file.exists():
            self.encryption_key = key_file.read_bytes()
        else:
            self.encryption_key = Fernet.generate_key()
            key_file.write_bytes(self.encryption_key)
            key_file.chmod(0o600)  # Read/write for owner only
    
    def store_token(self, token: str) -> None:
        """
        Store the authentication token securely.
        
        Args:
            token: JWT or API token to store
        """
        if WINDOWS_AVAILABLE:
            self._store_windows(token)
        else:
            self._store_fallback(token)
    
    def _store_windows(self, token: str) -> None:
        """Store token using Windows Credential Manager."""
        credential = {
            'Type': win32con.CRED_TYPE_GENERIC,
            'TargetName': self.TARGET_NAME,
            'UserName': config.DEVICE_ID,
            'CredentialBlob': token,
            'Comment': 'Phoenix Desktop Tracker Authentication Token',
            'Persist': win32con.CRED_PERSIST_LOCAL_MACHINE
        }
        win32cred.CredWrite(credential, 0)
    
    def _store_fallback(self, token: str) -> None:
        """Store token using encrypted file (fallback)."""
        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(token.encode())
        
        token_file = Path.home() / self.FALLBACK_FILE
        token_file.write_bytes(encrypted)
        token_file.chmod(0o600)
    
    def get_token(self) -> Optional[str]:
        """
        Retrieve the authentication token.
        
        Returns:
            The stored token, or None if not found
        """
        if WINDOWS_AVAILABLE:
            return self._get_windows()
        else:
            return self._get_fallback()
    
    def _get_windows(self) -> Optional[str]:
        """Retrieve token from Windows Credential Manager."""
        try:
            credential = win32cred.CredRead(
                Type=win32con.CRED_TYPE_GENERIC,
                TargetName=self.TARGET_NAME
            )
            return credential['CredentialBlob']
        except Exception:
            return None
    
    def _get_fallback(self) -> Optional[str]:
        """Retrieve token from encrypted file (fallback)."""
        try:
            token_file = Path.home() / self.FALLBACK_FILE
            if not token_file.exists():
                return None
            
            encrypted = token_file.read_bytes()
            fernet = Fernet(self.encryption_key)
            return fernet.decrypt(encrypted).decode()
        except Exception:
            return None
    
    def delete_token(self) -> None:
        """Delete the stored token."""
        if WINDOWS_AVAILABLE:
            self._delete_windows()
        else:
            self._delete_fallback()
    
    def _delete_windows(self) -> None:
        """Delete token from Windows Credential Manager."""
        try:
            win32cred.CredDelete(
                Type=win32con.CRED_TYPE_GENERIC,
                TargetName=self.TARGET_NAME
            )
        except Exception:
            pass
    
    def _delete_fallback(self) -> None:
        """Delete encrypted token file."""
        try:
            token_file = Path.home() / self.FALLBACK_FILE
            if token_file.exists():
                token_file.unlink()
        except Exception:
            pass
    
    def has_token(self) -> bool:
        """Check if a token is stored."""
        return self.get_token() is not None
    
    def setup_wizard(self) -> bool:
        """
        Interactive setup wizard to configure the token.
        
        Returns:
            True if token was successfully configured
        """
        print("=" * 60)
        print("Phoenix Desktop Tracker - Token Setup")
        print("=" * 60)
        print()
        print("To get your device token:")
        print("1. Log into the Phoenix Web Dashboard")
        print("2. Navigate to Settings > Devices")
        print("3. Click 'Generate New Device Token'")
        print(f"4. Name it: {config.DEVICE_ID}")
        print("5. Copy the token and paste it below")
        print()
        
        token = input("Enter your device token: ").strip()
        
        if not token:
            print("❌ No token provided. Setup cancelled.")
            return False
        
        # Basic validation
        if len(token) < 20:
            print("❌ Token seems too short. Please check and try again.")
            return False
        
        try:
            self.store_token(token)
            print("✅ Token stored securely!")
            return True
        except Exception as e:
            print(f"❌ Failed to store token: {e}")
            return False


# Convenience function
def get_auth_token() -> Optional[str]:
    """Get the authentication token, running setup if needed."""
    manager = TokenManager()
    
    if not manager.has_token():
        print("⚠️  No authentication token found.")
        if not manager.setup_wizard():
            return None
    
    return manager.get_token()


if __name__ == "__main__":
    # Allow running this module directly for token management
    import argparse
    
    parser = argparse.ArgumentParser(description="Manage Phoenix authentication token")
    parser.add_argument('action', choices=['setup', 'delete', 'show'], 
                       help='Action to perform')
    args = parser.parse_args()
    
    manager = TokenManager()
    
    if args.action == 'setup':
        manager.setup_wizard()
    elif args.action == 'delete':
        manager.delete_token()
        print("✅ Token deleted")
    elif args.action == 'show':
        token = manager.get_token()
        if token:
            # Show only first and last 4 characters for security
            masked = f"{token[:4]}...{token[-4:]}" if len(token) > 8 else "***"
            print(f"Token: {masked}")
        else:
            print("❌ No token stored")
