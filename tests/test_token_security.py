
import unittest
import os
import sys
import stat
import tempfile
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add repo root to path
sys.path.insert(0, os.getcwd())

class TestTokenSecurity(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for tests
        self.test_dir = tempfile.TemporaryDirectory()
        self.home_patcher = patch('pathlib.Path.home')
        self.mock_home = self.home_patcher.start()
        self.mock_home.return_value = Path(self.test_dir.name)

        # Paths for files in temp dir
        self.key_file = Path(self.test_dir.name) / ".phoenix_key"
        self.token_file = Path(self.test_dir.name) / ".phoenix_token.enc"

        # Mock winreg manually
        self.original_modules = {}
        for mod in ['winreg', 'win32cred', 'win32con']:
            if mod in sys.modules:
                self.original_modules[mod] = sys.modules[mod]

        sys.modules['winreg'] = MagicMock()
        sys.modules['win32cred'] = None # Ensure ImportError
        sys.modules['win32con'] = MagicMock()

        # Mock config
        self.config_patcher = patch('config.config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.DEVICE_ID = "test-device"

        # We need to reload TokenManager to pick up the mocks
        if 'phoenix.core.token_manager' in sys.modules:
            del sys.modules['phoenix.core.token_manager']

    def tearDown(self):
        # Restore sys.modules
        for mod in ['winreg', 'win32cred', 'win32con']:
            if mod in self.original_modules:
                sys.modules[mod] = self.original_modules[mod]
            else:
                if mod in sys.modules:
                    del sys.modules[mod]

        self.config_patcher.stop()
        self.home_patcher.stop()
        self.test_dir.cleanup()

    def check_permissions(self, filepath):
        """Check if file has 0600 permissions."""
        st = os.stat(filepath)
        mode = st.st_mode
        perms = mode & 0o777
        return perms == 0o600

    def test_secure_file_creation(self):
        from phoenix.core.token_manager import TokenManager

        # Instantiate
        manager = TokenManager()

        # Verify key file
        self.assertTrue(self.key_file.exists(), "Key file should be created")
        self.assertTrue(self.check_permissions(self.key_file), f"Key file permissions should be 0600, got {oct(os.stat(self.key_file).st_mode & 0o777)}")

        # Save token
        manager.save_token("test_token_123")

        # Verify token file
        self.assertTrue(self.token_file.exists(), "Token file should be created")
        self.assertTrue(self.check_permissions(self.token_file), f"Token file permissions should be 0600, got {oct(os.stat(self.token_file).st_mode & 0o777)}")

    def test_fix_existing_insecure_file(self):
        """Test that if token file exists with insecure permissions, it is fixed or replaced."""
        from phoenix.core.token_manager import TokenManager

        # Create insecure token file
        self.token_file.touch()
        self.token_file.chmod(0o666)

        # Verify it's insecure
        self.assertFalse(self.check_permissions(self.token_file), "Token file should be insecure initially")

        # Instantiate
        manager = TokenManager()

        # Save token - should fix permissions
        manager.save_token("test_token_123")

        # Verify token file is now secure
        self.assertTrue(self.check_permissions(self.token_file), "Token file permissions should be fixed to 0600")

    def test_fix_existing_insecure_key_file(self):
        """Test that if key file exists with insecure permissions, it is fixed."""
        from cryptography.fernet import Fernet
        from phoenix.core.token_manager import TokenManager

        # Create insecure key file
        key = Fernet.generate_key()
        self.key_file.write_bytes(key)
        self.key_file.chmod(0o666)

        # Verify it's insecure
        self.assertFalse(self.check_permissions(self.key_file), "Key file should be insecure initially")

        # Instantiate TokenManager - triggers _init_fallback_encryption which reads key
        manager = TokenManager()

        # Verify key file is now secure
        self.assertTrue(self.check_permissions(self.key_file), "Key file permissions should be fixed to 0600")

if __name__ == "__main__":
    unittest.main()
