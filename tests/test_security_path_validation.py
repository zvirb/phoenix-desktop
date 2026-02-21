import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from phoenix.core.inference_detector import InferenceDetector

class TestInferenceDetectorSecurity(unittest.TestCase):
    def setUp(self):
        self.detector = InferenceDetector()

    @patch('os.name', 'nt')
    @patch('os.environ.get')
    @patch('os.path.abspath')
    @patch('os.getcwd')
    @patch('os.path.normcase')
    def test_is_safe_path_windows_bypass(self, mock_normcase, mock_getcwd, mock_abspath, mock_env_get):
        # Mock Windows environment variables
        def get_env(key, default=None):
            if key == 'SystemRoot': return r'C:\Windows'
            if key == 'ProgramFiles': return r'C:\Program Files'
            if key == 'ProgramFiles(x86)': return r'C:\Program Files (x86)'
            return default
        mock_env_get.side_effect = get_env

        # Mock os.path functions to simulate Windows behavior
        # normcase on Windows lowercases the path
        mock_normcase.side_effect = lambda p: p.lower().replace('/', '\\')

        # mock abspath to just return the path (assuming input is absolute for test)
        mock_abspath.side_effect = lambda p: p.replace('/', '\\')

        # mock getcwd to a safe location
        mock_getcwd.return_value = r'C:\Users\User\Phoenix'

        # Trusted path
        safe_path = r'C:\Program Files\Tailscale\tailscale.exe'

        # Bypass attempt: Folder name starting with trusted root prefix
        bypass_path = r'C:\Program Files Malicious\tailscale.exe'

        # We need to mock os.path.commonpath because it relies on OS-specific separator logic
        # And we are running on Linux (likely) but testing Windows logic
        with patch('os.path.commonpath') as mock_commonpath:
            def commonpath_side_effect(paths):
                # Simple implementation for Windows paths
                # Split by backslash
                p1_parts = paths[0].replace('/', '\\').split('\\')
                p2_parts = paths[1].replace('/', '\\').split('\\')

                common = []
                for i in range(min(len(p1_parts), len(p2_parts))):
                    if p1_parts[i].lower() == p2_parts[i].lower():
                        common.append(p1_parts[i])
                    else:
                        break

                # Join back
                result = '\\'.join(common)
                # Handle root drive case (e.g. C: -> C:\ if needed, but split gives C: and parts)
                # For C:\Windows, split is ['C:', 'Windows']. Join is C:\Windows.
                return result

            mock_commonpath.side_effect = commonpath_side_effect

            # Test Safe Path
            self.assertTrue(self.detector._is_safe_path(safe_path), "Safe path should be accepted")

            # Test Bypass Path
            # This should now return False (Rejected)
            self.assertFalse(self.detector._is_safe_path(bypass_path), "Bypass path should be rejected")

if __name__ == '__main__':
    unittest.main()
