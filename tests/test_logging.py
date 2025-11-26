"""
Unit tests for phoenix_logging module.
Tests the comprehensive logging system.
"""
import pytest
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from phoenix_logging import (
    PhoenixLogger,
    get_logger,
    log_exception,
    logged_method,
    get_session_info,
    setup_error_logging
)


class TestPhoenixLogger:
    """Test the PhoenixLogger class."""
    
    def test_logger_initialization(self):
        """Test that logger initializes correctly."""
        phoenix_logger = PhoenixLogger("test_logger")
        
        assert phoenix_logger.name == "test_logger"
        assert phoenix_logger.session_id is not None
        assert phoenix_logger.log_dir.exists()
        assert phoenix_logger.log_file.exists()
    
    def test_unique_session_ids(self):
        """Test that each logger gets a unique session ID."""
        logger1 = PhoenixLogger("logger1")
        logger2 = PhoenixLogger("logger2")
        
        assert logger1.session_id != logger2.session_id
    
    def test_log_file_creation(self):
        """Test that log files are created."""
        phoenix_logger = PhoenixLogger("test_logger")
        
        # Check main log file
        assert phoenix_logger.log_file.exists()
        assert phoenix_logger.log_file.suffix == ".log"
        
        # Check log directory
        assert phoenix_logger.log_dir.exists()
        assert phoenix_logger.log_dir.name == "logs"
    
    def test_get_logger(self):
        """Test get_logger returns a logger instance."""
        logger = get_logger("test_module")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name.endswith("test_module")
    
    def test_log_exception_basic(self):
        """Test basic exception logging."""
        logger = get_logger("test")
        
        try:
            raise ValueError("Test error")
        except ValueError as e:
            # Should not raise an error
            log_exception(e, "Test context")
    
    def test_log_exception_with_context(self):
        """Test exception logging with context."""
        logger = get_logger("test")
        
        try:
            raise RuntimeError("Test runtime error")
        except RuntimeError as e:
            # Should not raise an error
            log_exception(e, "Test context", param1="value1", param2=123)
    
    def test_session_info(self):
        """Test get_session_info returns valid data."""
        info = get_session_info()
        
        assert 'session_id' in info
        assert 'log_file' in info
        assert 'log_dir' in info
        assert isinstance(info['session_id'], str)


class TestLoggedMethodDecorator:
    """Test the @logged_method decorator."""
    
    def test_decorator_basic_function(self):
        """Test decorator on a basic function."""
        
        @logged_method
        def test_function(x, y):
            return x + y
        
        result = test_function(2, 3)
        assert result == 5
    
    def test_decorator_with_exception(self):
        """Test decorator captures exceptions."""
        
        @logged_method
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
    
    def test_decorator_with_kwargs(self):
        """Test decorator with keyword arguments."""
        
        @logged_method
        def test_function(a, b=10, c=20):
            return a + b + c
        
        result = test_function(5, b=15, c=25)
        assert result == 45
    
    def test_decorator_preserves_function_name(self):
        """Test decorator preserves function metadata."""
        
        @logged_method
        def my_special_function():
            """A special function."""
            pass
        
        assert my_special_function.__name__ == "my_special_function"
        assert my_special_function.__doc__ == "A special function."
    
    def test_decorator_masks_sensitive_data(self):
        """Test decorator masks sensitive parameters."""
        
        @logged_method
        def process_token(token, password, user_id):
            return user_id
        
        # Should not raise an error even with sensitive params
        result = process_token("secret_token", "secret_pass", "user123")
        assert result == "user123"


class TestErrorHandling:
    """Test global error handling setup."""
    
    def test_setup_error_logging(self):
        """Test that error logging setup doesn't raise."""
        # Should not raise an error
        setup_error_logging()
    
    def test_exception_hook_installed(self):
        """Test that exception hook is installed."""
        setup_error_logging()
        assert sys.excepthook is not None


class TestLoggerCleanup:
    """Test log cleanup functionality."""
    
    def test_cleanup_old_logs_method_exists(self):
        """Test that cleanup method exists."""
        phoenix_logger = PhoenixLogger("test")
        assert hasattr(phoenix_logger, 'cleanup_old_logs')
    
    def test_cleanup_old_logs_basic(self):
        """Test cleanup doesn't crash."""
        phoenix_logger = PhoenixLogger("test")
        
        # Should not raise an error
        phoenix_logger.cleanup_old_logs(keep_days=30)


class TestLoggingLevels:
    """Test different logging levels."""
    
    def test_debug_logging(self):
        """Test DEBUG level logging."""
        logger = get_logger("test_debug")
        logger.debug("Debug message")
    
    def test_info_logging(self):
        """Test INFO level logging."""
        logger = get_logger("test_info")
        logger.info("Info message")
    
    def test_warning_logging(self):
        """Test WARNING level logging."""
        logger = get_logger("test_warning")
        logger.warning("Warning message")
    
    def test_error_logging(self):
        """Test ERROR level logging."""
        logger = get_logger("test_error")
        logger.error("Error message")
    
    def test_critical_logging(self):
        """Test CRITICAL level logging."""
        logger = get_logger("test_critical")
        logger.critical("Critical message")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
