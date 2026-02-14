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
    @patch('shutil.which')
    def test_tailscale_ip_masking(self, mock_which, mock_run):
        """Test that Tailscale IP is masked in logs."""
        # Mock shutil.which so logic proceeds
        mock_which.return_value = "/usr/bin/tailscale"

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

    @patch('inference_detector.subprocess.run')
    @patch('shutil.which')
    def test_tailscale_uses_absolute_path(self, mock_which, mock_run):
        """Test that subprocess.run is called with an absolute path for tailscale."""

        # Mock shutil.which to return a specific absolute path
        expected_path = "/usr/bin/tailscale"
        mock_which.return_value = expected_path

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "100.1.2.3"
        mock_run.return_value = mock_result

        detector = InferenceDetector()
        detector.clear_cache() # Ensure cache is cleared
        detector.get_tailscale_ip()

        # Verify shutil.which was called
        mock_which.assert_called_with('tailscale')

        # Verify subprocess.run was called with the absolute path
        args, _ = mock_run.call_args
        command = args[0]
        self.assertEqual(command[0], expected_path)

    @patch('inference_detector.subprocess.run')
    @patch('shutil.which')
    def test_tailscale_not_found_via_which(self, mock_which, mock_run):
        """Test behavior when tailscale is not found via shutil.which."""
        mock_which.return_value = None

        detector = InferenceDetector()
        detector.clear_cache()
        detector.get_tailscale_ip()

        # Verify subprocess.run was NOT called
        mock_run.assert_not_called()

if __name__ == '__main__':
    unittest.main()
