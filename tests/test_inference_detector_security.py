import sys
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import logging
import socket

# Add phoenix/core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "phoenix" / "core"))

from inference_detector import InferenceDetector

class TestInferenceDetectorSecurity(unittest.TestCase):

    def test_public_ip_detection(self):
        """Test that public IPs are not detected as Tailscale IPs."""
        detector = InferenceDetector()

        # Mock psutil to return a public IP starting with 100.
        with patch('psutil.net_if_addrs') as mock_net_if_addrs:
            # Mock address structure
            addr = MagicMock()
            addr.family = socket.AF_INET
            addr.address = '100.1.2.3' # Public IP (Verizon)

            mock_net_if_addrs.return_value = {
                'Ethernet': [addr]
            }

            # This should return None now
            result = detector._detect_tailscale_ip()
            self.assertIsNone(result, "Should not detect public IP 100.1.2.3 as Tailscale IP")

    def test_cgnat_ip_detection(self):
        """Test that valid CGNAT IPs are detected."""
        detector = InferenceDetector()

        with patch('psutil.net_if_addrs') as mock_net_if_addrs:
            addr = MagicMock()
            addr.family = socket.AF_INET
            addr.address = '100.64.0.1' # Valid CGNAT/Tailscale IP

            mock_net_if_addrs.return_value = {
                'Tailscale': [addr]
            }

            result = detector._detect_tailscale_ip()
            self.assertEqual(result, '100.64.0.1')

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

    @patch('inference_detector.subprocess.run')
    @patch('shutil.which')
    @patch('os.path.exists')
    def test_tailscale_cwd_vulnerability(self, mock_exists, mock_which, mock_run):
        """Test that tailscale in CWD is ignored."""
        import os

        # Simulate trusted paths not existing (so it falls back to shutil.which)
        mock_exists.return_value = False

        # Setup mock to return a path in CWD
        cwd = os.getcwd()
        malicious_path = os.path.join(cwd, 'tailscale.exe')
        mock_which.return_value = malicious_path

        # Run test
        detector = InferenceDetector()
        detector.clear_cache()

        # We expect a warning log about ignoring CWD
        with self.assertLogs('inference_detector', level='WARNING') as cm:
            ip = detector.get_tailscale_ip()

            # Verify subprocess.run was NOT called
            mock_run.assert_not_called()

            # Verify return value is None (since trusted paths failed too)
            self.assertIsNone(ip)

            # Verify warning message
            found = any("Ignored tailscale executable in CWD" in log for log in cm.output)
            self.assertTrue(found, f"Warning not found in logs: {cm.output}")

if __name__ == '__main__':
    unittest.main()
