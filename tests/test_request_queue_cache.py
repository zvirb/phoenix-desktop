
import unittest
import unittest.mock
import os
import shutil
import tempfile
import threading
from pathlib import Path

# Setup mock environment before importing
import sys
# Ensure we can import from phoenix.core
sys.path.append(os.getcwd())

from phoenix.core.request_queue import RequestQueue

class TestRequestQueueCache(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()

        # Patch HOME and LOCALAPPDATA to point to temp dir
        self.patcher = unittest.mock.patch.dict(os.environ, {
            'LOCALAPPDATA': self.test_dir.name,
            'HOME': self.test_dir.name
        })
        self.patcher.start()

        # Manually set db path relative to temp dir
        self.db_name = "test_queue.db"

    def tearDown(self):
        self.patcher.stop()
        self.test_dir.cleanup()

    def test_cache_consistency(self):
        # 1. Initialize queue
        queue = RequestQueue(self.db_name)

        # Initial count should be 0
        self.assertEqual(queue.count(), 0)
        self.assertEqual(len(queue.peek()), 0)

        # 2. Add items
        res = queue.add("/api/test/1", "POST", {"data": "test1"})
        self.assertTrue(res)
        self.assertEqual(queue.count(), 1)

        res = queue.add("/api/test/2", "POST", {"data": "test2"})
        self.assertTrue(res)
        self.assertEqual(queue.count(), 2)

        # Verify peek
        items = queue.peek()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]['endpoint'], "/api/test/1")

        # 3. Pop items
        first_id = items[0]['id']
        queue.pop(first_id)
        self.assertEqual(queue.count(), 1)

        # Pop non-existent item (should not change count)
        queue.pop(9999)
        self.assertEqual(queue.count(), 1)

        # Pop last item
        second_id = items[1]['id']
        queue.pop(second_id)
        self.assertEqual(queue.count(), 0)

    def test_persistence(self):
        # 1. Initialize and add items
        queue1 = RequestQueue(self.db_name)
        queue1.add("/api/test/1", "POST")
        queue1.add("/api/test/2", "POST")
        self.assertEqual(queue1.count(), 2)

        # 2. Close and reopen (simulate restart)
        # RequestQueue relies on sqlite3 connection per thread.
        # Create a new instance pointing to same DB.
        queue2 = RequestQueue(self.db_name)

        # Verify count is restored from DB
        self.assertEqual(queue2.count(), 2)

        # Verify cache works on new instance
        queue2.add("/api/test/3", "POST")
        self.assertEqual(queue2.count(), 3)

        # Original instance cache is stale (expected limitation of simple cache)
        self.assertEqual(queue1.count(), 2)

if __name__ == '__main__':
    unittest.main()
