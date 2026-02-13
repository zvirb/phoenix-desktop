import unittest
from unittest.mock import MagicMock, patch
import requests
import importlib

# Import module to reload
import phoenix.core.api_client

class TestSecurityLogLeak(unittest.TestCase):
    def setUp(self):
        # Reload to ensure fresh state and imports
        importlib.reload(phoenix.core.api_client)
        from phoenix.core.api_client import APIClient
        self.APIClient = APIClient

        self.logger_patcher = patch('phoenix.core.api_client.logger')
        self.mock_logger = self.logger_patcher.start()

    def tearDown(self):
        self.logger_patcher.stop()

    def test_sensitive_data_redacted_in_logs(self):
        client = self.APIClient("https://example.com", "device123")

        # Mock session.request to raise HTTPError with sensitive body
        mock_response = MagicMock()
        mock_response.status_code = 400
        sensitive_json = '{"error": "Invalid token", "token": "sensitive_secret_123"}'
        mock_response.text = sensitive_json

        error = requests.exceptions.HTTPError("Bad Request", response=mock_response)
        client.session.request = MagicMock(side_effect=error)

        # Make a request
        client._make_request('GET', '/api/test')

        # Verify logger.error was called
        found_sensitive = False
        found_redacted = False

        for call in self.mock_logger.error.call_args_list:
            args, _ = call
            message = args[0]
            if "sensitive_secret_123" in message:
                found_sensitive = True
            if "***REDACTED***" in message:
                found_redacted = True

        # Vulnerability check: sensitive data should NOT be present
        self.assertFalse(found_sensitive, "Security Fix Failed: Sensitive data still leaked in logs")

        # Verification check: redacted placeholder SHOULD be present
        self.assertTrue(found_redacted, "Security Fix Failed: Data was not properly redacted")

if __name__ == '__main__':
    unittest.main()
