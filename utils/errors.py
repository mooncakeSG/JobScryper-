"""
Auto Applyer - Error Handling System

Custom exception classes and error handling utilities for the Auto Applyer application.
"""

import traceback
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path
import re


class AutoApplyerError(Exception):
    """Base exception class for Auto Applyer application."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None, 
                 error_code: Optional[str] = None):
        """
        Initialize the base error.
        
        Args:
            message: Human-readable error message
            details: Additional error details
            error_code: Optional error code for programmatic handling
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.error_code = error_code
        self.timestamp = datetime.now()
        self.traceback = traceback.format_exc()
    
    @property
    def error_type(self) -> str:
        """Get the error type for the error."""
        if self.error_code:
            return self.error_code
        # Convert CamelCase to UPPER_SNAKE_CASE
        name = self.__class__.__name__
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        snake = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()
        return snake
    
    def to_response(self):
        """Return self for API response chaining."""
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for API responses."""
        return {
            'error': True,
            'message': self.message,
            'error_type': self.error_type,
            'error_code': self.error_code,
            'details': self.details,
            'timestamp': self.timestamp.isoformat(),
            'type': self.__class__.__name__,
            'severity': 'HIGH'  # Default severity for all errors
        }
    
    def __str__(self) -> str:
        """String representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def to_user_message(self) -> str:
        """Get user-friendly error message."""
        # Map error types to user-friendly messages
        friendly_messages = {
            'API_ERROR': 'Service temporarily unavailable',
            'NETWORK_ERROR': 'Network connection issue',
            'VALIDATION_ERROR': f'Invalid input: {self.message}',
            'FILE_PROCESSING_ERROR': 'File operation failed',
            'AUTHENTICATION_ERROR': 'Authentication failed',
            'RATE_LIMIT_ERROR': 'Too many requests, please try again later',
            'DATABASE_ERROR': 'Database operation failed',
            'MIGRATION_ERROR': 'System update failed',
            'CONFIG_ERROR': 'Configuration error',
            'EXTERNAL_SERVICE_ERROR': 'External service unavailable',
            'AI_PROCESSING_ERROR': 'AI processing failed',
            'JOB_SEARCH_ERROR': 'Job search failed',
            'RESOURCE_ERROR': 'System resources exhausted',
            'PARSE_ERROR': 'Data processing failed'
        }
        
        # Get friendly message based on error type
        friendly_msg = friendly_messages.get(self.error_type, self.message)
        
        # Add retry information for rate limit errors
        if self.error_type == 'RATE_LIMIT_ERROR' and 'retry_after' in self.details:
            friendly_msg += f". Retry after {self.details['retry_after']} seconds"
        
        return friendly_msg


class DatabaseError(AutoApplyerError):
    """Database-related errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None, 
                 table: Optional[str] = None, query: Optional[str] = None):
        """
        Initialize database error.
        
        Args:
            message: Error message
            operation: Database operation that failed
            table: Table involved in the error
            query: SQL query that caused the error
        """
        details = {
            'operation': operation,
            'table': table,
            'query': query
        }
        super().__init__(message, details=details, error_code="DB_ERROR")


class MigrationError(AutoApplyerError):
    """Database migration errors."""
    
    def __init__(self, message: str, migration_version: Optional[str] = None,
                 migration_step: Optional[str] = None, rollback_available: bool = False):
        """
        Initialize migration error.
        
        Args:
            message: Error message
            migration_version: Version of migration that failed
            migration_step: Step within migration that failed
            rollback_available: Whether rollback is available
        """
        details = {
            'migration_version': migration_version,
            'migration_step': migration_step,
            'rollback_available': rollback_available
        }
        super().__init__(message, details=details, error_code="MIGRATION_ERROR")


class APIError(AutoApplyerError):
    """API-related errors."""
    
    def __init__(self, message: str, api_name: Optional[str] = None, status_code: int = 500, response_data: Optional[str] = None):
        details = {
            'api_name': api_name,
            'status_code': status_code,
            'response_data': response_data
        }
        super().__init__(message, details=details, error_code="API_ERROR")


class AuthenticationError(AutoApplyerError):
    """Authentication and authorization errors."""
    
    def __init__(self, message: str, auth_type: Optional[str] = None,
                 user_id: Optional[int] = None, required_permissions: Optional[List[str]] = None):
        """
        Initialize authentication error.
        
        Args:
            message: Error message
            auth_type: Type of authentication that failed
            user_id: User ID involved
            required_permissions: Required permissions
        """
        details = {
            'auth_type': auth_type,
            'user_id': user_id,
            'required_permissions': required_permissions
        }
        super().__init__(message, details=details, error_code="AUTH_ERROR")


class ValidationError(AutoApplyerError):
    """Data validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Optional[Any] = None, expected_type: Optional[str] = None):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Invalid value
            expected_type: Expected data type
        """
        details = {
            'field': field,
            'value': value,
            'expected_type': expected_type
        }
        super().__init__(message, details=details, error_code="VALIDATION_ERROR")


class ConfigurationError(AutoApplyerError):
    """Configuration-related errors."""
    
    def __init__(self, message: str, config_key: Optional[str] = None,
                 config_file: Optional[str] = None, environment: Optional[str] = None):
        """
        Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            config_file: Configuration file involved
            environment: Environment where error occurred
        """
        details = {
            'config_key': config_key,
            'config_file': config_file,
            'environment': environment
        }
        super().__init__(message, details=details, error_code="CONFIG_ERROR")


class ExternalServiceError(AutoApplyerError):
    """External service integration errors."""
    
    def __init__(self, message: str, service_name: Optional[str] = None,
                 service_url: Optional[str] = None, response_code: Optional[int] = None):
        """
        Initialize external service error.
        
        Args:
            message: Error message
            service_name: Name of external service
            service_url: Service URL that failed
            response_code: HTTP response code from service
        """
        details = {
            'service_name': service_name,
            'service_url': service_url,
            'response_code': response_code
        }
        super().__init__(message, details=details, error_code="EXTERNAL_SERVICE_ERROR")


class FileProcessingError(AutoApplyerError):
    """File processing errors."""
    
    def __init__(self, message: str, file_path: Optional[str] = None,
                 file_type: Optional[str] = None, operation: Optional[str] = None):
        """
        Initialize file processing error.
        
        Args:
            message: Error message
            file_path: Path to file that caused error
            file_type: Type of file being processed
            operation: File operation that failed
        """
        details = {
            'file_path': file_path,
            'file_type': file_type,
            'operation': operation
        }
        super().__init__(message, details=details, error_code="FILE_PROCESSING_ERROR")


class JobSearchError(AutoApplyerError):
    """Job search and scraping errors."""
    
    def __init__(self, message: str, source: Optional[str] = None,
                 search_query: Optional[str] = None, rate_limited: bool = False):
        """
        Initialize job search error.
        
        Args:
            message: Error message
            source: Job source that failed
            search_query: Search query that caused error
            rate_limited: Whether error is due to rate limiting
        """
        details = {
            'source': source,
            'search_query': search_query,
            'rate_limited': rate_limited
        }
        super().__init__(message, details=details, error_code="JOB_SEARCH_ERROR")


class AIProcessingError(AutoApplyerError):
    """AI and machine learning processing errors."""
    
    def __init__(self, message: str, model: Optional[str] = None,
                 input_type: Optional[str] = None, tokens_used: Optional[int] = None):
        """
        Initialize AI processing error.
        
        Args:
            message: Error message
            model: AI model that failed
            input_type: Type of input being processed
            tokens_used: Number of tokens used before error
        """
        details = {
            'model': model,
            'input_type': input_type,
            'tokens_used': tokens_used
        }
        super().__init__(message, details=details, error_code="AI_PROCESSING_ERROR")


class NetworkError(AutoApplyerError):
    """Network and connectivity errors."""
    
    def __init__(self, message: str, url: Optional[str] = None,
                 timeout: Optional[float] = None, retry_count: Optional[int] = None):
        """
        Initialize network error.
        
        Args:
            message: Error message
            url: URL that failed to connect
            timeout: Timeout value used
            retry_count: Number of retries attempted
        """
        details = {
            'url': url,
            'timeout': timeout,
            'retry_count': retry_count
        }
        super().__init__(message, details=details, error_code="NETWORK_ERROR")


class ResourceError(AutoApplyerError):
    """Resource exhaustion errors."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None,
                 current_usage: Optional[float] = None, limit: Optional[float] = None):
        """
        Initialize resource error.
        
        Args:
            message: Error message
            resource_type: Type of resource (memory, disk, etc.)
            current_usage: Current resource usage
            limit: Resource limit
        """
        details = {
            'resource_type': resource_type,
            'current_usage': current_usage,
            'limit': limit
        }
        super().__init__(message, details=details, error_code="RESOURCE_ERROR")


class APIKeyError(AutoApplyerError):
    """API key related errors."""
    
    def __init__(self, message: str, api_name: Optional[str] = None,
                 key_type: Optional[str] = None, is_missing: bool = False):
        # If message is just the API name, format it properly
        if api_name is None and not message.startswith("API key"):
            api_name = message
            message = f"API key for {api_name} is missing or invalid"
        
        details = {
            'api_name': api_name,
            'key_type': key_type,
            'is_missing': is_missing
        }
        super().__init__(message, details=details, error_code="AUTHENTICATION_ERROR")


class RateLimitError(AutoApplyerError):
    """Rate limiting errors."""
    
    def __init__(self, message: str, service_name: Optional[str] = None,
                 retry_after: Optional[int] = None, limit_type: Optional[str] = None):
        """
        Initialize rate limit error.
        
        Args:
            message: Error message or service name
            service_name: Name of the service
            retry_after: Seconds to wait before retrying
            limit_type: Type of rate limit (requests, tokens, etc.)
        """
        # If message is just the service name, format it properly
        if service_name is None and not message.startswith("Rate limit"):
            service_name = message
            message = f"Rate limit exceeded for {service_name}"
            if retry_after:
                message += f". Retry after {retry_after} seconds"
        
        details = {
            'service_name': service_name,
            'retry_after': retry_after,
            'limit_type': limit_type
        }
        super().__init__(message, details=details, error_code="RATE_LIMIT_ERROR")


class ParseError(AutoApplyerError):
    """Data parsing errors."""
    
    def __init__(self, message: str, data_type: Optional[str] = None,
                 data_source: Optional[str] = None, parse_step: Optional[str] = None):
        """
        Initialize parse error.
        
        Args:
            message: Error message
            data_type: Type of data being parsed
            data_source: Source of the data
            parse_step: Step in parsing that failed
        """
        details = {
            'data_type': data_type,
            'data_source': data_source,
            'parse_step': parse_step
        }
        super().__init__(message, details=details, error_code="PARSE_ERROR")


class ErrorHandler:
    """Centralized error handling utility."""
    
    def __init__(self, log_errors: bool = True, error_log_file: Optional[str] = None):
        """
        Initialize error handler.
        
        Args:
            log_errors: Whether to log errors
            error_log_file: Path to error log file
        """
        self.log_errors = log_errors
        self.error_log_file = error_log_file or "logs/errors.log"
        self._ensure_log_directory()
    
    def _ensure_log_directory(self) -> None:
        """Ensure log directory exists."""
        log_path = Path(self.error_log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Handle an error and return error information.
        
        Args:
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            Dictionary containing error information
        """
        # Convert to AutoApplyerError if it's not already
        if not isinstance(error, AutoApplyerError):
            error = AutoApplyerError(str(error), details={'original_type': type(error).__name__})
        
        # Add context if provided
        if context:
            error.details.update(context)
        
        # Log error if enabled
        if self.log_errors:
            self._log_error(error)
        
        return error.to_dict()
    
    def _log_error(self, error: AutoApplyerError) -> None:
        """Log error to file."""
        try:
            with open(self.error_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{error.timestamp}] {error.__class__.__name__}: {error.message}\n")
                if error.details:
                    f.write(f"Details: {error.details}\n")
                if error.traceback:
                    f.write(f"Traceback: {error.traceback}\n")
                f.write("-" * 80 + "\n")
        except Exception as e:
            # Fallback to stderr if logging fails
            print(f"Failed to log error: {e}", file=sys.stderr)
            print(f"Original error: {error}", file=sys.stderr)
    
    def handle_and_raise(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Handle error and re-raise as AutoApplyerError.
        
        Args:
            error: The exception that occurred
            context: Additional context information
        """
        if isinstance(error, AutoApplyerError):
            self.handle_error(error, context)
            raise error
        
        # Convert and re-raise
        auto_error = AutoApplyerError(str(error), details={'original_type': type(error).__name__})
        if context:
            auto_error.details.update(context)
        
        self.handle_error(auto_error)
        raise auto_error


def handle_exceptions(func):
    """Decorator to handle exceptions in functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            handler = ErrorHandler()
            error_info = handler.handle_error(e, {
                'function': func.__name__,
                'args': str(args),
                'kwargs': str(kwargs)
            })
            raise AutoApplyerError(f"Function {func.__name__} failed: {str(e)}", 
                                 details=error_info)
    return wrapper


def safe_execute(func, *args, default_return=None, **kwargs):
    """
    Safely execute a function and return default value on error.
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Value to return on error
        **kwargs: Function keyword arguments
        
    Returns:
        Function result or default_return on error
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handler = ErrorHandler()
        handler.handle_error(e, {
            'function': func.__name__,
            'args': str(args),
            'kwargs': str(kwargs)
        })
        return default_return


# Global error handler instance
error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return error_handler


def set_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance."""
    global error_handler
    error_handler = handler


# Common error messages
ERROR_MESSAGES = {
    'database_connection_failed': 'Failed to connect to database',
    'migration_failed': 'Database migration failed',
    'validation_failed': 'Data validation failed',
    'authentication_failed': 'Authentication failed',
    'permission_denied': 'Permission denied',
    'file_not_found': 'File not found',
    'network_timeout': 'Network request timed out',
    'rate_limited': 'Rate limit exceeded',
    'resource_exhausted': 'System resources exhausted',
    'configuration_invalid': 'Invalid configuration',
    'external_service_unavailable': 'External service unavailable',
    'ai_processing_failed': 'AI processing failed',
    'job_search_failed': 'Job search failed',
    'file_processing_failed': 'File processing failed'
}


def create_error(error_type: str, **kwargs) -> AutoApplyerError:
    """
    Create an error of the specified type.
    
    Args:
        error_type: Type of error to create
        **kwargs: Additional error parameters
        
    Returns:
        AutoApplyerError instance
    """
    message = ERROR_MESSAGES.get(error_type, f"Unknown error: {error_type}")
    
    if error_type == 'database_connection_failed':
        return DatabaseError(message, **kwargs)
    elif error_type == 'migration_failed':
        return MigrationError(message, **kwargs)
    elif error_type == 'validation_failed':
        return ValidationError(message, **kwargs)
    elif error_type == 'authentication_failed':
        return AuthenticationError(message, **kwargs)
    elif error_type == 'file_not_found':
        return FileProcessingError(message, **kwargs)
    elif error_type == 'network_timeout':
        return NetworkError(message, **kwargs)
    elif error_type == 'rate_limited':
        return JobSearchError(message, rate_limited=True, **kwargs)
    elif error_type == 'resource_exhausted':
        return ResourceError(message, **kwargs)
    elif error_type == 'configuration_invalid':
        return ConfigurationError(message, **kwargs)
    elif error_type == 'external_service_unavailable':
        return ExternalServiceError(message, **kwargs)
    elif error_type == 'ai_processing_failed':
        return AIProcessingError(message, **kwargs)
    elif error_type == 'job_search_failed':
        return JobSearchError(message, **kwargs)
    elif error_type == 'file_processing_failed':
        return FileProcessingError(message, **kwargs)
    else:
        return AutoApplyerError(message, **kwargs)


# Error tracking system
class ErrorTracker:
    """Track errors for reporting and analysis."""
    
    def __init__(self):
        """Initialize error tracker."""
        self.errors = []
        self.error_counts = {}
    
    def track_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Track an error for reporting.
        
        Args:
            error: The exception that occurred
            context: Additional context information
        """
        error_info = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context or {}
        }
        
        self.errors.append(error_info)
        
        # Update error counts using error_type:severity format
        if hasattr(error, 'error_type'):
            error_type = error.error_type
            # Map error types to severities
            severity_map = {
                'API_ERROR': 'high',
                'AUTHENTICATION_ERROR': 'high',
                'DATABASE_ERROR': 'high',
                'NETWORK_ERROR': 'medium',
                'VALIDATION_ERROR': 'low',
                'CONFIG_ERROR': 'medium',
                'FILE_PROCESSING_ERROR': 'medium',
                'RATE_LIMIT_ERROR': 'medium',
                'JOB_SEARCH_ERROR': 'medium',
                'AI_PROCESSING_ERROR': 'medium',
                'EXTERNAL_SERVICE_ERROR': 'medium',
                'RESOURCE_ERROR': 'high',
                'PARSE_ERROR': 'medium',
                'MIGRATION_ERROR': 'high'
            }
            severity = severity_map.get(error_type, 'medium')
            count_key = f"{error_type.lower()}:{severity}"
        else:
            count_key = f"{type(error).__name__.lower()}:high"
        
        self.error_counts[count_key] = self.error_counts.get(count_key, 0) + 1
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of tracked errors."""
        return {
            'total_errors': len(self.errors),
            'error_counts': self.error_counts.copy(),
            'recent_errors': self.errors[-10:] if self.errors else []
        }
    
    def clear_errors(self) -> None:
        """Clear all tracked errors."""
        self.errors.clear()
        self.error_counts.clear()


class ErrorContext:
    """Context manager for error handling with optional spinner."""
    
    def __init__(self, operation_name: str, show_spinner: bool = True):
        """
        Initialize error context.
        
        Args:
            operation_name: Name of the operation
            show_spinner: Whether to show a spinner
        """
        self.operation_name = operation_name
        self.show_spinner = show_spinner
        self.spinner = None
    
    def __enter__(self):
        """Enter the context."""
        if self.show_spinner:
            try:
                import streamlit as st
                self.spinner = st.spinner(f"🔄 {self.operation_name}...")
                self.spinner.__enter__()
            except ImportError:
                print(f"🔄 {self.operation_name}...")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context."""
        if self.spinner:
            try:
                self.spinner.__exit__(exc_type, exc_val, exc_tb)
            except:
                pass
        
        if exc_type is not None:
            # Log the error
            log_error(exc_val, {'operation': self.operation_name})
            return False  # Re-raise the exception
        return True


# Global error tracker instance
error_tracker = ErrorTracker()


def handle_errors(operation_name: str = "Operation", show_user_error: bool = True, 
                 show_technical_details: bool = False, log_errors: bool = True,
                 default_return_value=None):
    """
    Decorator for handling errors in functions.
    
    Args:
        operation_name: Name of the operation for logging
        show_user_error: Whether to show error to user
        show_technical_details: Whether to show technical details
        log_errors: Whether to log errors
        default_return_value: Value to return on error
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Track the error
                error_tracker.track_error(e, {
                    'operation': operation_name,
                    'function': func.__name__,
                    'args': str(args),
                    'kwargs': str(kwargs)
                })
                
                # Log error if enabled
                if log_errors:
                    logger = get_logger()
                    logger.error(f"Error in {operation_name}: {str(e)}", exc_info=True)
                
                # Show error to user if enabled
                if show_user_error:
                    display_error_to_user(e, show_technical_details=show_technical_details)
                
                return default_return_value
        return wrapper
    return decorator


def display_error_to_user(error: Exception, show_technical_details: bool = False) -> None:
    """
    Display error to user in a user-friendly way.
    
    Args:
        error: The exception to display
        show_technical_details: Whether to show technical details
    """
    try:
        import streamlit as st
        
        if isinstance(error, AutoApplyerError):
            st.error(f"❌ {error.message}")
            if show_technical_details and error.details:
                with st.expander("Technical Details"):
                    st.json(error.details)
        else:
            st.error(f"❌ An error occurred: {str(error)}")
            if show_technical_details:
                with st.expander("Technical Details"):
                    st.code(traceback.format_exc())
    except ImportError:
        # Fallback if streamlit is not available
        print(f"Error: {str(error)}")
        if show_technical_details:
            print(f"Technical details: {traceback.format_exc()}")


def log_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an error with context.
    
    Args:
        error: The exception to log
        context: Additional context information
    """
    logger = get_logger()
    context_str = f" Context: {context}" if context else ""
    logger.error(f"Error: {str(error)}{context_str}", exc_info=True)


def get_logger():
    """Get logger instance."""
    try:
        from .logging_config import get_logger as get_app_logger
        return get_app_logger("utils.errors")
    except ImportError:
        import logging
        return logging.getLogger("utils.errors")


def exception_to_response(exc: Exception):
    class GenericErrorResponse:
        def __init__(self, exc):
            self.exc = exc
        def to_dict(self):
            return {
                'error': True,
                'message': str(self.exc),
                'error_type': 'INTERNAL_ERROR',
                'details': {'exception_type': type(self.exc).__name__},
                'timestamp': datetime.now().isoformat(),
                'type': type(self.exc).__name__,
                'severity': 'HIGH'
            }
    return GenericErrorResponse(exc)