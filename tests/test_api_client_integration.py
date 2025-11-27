import unittest
from unittest.mock import MagicMock, patch
import os
import json
import time
import requests
from api_client import APIClient
from data_cache import DataCache

class TestAPIClientIntegration(unittest.TestCase):
    def setUp(self):
        # Mock config and token
        self.config_patcher = patch('api_client.config')
        self.mock_config = self.config_patcher.start()
        self.mock_config.DEVICE_ID = "test_device"
        self.mock_config.VERIFY_SSL = False
        self.mock_config.heartbeat_url = "http://test.com/heartbeat"
        self.mock_config.capture_url = "http://test.com/capture"
        self.mock_config.REQUEST_TIMEOUT = 5
        
        self.token_patcher = patch('api_client.get_auth_token')
        self.mock_get_token = self.token_patcher.start()
        self.mock_get_token.return_value = "test_token"
        
        # Use a test database for cache
        self.test_db = f"test_integration_cache_{int(time.time()*1000)}.db"
        self.cleanup_db()
            
        # Patch DataCache class in api_client to use test db
        self.original_datacache = DataCache
        
        self.datacache_cls_patcher = patch('api_client.DataCache')
        self.mock_datacache_cls = self.datacache_cls_patcher.start()
        # When DataCache() is called, return a real instance with test_db
        self.mock_datacache_cls.side_effect = lambda: self.original_datacache(self.test_db)
        
        self.client = APIClient()
        
    def tearDown(self):
        self.config_patcher.stop()
        self.token_patcher.stop()
        self.datacache_cls_patcher.stop()
        self.cleanup_db()
        
    def cleanup_db(self):
        if os.path.exists(self.test_db):
            for _ in range(3):
                try:
                    os.remove(self.test_db)
                    break
                except PermissionError:
                    time.sleep(0.1)

    def test_heartbeat_caching_on_failure(self):
        # Mock session.post to raise an error
        self.client.session.post = MagicMock(side_effect=requests.exceptions.ConnectionError("Connection failed"))
        
        # Send heartbeat
        result = self.client.send_heartbeat("app", "title")
        
        # Verify it failed but was cached
        self.assertEqual(result['status'], 'cached')
        
        # Verify item in cache
        items = self.client.cache.get_pending_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][1], 'heartbeat')
        self.assertEqual(items[0][2]['app_name'], 'app')

    def test_screenshot_caching_on_failure(self):
        # Mock session.post to raise 500 error
        mock_response = MagicMock()
        mock_response.status_code = 500
        error = requests.exceptions.HTTPError("Server Error", response=mock_response)
        self.client.session.post = MagicMock(side_effect=error)
        
        # Upload screenshot
        try:
            self.client.upload_screenshot(b"image_data", {})
        except requests.exceptions.HTTPError:
            pass # Expected
            
        # Verify item in cache
        items = self.client.cache.get_pending_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0][1], 'screenshot')
        self.assertEqual(items[0][3], b"image_data")

    def test_retry_pending_uploads(self):
        # 1. Add item to cache manually
        self.client.cache.add_item('heartbeat', {'app_name': 'cached_app'})
        
        # 2. Mock session.post to succeed
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}
        self.client.session.post = MagicMock(return_value=mock_response)
        
        # 3. Trigger process_pending_uploads (via send_heartbeat)
        self.client.send_heartbeat("new_app", "title")
        
        # 4. Verify cache is empty
        items = self.client.cache.get_pending_items()
        self.assertEqual(len(items), 0)
        
        # 5. Verify post was called twice (once for new heartbeat, once for cached)
        self.assertEqual(self.client.session.post.call_count, 2)

if __name__ == '__main__':
    unittest.main()
