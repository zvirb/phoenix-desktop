"""
Comprehensive logging system for Phoenix Desktop Tracker.
Provides detailed error logging with unique log files per session.
"""
import logging
import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional
import functools


class PhoenixLogger:
    """Enhanced logging system with session tracking and detailed error capture."""
    
    def __init__(self, name: str = "phoenix_tracker"):
        """
        Initialize the Phoenix logging system.
        
        Args:
            name: Base name for the logger
        """
        self.name = name
        self.log_dir = Path(__file__).parent / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Create unique log file name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_id = timestamp
        self.log_file = self.log_dir / f"phoenix_tracker_{timestamp}.log"
        
        # Keep a reference to the latest log
        latest_link = self.log_dir / "latest.log"
        if latest_link.exists():
            latest_link.unlink()
        
        # Create symlink or copy for latest log (Windows compatibility)
        try:
            latest_link.write_text(str(self.log_file))
        except Exception:
            pass
        
        self.logger = self._setup_logger()
        
        # Log session start
        self.logger.info("=" * 80)
        self.logger.info(f"Phoenix Tracker Session Started - ID: {self.session_id}")
        self.logger.info(f"Log file: {self.log_file}")
        self.logger.info(f"Python version: {sys.version}")
        self.logger.info(f"Platform: {sys.platform}")
        self.logger.info("=" * 80)
    
    def _setup_logger(self) -> logging.Logger:
        """Set up the logger with multiple handlers and formatting."""
        logger = logging.getLogger(self.name)
        logger.setLevel(logging.DEBUG)  # Capture everything
        
        # Remove existing handlers
        logger.handlers.clear()
        
        # Detailed formatter
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Simple formatter for console
        console_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler - detailed logging
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        
        # Console handler - less verbose
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # Error file handler - only errors and critical
        error_log = self.log_dir / f"errors_{self.session_id}.log"
        error_handler = logging.FileHandler(error_log, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_handler)
        
        return logger
    
    def get_logger(self, module_name: Optional[str] = None) -> logging.Logger:
        """
        Get a logger instance for a specific module.
        
        Args:
            module_name: Name of the module requesting the logger
        
        Returns:
            Logger instance
        """
        if module_name:
            return logging.getLogger(f"{self.name}.{module_name}")
        return self.logger
    
    def log_exception(self, exc: Exception, context: str = "", **kwargs):
        """
        Log an exception with full context and traceback.
        
        Args:
            exc: The exception to log
            context: Additional context about where/why the error occurred
            **kwargs: Additional key-value pairs to log
        """
        self.logger.error(f"EXCEPTION CAUGHT: {context}")
        self.logger.error(f"Exception type: {type(exc).__name__}")
        self.logger.error(f"Exception message: {str(exc)}")
        
        # Log additional context
        for key, value in kwargs.items():
            self.logger.error(f"{key}: {value}")
        
        # Log full traceback
        self.logger.error("Full traceback:")
        self.logger.error(traceback.format_exc())
    
    def log_function_call(self, func_name: str, **kwargs):
        """Log a function call with parameters."""
        params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
        self.logger.debug(f"CALL: {func_name}({params})")
    
    def log_function_return(self, func_name: str, return_value):
        """Log a function return value."""
        self.logger.debug(f"RETURN: {func_name} -> {return_value}")
    
    def log_state_change(self, component: str, old_state, new_state):
        """Log a state change in the application."""
        self.logger.info(f"STATE CHANGE [{component}]: {old_state} -> {new_state}")
    
    def cleanup_old_logs(self, keep_days: int = 30):
        """
        Clean up log files older than specified days.
        
        Args:
            keep_days: Number of days to keep logs
        """
        try:
            cutoff = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob("*.log"):
                if log_file.name == "latest.log":
                    continue
                
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    self.logger.info(f"Cleaned up old log: {log_file.name}")
        
        except Exception as e:
            self.logger.error(f"Failed to cleanup old logs: {e}")


# Global logger instance
_phoenix_logger = None


def get_logger(module_name: Optional[str] = None) -> logging.Logger:
    """
    Get the global logger instance.
    
    Args:
        module_name: Name of the module requesting the logger
    
    Returns:
        Logger instance
    """
    global _phoenix_logger
    
    if _phoenix_logger is None:
        _phoenix_logger = PhoenixLogger()
    
    return _phoenix_logger.get_logger(module_name)


def log_exception(exc: Exception, context: str = "", **kwargs):
    """
    Log an exception to the global logger.
    
    Args:
        exc: The exception to log
        context: Additional context
        **kwargs: Additional context key-value pairs
    """
    global _phoenix_logger
    
    if _phoenix_logger is None:
        _phoenix_logger = PhoenixLogger()
    
    _phoenix_logger.log_exception(exc, context, **kwargs)


def logged_method(func):
    """
    Decorator to automatically log method calls, returns, and exceptions.
    
    Usage:
        @logged_method
        def my_function(arg1, arg2):
            ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        
        # Log function call
        func_name = f"{func.__qualname__}"
        
        # Build parameter string (avoid logging sensitive data)
        safe_kwargs = {k: v for k, v in kwargs.items() if 'token' not in k.lower() and 'password' not in k.lower()}
        params_str = ", ".join(f"{k}={v}" for k, v in safe_kwargs.items())
        
        logger.debug(f"→ CALL: {func_name}({params_str})")
        
        try:
            result = func(*args, **kwargs)
            
            # Log return (truncate long results)
            result_str = str(result)
            if len(result_str) > 100:
                result_str = result_str[:100] + "..."
            
            logger.debug(f"← RETURN: {func_name} -> {result_str}")
            return result
        
        except Exception as e:
            logger.error(f"✗ EXCEPTION in {func_name}")
            logger.error(f"  Type: {type(e).__name__}")
            logger.error(f"  Message: {str(e)}")
            logger.error(f"  Traceback:\n{traceback.format_exc()}")
            raise
    
    return wrapper


def setup_error_logging():
    """
    Setup global exception handling to catch all unhandled exceptions.
    """
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Allow KeyboardInterrupt to pass through
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger = get_logger("UNCAUGHT")
        logger.critical("=" * 80)
        logger.critical("UNCAUGHT EXCEPTION - APPLICATION CRASH")
        logger.critical("=" * 80)
        logger.critical(f"Type: {exc_type.__name__}")
        logger.critical(f"Value: {exc_value}")
        logger.critical("Traceback:")
        logger.critical("".join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        logger.critical("=" * 80)
    
    sys.excepthook = handle_exception


# Initialize error logging on import
setup_error_logging()


# Convenience function for getting session info
def get_session_info() -> dict:
    """Get current logging session information."""
    global _phoenix_logger
    
    if _phoenix_logger is None:
        _phoenix_logger = PhoenixLogger()
    
    return {
        'session_id': _phoenix_logger.session_id,
        'log_file': str(_phoenix_logger.log_file),
        'log_dir': str(_phoenix_logger.log_dir)
    }
