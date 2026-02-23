
import unittest
import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

# Add project root to path
import sys
sys.path.append(os.getcwd())

# Mock Windows-specific modules to allow import on Linux
patch.dict(sys.modules, {
    'win32crypt': None,
}).start()

from phoenix.core.request_queue import RequestQueue

class TestRequestQueueSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_name = "test_queue.db"
        self.db_path = Path(self.test_dir) / "PhoenixTracker" / self.db_name

        # Patch LOCALAPPDATA/HOME to point to our test dir
        self.env_patcher = patch.dict(os.environ, {
            'LOCALAPPDATA': self.test_dir,
            'HOME': self.test_dir
        })
        self.env_patcher.start()

    def tearDown(self):
        self.env_patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_database_permissions(self):
        """
        Test that RequestQueue database file has secure permissions (0600).
        """
        if os.name == 'nt':
            print("Skipping permission test on Windows")
            return

        # Initialize RequestQueue
        queue = RequestQueue(db_name=self.db_name)

        # Verify file exists
        self.assertTrue(queue.db_path.exists())

        # Check permissions
        st = queue.db_path.stat()
        permissions = st.st_mode & 0o777

        # We expect 0o600 (rw-------)
        # If it's 0o644 (rw-r--r--), it's insecure
        if permissions != 0o600:
            print(f"Permissions are: {oct(permissions)}")

        self.assertEqual(permissions, 0o600,
                        f"Insecure permissions on {queue.db_path}: {oct(permissions)}. Expected 0o600.")

if __name__ == '__main__':
    unittest.main()
