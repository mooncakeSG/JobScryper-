"""
Auto Applyer - Utils Package

This package provides comprehensive utilities for error handling, logging,
validation, and retry mechanisms.
"""

# Initialize logging first
from .logging_config import initialize_logging, get_logger, get_performance_logger

# Initialize logging with default settings
try:
    initialize_logging()
except Exception as e:
    import logging
    logging.warning(f"Failed to initialize advanced logging: {e}")

# Import error handling utilities
from .errors import (
    AutoApplyerError, APIError, APIKeyError, RateLimitError,
    NetworkError, ValidationError, ParseError, FileProcessingError, ConfigurationError,
    handle_errors, display_error_to_user, log_error, error_tracker
)

# Import validation utilities
from .validation import (
    InputValidator, RateLimitValidator,
    validate_job_search, validate_file, sanitize_input, validate_text_input,
    validate_inputs, rate_limit_validator
)

# Import retry utilities
from .retry import (
    RetryConfig, RetryStrategy, CircuitBreaker, RetryHandler,
    APIRetryConfigs, retry_on_failure, async_retry_on_failure,
    execute_with_retry, execute_with_async_retry, get_retry_handler
)

# Version information
__version__ = "1.0.0"
__author__ = "Auto Applyer Team"

# Package-level exports
__all__ = [
    # Logging
    'initialize_logging', 'get_logger', 'get_performance_logger',
    
    # Error handling
    'AutoApplyerError', 'APIError', 'APIKeyError', 'RateLimitError',
    'NetworkError', 'ValidationError', 'ParseError', 'FileProcessingError', 'ConfigurationError',
    'handle_errors', 'display_error_to_user', 'log_error', 'error_tracker',
    
    # Validation
    'InputValidator', 'RateLimitValidator',
    'validate_job_search', 'validate_file', 'sanitize_input', 'validate_text_input',
    'validate_inputs', 'rate_limit_validator',
    
    # Retry mechanisms
    'RetryConfig', 'RetryStrategy', 'CircuitBreaker', 'RetryHandler',
    'APIRetryConfigs', 'retry_on_failure', 'async_retry_on_failure',
    'execute_with_retry', 'execute_with_async_retry', 'get_retry_handler'
] 