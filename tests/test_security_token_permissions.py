
import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add project root to path
sys.path.append(os.getcwd())

# Mock Windows-specific modules to allow import on Linux
# We need to do this BEFORE importing any project modules
mock_winreg = MagicMock()
mock_winreg.HKEY_CURRENT_USER = 0
mock_winreg.KEY_WRITE = 1
mock_winreg.KEY_READ = 2
mock_winreg.REG_SZ = 3
mock_winreg.REG_DWORD = 4
patch.dict(sys.modules, {
    'winreg': mock_winreg,
    'win32cred': None,
    'win32con': None
}).start()

# Now we can safely import
from phoenix.core.token_manager import TokenManager

class TestTokenManagerSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path("test_security_tmp")
        self.test_dir.mkdir(exist_ok=True)
        self.key_file = self.test_dir / ".phoenix_key"

        # Patch Path.home to return our test dir
        self.home_patcher = patch('pathlib.Path.home', return_value=self.test_dir)
        self.mock_home = self.home_patcher.start()

    def tearDown(self):
        self.home_patcher.stop()
        if self.key_file.exists():
            try:
                self.key_file.unlink()
            except:
                pass
        if self.test_dir.exists():
            try:
                self.test_dir.rmdir()
            except:
                pass

    def test_insecure_key_file_handling(self):
        """
        Test that TokenManager raises RuntimeError when key file has insecure permissions
        and chmod fails to fix them.
        """
        self.key_file.write_bytes(b"A" * 32) # 32 bytes key

        # Patch Path.chmod to raise an exception, simulating failure to secure
        with patch.object(Path, 'chmod', side_effect=PermissionError("Mock permission error")):
            # Patch Path.stat to return insecure permissions (0o644)
            # st_mode=0o100644 (S_IFREG | 0644)
            # tuple: (st_mode, st_ino, st_dev, st_nlink, st_uid, st_gid, st_size, st_atime, st_mtime, st_ctime)
            mock_stat = os.stat_result((0o100644, 0, 0, 0, 0, 0, 0, 0, 0, 0))

            with patch.object(Path, 'stat', return_value=mock_stat):
                # We expect RuntimeError because strict permission check should fail
                with self.assertRaises(RuntimeError) as cm:
                    TokenManager()

                self.assertIn("Insecure permissions", str(cm.exception))
                print("\n[SUCCESS] TokenManager correctly refused insecure key file.")

if __name__ == '__main__':
    unittest.main()
