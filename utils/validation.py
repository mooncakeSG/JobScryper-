"""
Auto Applyer - Input Validation Module

This module provides comprehensive input validation including:
- Job search parameter validation
- File upload validation
- API input sanitization
- User data validation
- Security input checks
"""

import re
import os
import mimetypes
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from urllib.parse import urlparse
import validators
from datetime import datetime, timedelta

from .errors import ValidationError, FileProcessingError


class InputValidator:
    """Comprehensive input validation utilities"""
    
    # Supported file formats
    SUPPORTED_RESUME_FORMATS = {'.pdf', '.docx', '.doc', '.txt'}
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    
    # File size limits (in bytes)
    MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024    # 5MB
    
    # Text length limits
    MAX_TEXT_LENGTH = 10000
    MAX_SEARCH_TERM_LENGTH = 100
    MAX_LOCATION_LENGTH = 100
    
    # Security patterns
    DANGEROUS_PATTERNS = [
        r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>',  # Script tags
        r'javascript:',                                          # JavaScript URLs
        r'on\w+\s*=',                                           # Event handlers
        r'eval\s*\(',                                           # eval() calls
        r'document\.cookie',                                     # Cookie access
        r'window\.location',                                     # Location redirect
    ]

    @classmethod
    def validate_job_search_params(cls, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate job search parameters
        
        Args:
            params: Dictionary of search parameters
            
        Returns:
            Validated and sanitized parameters
            
        Raises:
            ValidationError: If validation fails
        """
        validated = {}
        
        # Validate job title
        job_title = params.get('job_title', '').strip()
        if not job_title:
            raise ValidationError("Job title is required", field="job_title")
        
        if len(job_title) > cls.MAX_SEARCH_TERM_LENGTH:
            raise ValidationError(
                f"Job title must be {cls.MAX_SEARCH_TERM_LENGTH} characters or less",
                field="job_title",
                value=job_title
            )
        
        validated['job_title'] = cls.sanitize_text(job_title)
        
        # Validate location
        location = params.get('location', '').strip()
        if location and len(location) > cls.MAX_LOCATION_LENGTH:
            raise ValidationError(
                f"Location must be {cls.MAX_LOCATION_LENGTH} characters or less",
                field="location",
                value=location
            )
        
        validated['location'] = cls.sanitize_text(location) if location else "Remote"
        
        # Validate job type
        job_type = params.get('job_type', '')
        valid_job_types = {'Full-time', 'Part-time', 'Contract', 'Internship', 'Temporary', ''}
        if job_type not in valid_job_types:
            raise ValidationError(
                f"Invalid job type. Must be one of: {', '.join(valid_job_types)}",
                field="job_type",
                value=job_type
            )
        
        validated['job_type'] = job_type
        
        # Validate keywords
        keywords = params.get('keywords', '').strip()
        if keywords and len(keywords) > cls.MAX_TEXT_LENGTH:
            raise ValidationError(
                f"Keywords must be {cls.MAX_TEXT_LENGTH} characters or less",
                field="keywords",
                value=keywords
            )
        
        validated['keywords'] = cls.sanitize_text(keywords) if keywords else ""
        
        # Validate max results
        max_results = params.get('max_results', 50)
        try:
            max_results = int(max_results)
            if max_results < 1 or max_results > 200:
                raise ValidationError(
                    "Maximum results must be between 1 and 200",
                    field="max_results",
                    value=max_results
                )
        except (ValueError, TypeError):
            raise ValidationError(
                "Maximum results must be a valid number",
                field="max_results",
                value=max_results
            )
        
        validated['max_results'] = max_results
        
        return validated

    @classmethod
    def validate_file_upload(cls, file_path: Union[str, Path], file_type: str = "resume") -> Dict[str, Any]:
        """
        Validate uploaded file
        
        Args:
            file_path: Path to the uploaded file
            file_type: Type of file (resume, image, etc.)
            
        Returns:
            File validation info
            
        Raises:
            FileProcessingError: If file validation fails
        """
        file_path = Path(file_path)
        
        # Check if file exists
        if not file_path.exists():
            raise FileProcessingError(f"File not found: {file_path}", str(file_path), "validation")
        
        # Check file size
        file_size = file_path.stat().st_size
        
        if file_type == "resume":
            max_size = cls.MAX_RESUME_SIZE
            supported_formats = cls.SUPPORTED_RESUME_FORMATS
        elif file_type == "image":
            max_size = cls.MAX_IMAGE_SIZE
            supported_formats = cls.SUPPORTED_IMAGE_FORMATS
        else:
            raise ValidationError(f"Unsupported file type: {file_type}", field="file_type")
        
        if file_size > max_size:
            raise FileProcessingError(
                f"File size ({file_size:,} bytes) exceeds maximum allowed size ({max_size:,} bytes)",
                str(file_path),
                "size_validation"
            )
        
        # Check file format
        file_extension = file_path.suffix.lower()
        if file_extension not in supported_formats:
            raise FileProcessingError(
                f"Unsupported file format: {file_extension}. Supported formats: {', '.join(supported_formats)}",
                str(file_path),
                "format_validation"
            )
        
        # Validate MIME type
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not cls._is_valid_mime_type(mime_type, file_type):
            raise FileProcessingError(
                f"Invalid file content. Expected {file_type} but detected: {mime_type}",
                str(file_path),
                "mime_validation"
            )
        
        return {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_size": file_size,
            "file_extension": file_extension,
            "mime_type": mime_type,
            "is_valid": True
        }

    @classmethod
    def validate_api_input(cls, input_data: Dict[str, Any], api_name: str) -> Dict[str, Any]:
        """
        Validate API input data
        
        Args:
            input_data: Data to send to API
            api_name: Name of the API
            
        Returns:
            Validated input data
            
        Raises:
            ValidationError: If validation fails
        """
        validated = {}
        
        # Common validations for all APIs
        for key, value in input_data.items():
            if isinstance(value, str):
                # Check for dangerous patterns
                if cls._contains_dangerous_patterns(value):
                    raise ValidationError(
                        f"Input contains potentially dangerous content: {key}",
                        field=key,
                        value=value[:100]  # Truncate for security
                    )
                
                # Sanitize string values
                validated[key] = cls.sanitize_text(value)
            else:
                validated[key] = value
        
        # API-specific validations
        if api_name.lower() == "groq":
            return cls._validate_groq_input(validated)
        elif api_name.lower() == "jobspy":
            return cls._validate_jobspy_input(validated)
        else:
            return validated

    @classmethod
    def validate_user_text_input(cls, text: str, field_name: str, max_length: Optional[int] = None) -> str:
        """
        Validate and sanitize user text input
        
        Args:
            text: User input text
            field_name: Name of the field for error messages
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(text, str):
            raise ValidationError(f"{field_name} must be a string", field=field_name, value=text)
        
        text = text.strip()
        
        # Check length
        max_len = max_length or cls.MAX_TEXT_LENGTH
        if len(text) > max_len:
            raise ValidationError(
                f"{field_name} must be {max_len} characters or less",
                field=field_name,
                value=text[:100]
            )
        
        # Check for dangerous patterns
        if cls._contains_dangerous_patterns(text):
            raise ValidationError(
                f"{field_name} contains potentially dangerous content",
                field=field_name,
                value=text[:100]
            )
        
        return cls.sanitize_text(text)

    @classmethod
    def validate_url(cls, url: str, field_name: str = "url") -> str:
        """
        Validate URL format
        
        Args:
            url: URL to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated URL
            
        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            raise ValidationError(f"{field_name} is required", field=field_name)
        
        if not validators.url(url):
            raise ValidationError(f"Invalid URL format: {url}", field=field_name, value=url)
        
        # Check for dangerous protocols
        parsed = urlparse(url)
        if parsed.scheme.lower() not in ['http', 'https']:
            raise ValidationError(
                f"Only HTTP and HTTPS URLs are allowed: {url}",
                field=field_name,
                value=url
            )
        
        return url

    @classmethod
    def validate_email(cls, email: str, field_name: str = "email") -> str:
        """
        Validate email format
        
        Args:
            email: Email to validate
            field_name: Name of the field for error messages
            
        Returns:
            Validated email
            
        Raises:
            ValidationError: If email is invalid
        """
        if not email:
            raise ValidationError(f"{field_name} is required", field=field_name)
        
        if not validators.email(email):
            raise ValidationError(f"Invalid email format: {email}", field=field_name, value=email)
        
        return email.lower().strip()

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Sanitize text input by removing dangerous content
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    @classmethod
    def _contains_dangerous_patterns(cls, text: str) -> bool:
        """Check if text contains dangerous patterns"""
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    @classmethod
    def _is_valid_mime_type(cls, mime_type: str, file_type: str) -> bool:
        """Validate MIME type against expected file type"""
        if not mime_type:
            return False
        
        valid_mime_types = {
            "resume": [
                'application/pdf',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/msword',
                'text/plain'
            ],
            "image": [
                'image/jpeg',
                'image/png',
                'image/gif',
                'image/bmp'
            ]
        }
        
        return mime_type in valid_mime_types.get(file_type, [])

    @classmethod
    def _validate_groq_input(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Groq API specific input"""
        # Check for required fields
        if 'prompt' not in input_data and 'messages' not in input_data:
            raise ValidationError("Groq API requires either 'prompt' or 'messages'")
        
        # Validate prompt length
        if 'prompt' in input_data:
            prompt = input_data['prompt']
            if len(prompt) > 8000:  # Groq token limit consideration
                raise ValidationError("Prompt too long for Groq API", field="prompt")
        
        # Validate model name
        if 'model' in input_data:
            valid_models = [
                'llama3-8b-8192',
                'llama3-70b-8192',
                'mixtral-8x7b-32768',
                'gemma-7b-it'
            ]
            if input_data['model'] not in valid_models:
                raise ValidationError(
                    f"Invalid Groq model. Valid models: {', '.join(valid_models)}",
                    field="model"
                )
        
        return input_data

    @classmethod
    def _validate_jobspy_input(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate JobSpy specific input"""
        # Validate sites
        if 'sites' in input_data:
            valid_sites = ['indeed', 'linkedin', 'zip_recruiter', 'glassdoor', 'google']
            sites = input_data['sites']
            if isinstance(sites, list):
                invalid_sites = [site for site in sites if site not in valid_sites]
                if invalid_sites:
                    raise ValidationError(
                        f"Invalid job sites: {', '.join(invalid_sites)}. "
                        f"Valid sites: {', '.join(valid_sites)}",
                        field="sites"
                    )
        
        # Validate results count
        if 'max_results' in input_data:
            max_results = input_data['max_results']
            if not isinstance(max_results, int) or max_results < 1 or max_results > 100:
                raise ValidationError(
                    "JobSpy max_results must be between 1 and 100",
                    field="max_results"
                )
        
        return input_data


class RateLimitValidator:
    """Validate and track rate limits"""
    
    def __init__(self):
        self.request_history = {}
    
    def check_rate_limit(self, identifier: str, max_requests: int, time_window: int) -> Tuple[bool, int]:
        """
        Check if request is within rate limits
        
        Args:
            identifier: Unique identifier (user, IP, API key, etc.)
            max_requests: Maximum requests allowed
            time_window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, retry_after_seconds)
        """
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=time_window)
        
        # Clean old requests
        if identifier in self.request_history:
            self.request_history[identifier] = [
                req_time for req_time in self.request_history[identifier]
                if req_time > cutoff_time
            ]
        else:
            self.request_history[identifier] = []
        
        # Check current request count
        current_requests = len(self.request_history[identifier])
        
        if current_requests >= max_requests:
            # Calculate retry after time
            oldest_request = min(self.request_history[identifier])
            retry_after = int((oldest_request + timedelta(seconds=time_window) - now).total_seconds())
            return False, max(retry_after, 1)
        
        # Add current request
        self.request_history[identifier].append(now)
        return True, 0


# ============================================================================
# Convenience Functions
# ============================================================================

def validate_job_search(params: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function for job search validation"""
    return InputValidator.validate_job_search_params(params)


def validate_file(file_path: Union[str, Path], file_type: str = "resume") -> Dict[str, Any]:
    """Convenience function for file validation"""
    return InputValidator.validate_file_upload(file_path, file_type)


def sanitize_input(text: str) -> str:
    """Convenience function for text sanitization"""
    return InputValidator.sanitize_text(text)


def validate_text_input(text: str, field_name: str, max_length: Optional[int] = None) -> str:
    """Convenience function for text input validation"""
    return InputValidator.validate_user_text_input(text, field_name, max_length)


# ============================================================================
# Validation Decorators
# ============================================================================

def validate_inputs(**validation_rules):
    """
    Decorator to validate function inputs
    
    Usage:
        @validate_inputs(job_title=str, max_results=int)
        def search_jobs(job_title, max_results=50):
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function arguments
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate arguments
            for param_name, expected_type in validation_rules.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    if not isinstance(value, expected_type):
                        raise ValidationError(
                            f"Parameter '{param_name}' must be of type {expected_type.__name__}",
                            field=param_name,
                            value=value
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global rate limit validator instance
rate_limit_validator = RateLimitValidator()


# Export main classes and functions
__all__ = [
    'InputValidator', 'RateLimitValidator', 'ValidationError', 'FileProcessingError',
    'validate_job_search', 'validate_file', 'sanitize_input', 'validate_text_input',
    'validate_inputs', 'rate_limit_validator'
] 