"""
Unit tests for the error handling system.

Tests the comprehensive error handling framework including custom exceptions,
error responses, validation, and retry mechanisms.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import the modules we're testing
from utils.errors import (
    AutoApplyerError, APIError, APIKeyError, RateLimitError,
    NetworkError, ValidationError, ParseError, FileProcessingError,
    handle_errors, error_tracker
)
from utils.validation import (
    InputValidator, validate_job_search, sanitize_input,
    validate_text_input
)
from utils.retry import (
    RetryHandler, RetryConfig, CircuitBreaker,
    execute_with_retry, get_retry_handler
)


class TestCustomExceptions:
    """Test custom exception classes."""
    
    def test_auto_applyer_error_creation(self):
        """Test basic AutoApplyerError creation."""
        error = AutoApplyerError(
            "Test error",
            {"key": "value"},
            "high"
        )
        
        assert error.message == "Test error"
        assert error.error_type == "high"  # error_code becomes error_type
        assert error.details == {"key": "value"}
        assert error.timestamp is not None
    
    def test_api_error_creation(self):
        """Test APIError creation with specific details."""
        error = APIError("API failed", "TestAPI", 500, "Server Error")
        
        assert error.message == "API failed"
        assert error.error_type == "API_ERROR"
        assert error.details["api_name"] == "TestAPI"
        assert error.details["status_code"] == 500
        assert error.details["response_data"] == "Server Error"
    
    def test_api_key_error(self):
        """Test APIKeyError specific behavior."""
        error = APIKeyError("TestAPI")
        
        assert "API key for TestAPI" in error.message
        assert error.error_type == "AUTHENTICATION_ERROR"
        assert error.details["api_name"] == "TestAPI"
    
    def test_rate_limit_error(self):
        """Test RateLimitError with retry information."""
        error = RateLimitError("TestAPI", retry_after=60)
        
        assert "Rate limit exceeded for TestAPI" in error.message
        assert "60 seconds" in error.message
        assert error.error_type == "RATE_LIMIT_ERROR"
        assert error.details["retry_after"] == 60
    
    def test_validation_error(self):
        """Test ValidationError with field information."""
        error = ValidationError("Invalid input", "email", "invalid@")
        
        assert error.message == "Invalid input"
        assert error.error_type == "VALIDATION_ERROR"
        assert error.details["field"] == "email"
        assert error.details["value"] == "invalid@"


class TestErrorResponse:
    """Test error response formatting."""
    
    def test_auto_applyer_error_response(self):
        """Test error response from AutoApplyerError."""
        error = APIError("Test API error", "TestAPI", 500)
        response = error.to_response()
        response_dict = response.to_dict()
        
        assert response_dict["error"] is True
        assert response_dict["message"] == "Test API error"
        assert response_dict["error_type"] == "API_ERROR"
        assert response_dict["severity"] == "HIGH"
        assert "details" in response_dict
        assert "timestamp" in response_dict
    
    def test_generic_exception_response(self):
        """Test error response from generic exception."""
        error = ValueError("Generic error")
        from utils.errors import exception_to_response
        response = exception_to_response(error)
        response_dict = response.to_dict()
        
        assert response_dict["error"] is True
        assert response_dict["message"] == "Generic error"
        assert response_dict["error_type"] == "INTERNAL_ERROR"
        assert response_dict["details"]["exception_type"] == "ValueError"
    
    def test_user_friendly_messages(self):
        """Test user-friendly error message generation."""
        test_cases = [
            (APIError("API failed", "TestAPI"), "Service temporarily unavailable"),
            (NetworkError("Network timeout"), "Network connection issue"),
            (ValidationError("Invalid email", "email"), "Invalid input: Invalid email"),
            (FileProcessingError("File not found", "/path/to/file"), "File operation failed")
        ]
        
        for error, expected_message in test_cases:
            response = error.to_response()
            user_message = response.to_user_message()
            assert expected_message in user_message


class TestErrorTracker:
    """Test error tracking functionality."""
    
    def setup_method(self):
        """Reset error tracker before each test."""
        error_tracker.clear_errors()
    
    def test_track_error(self):
        """Test error tracking."""
        error = APIError("Test error", "TestAPI")
        context = {"operation": "test_operation"}
        
        error_tracker.track_error(error, context)
        summary = error_tracker.get_error_summary()
        
        assert summary["total_errors"] == 1
        assert len(summary["recent_errors"]) == 1
        assert "api_error:high" in summary["error_counts"]
    
    def test_error_counts(self):
        """Test error counting by type and severity."""
        errors = [
            APIError("Error 1", "API1"),
            APIError("Error 2", "API2"),
            ValidationError("Error 3", "field1"),
        ]
        
        for error in errors:
            error_tracker.track_error(error)
        
        summary = error_tracker.get_error_summary()
        assert summary["total_errors"] == 3
        assert summary["error_counts"]["api_error:high"] == 2
        assert summary["error_counts"]["validation_error:low"] == 1


class TestErrorHandlingDecorator:
    """Test the @handle_errors decorator."""
    
    def test_successful_function(self):
        """Test decorator with successful function."""
        @handle_errors(
            operation_name="Test Operation",
            show_user_error=False,
            default_return_value="default"
        )
        def successful_function():
            return "success"
        
        result = successful_function()
        assert result == "success"
    
    def test_function_with_exception(self):
        """Test decorator with function that raises exception."""
        @handle_errors(
            operation_name="Test Operation",
            show_user_error=False,
            default_return_value="default"
        )
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        assert result == "default"
    
    def test_decorator_with_logging(self):
        """Test that decorator logs errors properly."""
        with patch('utils.errors.logging.getLogger') as mock_logger:
            mock_log = Mock()
            mock_logger.return_value = mock_log
            
            @handle_errors(
                operation_name="Test Operation",
                show_user_error=False,
                log_errors=True
            )
            def failing_function():
                raise ValueError("Test error")
            
            failing_function()
            mock_log.error.assert_called_once()


class TestInputValidation:
    """Test input validation functionality."""
    
    def test_valid_job_search_params(self):
        """Test validation of valid job search parameters."""
        params = {
            'job_title': 'Python Developer',
            'location': 'Cape Town',
            'job_type': 'Full-time',
            'keywords': 'Python, Django',
            'max_results': 50
        }
        
        validated = validate_job_search(params)
        
        assert validated['job_title'] == 'Python Developer'
        assert validated['location'] == 'Cape Town'
        assert validated['job_type'] == 'Full-time'
        assert validated['keywords'] == 'Python, Django'
        assert validated['max_results'] == 50
    
    def test_invalid_job_search_params(self):
        """Test validation with invalid parameters."""
        # Empty job title
        with pytest.raises(ValidationError) as exc_info:
            validate_job_search({'job_title': '', 'location': 'Cape Town'})
        assert "Job title is required" in str(exc_info.value)
        
        # Invalid max_results
        with pytest.raises(ValidationError) as exc_info:
            validate_job_search({'job_title': 'Developer', 'max_results': 'invalid'})
        assert "must be a valid number" in str(exc_info.value)
        
        # Max results out of range
        with pytest.raises(ValidationError) as exc_info:
            validate_job_search({'job_title': 'Developer', 'max_results': 300})
        assert "between 1 and 200" in str(exc_info.value)
    
    def test_text_sanitization(self):
        """Test text sanitization functionality."""
        dangerous_inputs = [
            "<script>alert('xss')</script>Normal text",
            "javascript:alert('xss')",
            "Normal text<img src=x onerror=alert(1)>",
            "eval('dangerous code')"
        ]
        
        for dangerous_input in dangerous_inputs:
            sanitized = sanitize_input(dangerous_input)
            
            # Should remove dangerous patterns
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized
            assert "eval(" not in sanitized
    
    def test_url_validation(self):
        """Test URL validation."""
        validator = InputValidator()
        
        # Valid URLs
        valid_urls = [
            "https://example.com",
            "http://job-site.com/job/123",
            "https://company.co.za/careers"
        ]
        
        for url in valid_urls:
            validated = validator.validate_url(url)
            assert validated == url
        
        # Invalid URLs
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",  # Wrong protocol
            "javascript:alert(1)"  # Dangerous protocol
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValidationError):
                validator.validate_url(url)
    
    def test_file_validation(self):
        """Test file validation functionality."""
        validator = InputValidator()
        
        # Test file validation would require actual files
        # This is a placeholder for file validation tests
        with pytest.raises(FileProcessingError):
            validator.validate_file_upload("/nonexistent/file.pdf")


class TestRetryMechanism:
    """Test retry functionality."""
    
    def test_successful_retry(self):
        """Test retry with function that succeeds on second attempt."""
        config = RetryConfig(max_attempts=3, initial_delay=0.1)
        handler = RetryHandler(config)
        
        call_count = 0
        
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise NetworkError("Network timeout")
            return "success"
        
        result = handler.retry(flaky_function)
        
        assert result == "success"
        assert call_count == 2
    
    def test_retry_exhaustion(self):
        """Test retry when all attempts fail."""
        config = RetryConfig(max_attempts=2, initial_delay=0.1)
        handler = RetryHandler(config)
        
        def always_failing_function():
            raise APIError("Always fails", "TestAPI")
        
        with pytest.raises(APIError):
            handler.retry(always_failing_function)
    
    def test_non_retryable_exception(self):
        """Test that non-retryable exceptions are not retried."""
        config = RetryConfig(max_attempts=3, initial_delay=0.1)
        handler = RetryHandler(config)
        
        call_count = 0
        
        def function_with_non_retryable_error():
            nonlocal call_count
            call_count += 1
            raise ValueError("This should not be retried")
        
        with pytest.raises(ValueError):
            handler.retry(function_with_non_retryable_error)
        
        # Should only be called once (no retries)
        assert call_count == 1
    
    def test_circuit_breaker(self):
        """Test circuit breaker functionality."""
        circuit_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)
        
        def failing_function():
            raise APIError("Service unavailable", "TestAPI")
        
        # First two failures should go through
        with pytest.raises(APIError):
            circuit_breaker.call(failing_function)
        
        with pytest.raises(APIError):
            circuit_breaker.call(failing_function)
        
        # Third call should be blocked by circuit breaker
        with pytest.raises(APIError) as exc_info:
            circuit_breaker.call(failing_function)
        
        assert "Circuit breaker is OPEN" in str(exc_info.value)
    
    def test_execute_with_retry_helper(self):
        """Test the execute_with_retry helper function."""
        call_count = 0
        
        def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise NetworkError("Temporary failure")
            return "success"
        
        result = execute_with_retry(flaky_function)
        assert result == "success"
        assert call_count == 2


class TestErrorContext:
    """Test ErrorContext context manager."""
    
    def test_successful_context(self):
        """Test ErrorContext with successful operation."""
        with ErrorContext("Test Operation", show_spinner=False) as ctx:
            # Simulate successful operation
            pass
        
        assert not ctx.error_occurred
    
    def test_error_context(self):
        """Test ErrorContext with error."""
        with ErrorContext("Test Operation", show_spinner=False) as ctx:
            raise ValueError("Test error")
        
        assert ctx.error_occurred


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling system."""
    
    def test_full_error_handling_workflow(self):
        """Test complete error handling workflow."""
        # This would test the integration of all error handling components
        # in a realistic scenario
        
        @handle_errors(
            operation_name="Integration Test",
            show_user_error=False,
            default_return_value={"error": "handled"}
        )
        def complex_operation():
            # Simulate complex operation with potential failures
            validator = InputValidator()
            
            # Validate some input
            validator.validate_user_text_input("test input", "test_field")
            
            # Simulate API call that might fail
            raise APIError("Service temporarily unavailable", "TestAPI", 503)
        
        result = complex_operation()
        assert result == {"error": "handled"}
    
    def test_retry_with_circuit_breaker(self):
        """Test retry mechanism with circuit breaker integration."""
        config = RetryConfig(max_attempts=3, initial_delay=0.1)
        handler = RetryHandler(config)
        
        call_count = 0
        
        def service_call():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise RateLimitError("TestAPI", retry_after=1)
            return {"status": "success"}
        
        result = handler.retry(service_call, circuit_breaker_key="test_service")
        
        assert result == {"status": "success"}
        assert call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 