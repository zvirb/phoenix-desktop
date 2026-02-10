import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import logging

# Add phoenix/core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "phoenix" / "core"))

from inference_detector import InferenceDetector

class TestInferenceDetectorSecurity(unittest.TestCase):

    def test_init_secure_host(self):
        """Test initialization with secure localhost URL."""
        # Standard localhost
        detector = InferenceDetector("http://localhost:11434")
        self.assertEqual(detector.ollama_host, "http://localhost:11434")

        # IP loopback
        detector = InferenceDetector("http://127.0.0.1:11434")
        self.assertEqual(detector.ollama_host, "http://127.0.0.1:11434")

        # HTTPS localhost
        detector = InferenceDetector("https://localhost:11434")
        self.assertEqual(detector.ollama_host, "https://localhost:11434")

    def test_init_insecure_host_external_domain(self):
        """Test initialization with external domain (SSRF attempt)."""
        detector = InferenceDetector("http://evil.com:80")
        # Should reset to default
        self.assertEqual(detector.ollama_host, "http://localhost:11450")

    def test_init_insecure_host_ip(self):
        """Test initialization with external IP (SSRF attempt)."""
        detector = InferenceDetector("http://192.168.1.1:8080")
        # Should reset to default
        self.assertEqual(detector.ollama_host, "http://localhost:11450")

    def test_init_insecure_scheme(self):
        """Test initialization with insecure scheme."""
        detector = InferenceDetector("ftp://localhost:21")
        # Should reset to default
        self.assertEqual(detector.ollama_host, "http://localhost:11450")

    @patch('inference_detector.subprocess.run')
    def test_tailscale_ip_masking(self, mock_run):
        """Test that Tailscale IP is masked in logs."""
        # Setup mock to return a valid Tailscale IP
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "100.101.102.103\n"
        mock_run.return_value = mock_result

        # Capture logs
        with self.assertLogs('inference_detector', level='DEBUG') as cm:
            detector = InferenceDetector()
            # Ensure cache doesn't hit
            detector.clear_cache()

            ip = detector.get_tailscale_ip()

            # Verify the IP returned is correct
            self.assertEqual(ip, "100.101.102.103")

            # Verify the log message contains masked IP
            found_masked = False
            for log in cm.output:
                if "Tailscale IP from CLI: 100.***.***.103" in log:
                    found_masked = True
                    break

            self.assertTrue(found_masked, f"Log message did not contain masked IP. Logs: {cm.output}")

if __name__ == '__main__':
    unittest.main()
