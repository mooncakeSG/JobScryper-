"""
Auto Applyer - Logging Configuration Module

This module provides comprehensive logging setup including:
- Multiple log levels and handlers
- File rotation and management
- Structured logging with context
- Performance and error tracking
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging"""
    
    def format(self, record):
        """Format log record as structured JSON"""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra context if present
        if hasattr(record, 'context'):
            log_entry["context"] = record.context
        
        # Add user ID if present (for future user tracking)
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        # Add request ID if present (for future request tracking)
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredConsoleFormatter(logging.Formatter):
    """Colored console formatter for better readability"""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m'   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        """Format record with colors"""
        color = self.COLORS.get(record.levelname, self.RESET)
        
        # Format: [TIMESTAMP] LEVEL MODULE.FUNCTION:LINE - MESSAGE
        formatted_time = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        log_format = (
            f"{color}[{formatted_time}] {record.levelname:<8} "
            f"{record.module}.{record.funcName}:{record.lineno} - "
            f"{record.getMessage()}{self.RESET}"
        )
        
        return log_format


class ContextLogger:
    """Logger wrapper that adds context to log messages"""
    
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.context = {}
    
    def add_context(self, **kwargs):
        """Add context that will be included in all log messages"""
        self.context.update(kwargs)
        return self
    
    def clear_context(self):
        """Clear all context"""
        self.context.clear()
    
    def _log_with_context(self, level, message, *args, **kwargs):
        """Log message with added context"""
        extra = kwargs.get('extra', {})
        extra['context'] = {**self.context, **extra.get('context', {})}
        kwargs['extra'] = extra
        
        getattr(self.logger, level)(message, *args, **kwargs)
    
    def debug(self, message, *args, **kwargs):
        self._log_with_context('debug', message, *args, **kwargs)
    
    def info(self, message, *args, **kwargs):
        self._log_with_context('info', message, *args, **kwargs)
    
    def warning(self, message, *args, **kwargs):
        self._log_with_context('warning', message, *args, **kwargs)
    
    def error(self, message, *args, **kwargs):
        self._log_with_context('error', message, *args, **kwargs)
    
    def critical(self, message, *args, **kwargs):
        self._log_with_context('critical', message, *args, **kwargs)


class LoggingConfig:
    """Centralized logging configuration"""
    
    def __init__(
        self,
        log_level: str = "INFO",
        log_dir: str = "logs",
        max_file_size: int = 10 * 1024 * 1024,  # 10MB
        backup_count: int = 5,
        enable_console: bool = True,
        enable_file: bool = True,
        enable_structured: bool = True,
        enable_colors: bool = True
    ):
        self.log_level = getattr(logging, log_level.upper())
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_file = enable_file
        self.enable_structured = enable_structured
        self.enable_colors = enable_colors
        
        # Create logs directory
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging configuration"""
        # Clear any existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        
        # Set root logger level
        root_logger.setLevel(self.log_level)
        
        # Console handler
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            
            if self.enable_colors and sys.stdout.isatty():
                console_formatter = ColoredConsoleFormatter()
            else:
                console_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
                )
            
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # File handlers
        if self.enable_file:
            # Main application log
            app_log_file = self.log_dir / "auto_applyer.log"
            app_handler = logging.handlers.RotatingFileHandler(
                app_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            app_handler.setLevel(self.log_level)
            
            if self.enable_structured:
                app_formatter = StructuredFormatter()
            else:
                app_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
                )
            
            app_handler.setFormatter(app_formatter)
            root_logger.addHandler(app_handler)
            
            # Error-only log
            error_log_file = self.log_dir / "errors.log"
            error_handler = logging.handlers.RotatingFileHandler(
                error_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(StructuredFormatter())
            root_logger.addHandler(error_handler)
            
            # Performance log (for future use)
            performance_log_file = self.log_dir / "performance.log"
            performance_handler = logging.handlers.RotatingFileHandler(
                performance_log_file,
                maxBytes=self.max_file_size,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            performance_handler.setLevel(logging.INFO)
            performance_handler.setFormatter(StructuredFormatter())
            
            # Create performance logger
            performance_logger = logging.getLogger('performance')
            performance_logger.addHandler(performance_handler)
            performance_logger.setLevel(logging.INFO)
            performance_logger.propagate = False
    
    def get_logger(self, name: str) -> ContextLogger:
        """Get a context-aware logger for a module"""
        logger = logging.getLogger(name)
        return ContextLogger(logger)
    
    def get_performance_logger(self) -> ContextLogger:
        """Get the performance logger"""
        logger = logging.getLogger('performance')
        return ContextLogger(logger)


class PerformanceLogger:
    """Logger for tracking performance metrics"""
    
    def __init__(self):
        self.logger = logging.getLogger('performance')
    
    def log_operation(
        self,
        operation: str,
        duration: float,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log operation performance"""
        performance_data = {
            "operation": operation,
            "duration_seconds": duration,
            "success": success,
            "metadata": metadata or {}
        }
        
        self.logger.info(
            f"Operation: {operation} | Duration: {duration:.3f}s | Success: {success}",
            extra={"context": performance_data}
        )
    
    def log_api_call(
        self,
        api_name: str,
        endpoint: str,
        response_time: float,
        status_code: int,
        request_size: Optional[int] = None,
        response_size: Optional[int] = None
    ):
        """Log API call performance"""
        api_data = {
            "api_name": api_name,
            "endpoint": endpoint,
            "response_time_seconds": response_time,
            "status_code": status_code,
            "request_size_bytes": request_size,
            "response_size_bytes": response_size
        }
        
        self.logger.info(
            f"API Call: {api_name} | Endpoint: {endpoint} | "
            f"Response Time: {response_time:.3f}s | Status: {status_code}",
            extra={"context": api_data}
        )


# ============================================================================
# Utility Functions
# ============================================================================

def setup_logging(
    log_level: str = None,
    log_dir: str = None,
    **kwargs
) -> LoggingConfig:
    """
    Set up application logging with environment variable support
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        **kwargs: Additional configuration options
    
    Returns:
        LoggingConfig instance
    """
    # Get configuration from environment variables
    log_level = log_level or os.getenv('LOG_LEVEL', 'INFO')
    log_dir = log_dir or os.getenv('LOG_DIR', 'logs')
    
    # Additional environment-based configuration
    config_kwargs = {
        'log_level': log_level,
        'log_dir': log_dir,
        'enable_console': os.getenv('LOG_CONSOLE', 'true').lower() == 'true',
        'enable_file': os.getenv('LOG_FILE', 'true').lower() == 'true',
        'enable_structured': os.getenv('LOG_STRUCTURED', 'true').lower() == 'true',
        'enable_colors': os.getenv('LOG_COLORS', 'true').lower() == 'true',
        **kwargs
    }
    
    return LoggingConfig(**config_kwargs)


def get_logger(name: str) -> ContextLogger:
    """Get a context-aware logger (convenience function)"""
    logger = logging.getLogger(name)
    return ContextLogger(logger)


def log_function_call(func_name: str, args: tuple = (), kwargs: dict = None):
    """Decorator to log function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            logger.add_context(function=func_name)
            
            try:
                logger.debug(f"Calling {func_name} with args={args}, kwargs={kwargs}")
                result = func(*args, **kwargs)
                logger.debug(f"{func_name} completed successfully")
                return result
            except Exception as e:
                logger.error(f"{func_name} failed with error: {str(e)}")
                raise
            finally:
                logger.clear_context()
        
        return wrapper
    return decorator


# ============================================================================
# Module Initialization
# ============================================================================

# Global logging config instance
_logging_config = None
_performance_logger = None


def initialize_logging(**kwargs):
    """Initialize global logging configuration"""
    global _logging_config, _performance_logger
    
    _logging_config = setup_logging(**kwargs)
    _performance_logger = PerformanceLogger()
    
    # Log initialization
    logger = get_logger(__name__)
    logger.info("Logging system initialized", extra={
        "context": {
            "log_level": _logging_config.log_level,
            "log_dir": str(_logging_config.log_dir),
            "handlers": len(logging.getLogger().handlers)
        }
    })


def get_performance_logger() -> PerformanceLogger:
    """Get the global performance logger"""
    global _performance_logger
    if _performance_logger is None:
        _performance_logger = PerformanceLogger()
    return _performance_logger


# Auto-initialize with default settings if not already initialized
if _logging_config is None:
    try:
        initialize_logging()
    except Exception as e:
        # Fallback to basic logging if initialization fails
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logging.error(f"Failed to initialize advanced logging: {e}")


# Export main classes and functions
__all__ = [
    'LoggingConfig', 'ContextLogger', 'PerformanceLogger',
    'setup_logging', 'get_logger', 'get_performance_logger',
    'initialize_logging', 'log_function_call'
] 