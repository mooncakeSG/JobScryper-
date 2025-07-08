"""
Auto Applyer - Centralized Error Handling Module

This module provides comprehensive error handling utilities including:
- Custom exception classes
- Error response formatting
- User-friendly error messages
- Error tracking and reporting
"""

import logging
import traceback
from typing import Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum
import streamlit as st


class ErrorType(Enum):
    """Enumeration of error types for categorization"""
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    VALIDATION_ERROR = "validation_error"
    PARSING_ERROR = "parsing_error"
    AUTHENTICATION_ERROR = "authentication_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    FILE_ERROR = "file_error"
    CONFIGURATION_ERROR = "configuration_error"
    INTERNAL_ERROR = "internal_error"
    USER_ERROR = "user_error"


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# Custom Exception Classes
# ============================================================================

class AutoApplyerError(Exception):
    """Base exception for all Auto Applyer errors"""
    
    def __init__(self, message: str, error_type: ErrorType = ErrorType.INTERNAL_ERROR, 
                 details: Optional[Dict[str, Any]] = None, severity: ErrorSeverity = ErrorSeverity.MEDIUM):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        self.severity = severity
        self.timestamp = datetime.now().isoformat()
        super().__init__(self.message)


class APIError(AutoApplyerError):
    """Raised when external API calls fail"""
    
    def __init__(self, message: str, api_name: str = "Unknown", status_code: Optional[int] = None, 
                 response_data: Optional[str] = None):
        details = {
            "api_name": api_name,
            "status_code": status_code,
            "response_data": response_data
        }
        super().__init__(message, ErrorType.API_ERROR, details, ErrorSeverity.HIGH)


class APIKeyError(APIError):
    """Raised when API keys are missing or invalid"""
    
    def __init__(self, api_name: str):
        message = f"API key for {api_name} is missing or invalid"
        super().__init__(message, api_name)
        self.error_type = ErrorType.AUTHENTICATION_ERROR


class RateLimitError(APIError):
    """Raised when API rate limits are exceeded"""
    
    def __init__(self, api_name: str, retry_after: Optional[int] = None):
        message = f"Rate limit exceeded for {api_name}"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        details = {"retry_after": retry_after}
        super().__init__(message, api_name, details=details)
        self.error_type = ErrorType.RATE_LIMIT_ERROR


class NetworkError(AutoApplyerError):
    """Raised when network requests fail"""
    
    def __init__(self, message: str, url: Optional[str] = None, timeout: Optional[int] = None):
        details = {"url": url, "timeout": timeout}
        super().__init__(message, ErrorType.NETWORK_ERROR, details, ErrorSeverity.MEDIUM)


class ValidationError(AutoApplyerError):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        details = {"field": field, "value": str(value) if value is not None else None}
        super().__init__(message, ErrorType.VALIDATION_ERROR, details, ErrorSeverity.LOW)


class ParseError(AutoApplyerError):
    """Raised when document or data parsing fails"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, parser_type: Optional[str] = None):
        details = {"file_path": file_path, "parser_type": parser_type}
        super().__init__(message, ErrorType.PARSING_ERROR, details, ErrorSeverity.MEDIUM)


class FileError(AutoApplyerError):
    """Raised when file operations fail"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, operation: Optional[str] = None):
        details = {"file_path": file_path, "operation": operation}
        super().__init__(message, ErrorType.FILE_ERROR, details, ErrorSeverity.MEDIUM)


class ConfigurationError(AutoApplyerError):
    """Raised when configuration is invalid or missing"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        details = {"config_key": config_key}
        super().__init__(message, ErrorType.CONFIGURATION_ERROR, details, ErrorSeverity.HIGH)


class DatabaseError(AutoApplyerError):
    """Raised when database operations fail"""
    
    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None):
        details = {"operation": operation, "table": table}
        super().__init__(message, ErrorType.INTERNAL_ERROR, details, ErrorSeverity.HIGH)


class MigrationError(DatabaseError):
    """Raised when database migration operations fail"""
    
    def __init__(self, message: str, migration_version: Optional[str] = None):
        details = {"migration_version": migration_version}
        super().__init__(message, "migration", details=details)


# ============================================================================
# Error Response Utilities
# ============================================================================

class ErrorResponse:
    """Standardized error response format"""
    
    def __init__(self, error: Union[Exception, AutoApplyerError], context: Optional[Dict[str, Any]] = None):
        self.error = error
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format"""
        if isinstance(self.error, AutoApplyerError):
            return {
                "error": True,
                "message": self.error.message,
                "error_type": self.error.error_type.value,
                "severity": self.error.severity.value,
                "details": self.error.details,
                "timestamp": self.error.timestamp,
                "context": self.context
            }
        else:
            return {
                "error": True,
                "message": str(self.error),
                "error_type": ErrorType.INTERNAL_ERROR.value,
                "severity": ErrorSeverity.MEDIUM.value,
                "details": {"exception_type": type(self.error).__name__},
                "timestamp": self.timestamp,
                "context": self.context
            }
    
    def to_user_message(self) -> str:
        """Generate user-friendly error message"""
        if isinstance(self.error, AutoApplyerError):
            return self._get_user_friendly_message(self.error)
        else:
            return "An unexpected error occurred. Please try again."
    
    def _get_user_friendly_message(self, error: AutoApplyerError) -> str:
        """Generate user-friendly messages based on error type"""
        messages = {
            ErrorType.API_ERROR: "Service temporarily unavailable. Please try again in a few moments.",
            ErrorType.NETWORK_ERROR: "Network connection issue. Please check your internet connection.",
            ErrorType.VALIDATION_ERROR: f"Invalid input: {error.message}",
            ErrorType.PARSING_ERROR: "Unable to process the uploaded file. Please ensure it's a valid PDF or DOCX.",
            ErrorType.AUTHENTICATION_ERROR: "API configuration required. Please contact support.",
            ErrorType.RATE_LIMIT_ERROR: "Service is busy. Please wait a moment and try again.",
            ErrorType.FILE_ERROR: "File operation failed. Please check the file and try again.",
            ErrorType.CONFIGURATION_ERROR: "System configuration error. Please contact support.",
            ErrorType.USER_ERROR: error.message,
            ErrorType.INTERNAL_ERROR: "An internal error occurred. Please try again."
        }
        
        return messages.get(error.error_type, error.message)


# ============================================================================
# Error Handler Decorator and Context Manager
# ============================================================================

def handle_errors(
    operation_name: str = "Operation",
    show_user_error: bool = True,
    show_technical_details: bool = False,
    default_return_value: Any = None,
    log_errors: bool = True
):
    """
    Decorator for handling errors in functions with Streamlit UI feedback
    
    Args:
        operation_name: Name of the operation for user messages
        show_user_error: Whether to show error message to user
        show_technical_details: Whether to show technical error details in expander
        default_return_value: Value to return on error
        log_errors: Whether to log errors
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log error if requested
                if log_errors:
                    logger = logging.getLogger(func.__module__)
                    logger.error(f"Error in {operation_name}: {str(e)}", exc_info=True)
                
                # Create error response
                error_response = ErrorResponse(e, {
                    "operation": operation_name,
                    "function": func.__name__,
                    "module": func.__module__
                })
                
                # Show user error if requested
                if show_user_error:
                    display_error_to_user(error_response, show_technical_details)
                
                return default_return_value
        
        return wrapper
    return decorator


class ErrorContext:
    """Context manager for handling errors with automatic UI feedback"""
    
    def __init__(self, operation_name: str, show_spinner: bool = True, 
                 show_technical_details: bool = False):
        self.operation_name = operation_name
        self.show_spinner = show_spinner
        self.show_technical_details = show_technical_details
        self.error_occurred = False
        self.spinner = None
    
    def __enter__(self):
        if self.show_spinner:
            self.spinner = st.spinner(f"Processing {self.operation_name}...")
            self.spinner.__enter__()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.spinner:
            self.spinner.__exit__(exc_type, exc_val, exc_tb)
        
        if exc_type is not None:
            self.error_occurred = True
            error_response = ErrorResponse(exc_val, {"operation": self.operation_name})
            display_error_to_user(error_response, self.show_technical_details)
            return True  # Suppress exception
        
        return False


# ============================================================================
# Streamlit UI Error Display Functions
# ============================================================================

def display_error_to_user(error_response: ErrorResponse, show_technical_details: bool = False):
    """Display error message to user in Streamlit UI"""
    
    user_message = error_response.to_user_message()
    error_dict = error_response.to_dict()
    
    # Determine error level for Streamlit display
    severity = error_dict.get("severity", "medium")
    
    if severity == "critical":
        st.error(f"🚨 {user_message}")
    elif severity == "high":
        st.error(f"❌ {user_message}")
    elif severity == "medium":
        st.warning(f"⚠️ {user_message}")
    else:
        st.info(f"ℹ️ {user_message}")
    
    # Show technical details if requested
    if show_technical_details:
        with st.expander("🔧 Technical Details", expanded=False):
            st.json(error_dict)
    
    # Show helpful suggestions based on error type
    error_type = error_dict.get("error_type", "")
    suggestions = get_error_suggestions(error_type)
    if suggestions:
        with st.expander("💡 Suggested Solutions", expanded=False):
            for suggestion in suggestions:
                st.write(f"• {suggestion}")


def get_error_suggestions(error_type: str) -> list:
    """Get helpful suggestions based on error type"""
    suggestions = {
        "api_error": [
            "Check your internet connection",
            "Try again in a few moments",
            "Contact support if the issue persists"
        ],
        "network_error": [
            "Verify your internet connection",
            "Check if the service is accessible",
            "Try using a different network"
        ],
        "validation_error": [
            "Check your input format",
            "Ensure all required fields are filled",
            "Review the input requirements"
        ],
        "parsing_error": [
            "Ensure your file is not corrupted",
            "Try a different file format (PDF recommended)",
            "Check that the file is not password protected"
        ],
        "authentication_error": [
            "Check your API key configuration",
            "Verify API key permissions",
            "Contact administrator for API access"
        ],
        "rate_limit_error": [
            "Wait for the specified time before retrying",
            "Reduce the frequency of requests",
            "Consider upgrading your API plan"
        ],
        "file_error": [
            "Check file permissions",
            "Ensure the file exists and is accessible",
            "Try moving the file to a different location"
        ]
    }
    
    return suggestions.get(error_type, [
        "Try refreshing the page",
        "Contact support if the problem continues"
    ])


# ============================================================================
# Error Tracking and Reporting
# ============================================================================

class ErrorTracker:
    """Track and analyze application errors"""
    
    def __init__(self):
        self.errors = []
        self.error_counts = {}
    
    def track_error(self, error: AutoApplyerError, context: Optional[Dict[str, Any]] = None):
        """Track an error occurrence"""
        error_record = {
            "timestamp": error.timestamp,
            "error_type": error.error_type.value,
            "severity": error.severity.value,
            "message": error.message,
            "details": error.details,
            "context": context or {}
        }
        
        self.errors.append(error_record)
        
        # Update error counts
        error_key = f"{error.error_type.value}:{error.severity.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of tracked errors"""
        return {
            "total_errors": len(self.errors),
            "error_counts": self.error_counts,
            "recent_errors": self.errors[-10:] if self.errors else []
        }
    
    def clear_errors(self):
        """Clear tracked errors"""
        self.errors.clear()
        self.error_counts.clear()


# Global error tracker instance
error_tracker = ErrorTracker()


# ============================================================================
# Utility Functions
# ============================================================================

def log_error(error: Exception, context: Optional[Dict[str, Any]] = None, logger_name: str = __name__):
    """Log error with context information"""
    logger = logging.getLogger(logger_name)
    
    error_info = {
        "error_type": type(error).__name__,
        "message": str(error),
        "context": context or {}
    }
    
    logger.error(f"Error occurred: {error_info}", exc_info=True)
    
    # Track error if it's a custom error
    if isinstance(error, AutoApplyerError):
        error_tracker.track_error(error, context)


def create_error_response(message: str, error_type: ErrorType = ErrorType.INTERNAL_ERROR, 
                         details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Create standardized error response"""
    error = AutoApplyerError(message, error_type, details)
    return ErrorResponse(error).to_dict()


def safe_execute(func, *args, default_return=None, **kwargs):
    """Safely execute a function and return default value on error"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        log_error(e, {"function": func.__name__, "args": args, "kwargs": kwargs})
        return default_return


# ============================================================================
# Module Initialization
# ============================================================================

# Set up module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Export main classes and functions
__all__ = [
    # Exception classes
    'AutoApplyerError', 'APIError', 'APIKeyError', 'RateLimitError', 
    'NetworkError', 'ValidationError', 'ParseError', 'FileError', 'ConfigurationError',
    
    # Enums
    'ErrorType', 'ErrorSeverity',
    
    # Response and handling
    'ErrorResponse', 'ErrorContext', 'ErrorTracker',
    
    # Decorators and utilities
    'handle_errors', 'display_error_to_user', 'log_error', 'create_error_response', 'safe_execute',
    
    # Global instances
    'error_tracker'
] 