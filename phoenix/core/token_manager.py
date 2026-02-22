"""
Secure token management for Phoenix Desktop Tracker.
Uses Windows Credential Manager to securely store authentication tokens.
"""
import os
import sys
import time
import logging
import getpass
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

logger = logging.getLogger(__name__)


class TokenManager:
    """Secure token storage and retrieval."""
    
    TARGET_NAME = f"PhoenixTracker_{config.DEVICE_ID}"
    FALLBACK_FILE = ".phoenix_token.enc"
    
    def __init__(self):
        """Initialize token manager."""
        if not WINDOWS_AVAILABLE:
            # Only print warning once or rely on logging
            if not hasattr(self, '_logged_warning'):
                print("⚠️  Warning: pywin32 not available. Using encrypted file storage as fallback.")
                self._logged_warning = True
            self._init_fallback_encryption()
    
    def _ensure_secure_permissions(self, file_path: Path) -> None:
        """
        Ensure file has strict permissions (0o600) on POSIX systems.
        Raises RuntimeError if permissions cannot be secured.
        """
        if not file_path.exists():
            return

        # Skip on Windows as chmod/stat behavior is different and we use DPAPI there normally
        if os.name == 'nt':
            return

        # 1. Try to set strict permissions (read/write for owner only)
        try:
            file_path.chmod(0o600)
        except Exception as e:
            # If chmod fails (e.g. not owner), we must check if it's already secure
            logger.warning(f"Failed to chmod {file_path}: {e}")

        # 2. Verify permissions
        try:
            # Check if group or others have any permissions
            # st_mode & 0o077 should be 0 for 0o600 (rw-------)
            # We explicitly want to forbid group/world access
            st = file_path.stat()
            if st.st_mode & 0o077:
                raise RuntimeError(
                    f"Insecure permissions on {file_path}: {oct(st.st_mode & 0o777)}. "
                    "File must be accessible only by owner (0o600)."
                )
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise
            raise RuntimeError(f"Failed to verify permissions on {file_path}: {e}")

    def _init_fallback_encryption(self):
        """Initialize fallback encryption key."""
        key_file = Path.home() / ".phoenix_key"

        # Try to read existing key first (with retry for race conditions)
        for attempt in range(3):
            if key_file.exists():
                try:
                    # Security: Ensure correct permissions on existing key
                    self._ensure_secure_permissions(key_file)

                    key = key_file.read_bytes()
                    if key and len(key) > 0:
                        self.encryption_key = key
                        return
                except Exception as e:
                    # If it's a security error, don't retry - fail hard?
                    # But we are in a retry loop for race conditions.
                    # If we can't secure it, maybe we should stop trying to read it?
                    if "Insecure permissions" in str(e):
                        logger.error(f"Security error reading key file: {e}")
                        # If the file is insecure and we can't fix it, we shouldn't use it.
                        # Break loop to force new key generation?
                        # No, generating a new key won't help if we can't write to the same location securely.
                        # And we can't decrypt existing data with a new key.
                        # Raising here will crash the app start, which is "Fail Secure".
                        raise

                    pass # Retry if read fails (e.g. locked file)
            else:
                break # File doesn't exist, proceed to creation

            # Wait briefly if file exists but read failed (maybe being written)
            time.sleep(0.1)

        # Generate new key and save atomically
        self.encryption_key = Fernet.generate_key()
        try:
            # Security: Use os.open to atomically create file with 0600 permissions
            # Use O_EXCL to fail if file already exists (prevent overwriting race condition)
            fd = os.open(str(key_file), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                os.write(fd, self.encryption_key)
            finally:
                os.close(fd)
        except FileExistsError:
            # Race condition: file created by another process between check and open
            # Wait for the other process to finish writing
            for attempt in range(5):
                try:
                    time.sleep(0.1)
                    key = key_file.read_bytes()
                    if key and len(key) > 0:
                        self.encryption_key = key
                        return
                except Exception:
                    pass

            # If still failing, we have a problem (permission or empty file)
            # Try to read one last time or re-raise
            try:
                self.encryption_key = key_file.read_bytes()
            except Exception as e:
                # Log error but don't crash if possible? No, we need encryption key.
                raise RuntimeError(f"Failed to initialize encryption key: {e}")
    
    def save_token(self, token: str) -> bool:
        """
        Store the authentication token securely.
        
        Args:
            token: JWT or API token to store
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if WINDOWS_AVAILABLE:
                self._store_windows(token)
            else:
                self._store_fallback(token)
            return True
        except Exception as e:
            # Security: Log error but avoid printing sensitive details to stdout
            logger.error(f"Failed to save token: {e}")
            print(f"Failed to save token: {type(e).__name__}")
            return False
    
    def _store_windows(self, token: str) -> None:
        """Store token using Windows Credential Manager."""
        credential = {
            'Type': win32cred.CRED_TYPE_GENERIC,
            'TargetName': self.TARGET_NAME,
            'UserName': config.DEVICE_ID,
            'CredentialBlob': token,
            'Comment': 'Phoenix Desktop Tracker Authentication Token',
            'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE
        }
        win32cred.CredWrite(credential, 0)
    
    def _store_fallback(self, token: str) -> None:
        """Store token using encrypted file (fallback)."""
        fernet = Fernet(self.encryption_key)
        encrypted = fernet.encrypt(token.encode())
        
        token_file = Path.home() / self.FALLBACK_FILE

        # Security: Ensure correct permissions if file already exists
        if token_file.exists():
            self._ensure_secure_permissions(token_file)

        # Security: Use os.open to atomically create file with 0600 permissions
        fd = os.open(str(token_file), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        try:
            os.write(fd, encrypted)
        finally:
            os.close(fd)
    
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
                Type=win32cred.CRED_TYPE_GENERIC,
                TargetName=self.TARGET_NAME
            )
            # Windows Credential Manager stores as UTF-16LE bytes
            token_bytes = credential['CredentialBlob']
            if isinstance(token_bytes, bytes):
                # Decode from UTF-16LE (Windows native encoding)
                return token_bytes.decode('utf-16le').rstrip('\x00')
            return token_bytes
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
                Type=win32cred.CRED_TYPE_GENERIC,
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
        
        token = getpass.getpass("Enter your device token: ").strip()
        
        if not token:
            print("❌ No token provided. Setup cancelled.")
            return False
        
        # Basic validation
        if len(token) < 20:
            print("❌ Token seems too short. Please check and try again.")
            return False
        
        try:
            self.save_token(token)
            print("✅ Token stored securely!")
            return True
        except Exception as e:
            # Security: Don't leak token in exception message
            logger.error(f"Failed to store token in setup wizard: {e}")
            print(f"❌ Failed to store token. Error: {type(e).__name__}")
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
