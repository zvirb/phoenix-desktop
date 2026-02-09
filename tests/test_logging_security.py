"""
Security tests for logging redaction.
"""
import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phoenix_logging import sanitize_data, SENSITIVE_KEYS

def test_sanitize_data_new_keys():
    """Test that new sensitive keys are redacted."""
    sensitive_data = {
        "cookie": "session=secret_session_id",
        "Set-Cookie": "auth=secret_auth",
        "session": "secret_session_data",
        "bearer": "Bearer secret_token",
        "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "safe_field": "safe_value"
    }

    sanitized = sanitize_data(sensitive_data)

    assert sanitized["cookie"] == "***REDACTED***"
    assert sanitized["Set-Cookie"] == "***REDACTED***"
    assert sanitized["session"] == "***REDACTED***"
    assert sanitized["bearer"] == "***REDACTED***"
    assert sanitized["jwt"] == "***REDACTED***"
    assert sanitized["safe_field"] == "safe_value"

def test_sanitize_data_nested():
    """Test recursive redaction."""
    data = {
        "user": {
            "profile": {
                "session_id": "secret_id"
            }
        }
    }
    # "session_id" contains "session", so it should be redacted
    sanitized = sanitize_data(data)
    assert sanitized["user"]["profile"]["session_id"] == "***REDACTED***"

def test_sensitive_keys_presence():
    """Ensure the new keys are in the SENSITIVE_KEYS set."""
    required_keys = {'cookie', 'session', 'bearer', 'jwt'}
    assert required_keys.issubset(SENSITIVE_KEYS)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
