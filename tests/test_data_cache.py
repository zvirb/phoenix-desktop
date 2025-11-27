import unittest
import os
import time
import json
import sqlite3
from data_cache import DataCache

class TestDataCache(unittest.TestCase):
    def setUp(self):
        self.test_db = f"test_cache_{int(time.time()*1000)}.db"
        self.cleanup_db()
        self.cache = DataCache(self.test_db)
        
    def tearDown(self):
        self.cleanup_db()
        
    def cleanup_db(self):
        if os.path.exists(self.test_db):
            for _ in range(3):
                try:
                    os.remove(self.test_db)
                    break
                except PermissionError:
                    time.sleep(0.1)
                
    def test_add_and_get_item(self):
        data = {"key": "value"}
        self.cache.add_item("test_type", data)
        
        items = self.cache.get_pending_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][1], "test_type")
        self.assertEqual(items[0][2], data)
        self.assertIsNone(items[0][3])
        
    def test_add_item_with_file(self):
        data = {"meta": "data"}
        file_data = b"binary_data"
        self.cache.add_item("screenshot", data, file_data)
        
        items = self.cache.get_pending_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][1], "screenshot")
        self.assertEqual(items[0][3], file_data)
        
    def test_remove_item(self):
        self.cache.add_item("item1", {})
        items = self.cache.get_pending_items()
        item_id = items[0][0]
        
        self.assertTrue(self.cache.remove_item(item_id))
        self.assertEqual(len(self.cache.get_pending_items()), 0)
        
    def test_clear_cache(self):
        self.cache.add_item("item1", {})
        self.cache.add_item("item2", {})
        self.assertEqual(len(self.cache.get_pending_items()), 2)
        
        self.cache.clear_cache()
        self.assertEqual(len(self.cache.get_pending_items()), 0)
        
    def test_get_stats(self):
        self.cache.add_item("item1", {})
        stats = self.cache.get_stats()
        self.assertEqual(stats['count'], 1)
        self.assertGreater(stats['size_bytes'], 0)

if __name__ == '__main__':
    unittest.main()
