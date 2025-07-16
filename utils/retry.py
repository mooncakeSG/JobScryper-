"""
Auto Applyer - Retry Mechanism Module

This module provides comprehensive retry utilities including:
- Exponential backoff with jitter
- Circuit breaker pattern
- Rate limiting integration
- API-specific retry strategies
- Failure tracking and recovery
"""

import time
import random
import asyncio
from typing import Callable, Any, Optional, Dict, List, Type, Union
from functools import wraps
from enum import Enum
from datetime import datetime, timedelta
import logging

from .errors import APIError, RateLimitError, NetworkError, AutoApplyerError
from .logging_config import get_logger


class RetryStrategy(Enum):
    """Different retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    IMMEDIATE = "immediate"


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failure state, all calls fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_multiplier: float = 2.0,
        jitter: bool = True,
        strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF,
        retryable_exceptions: Optional[List[Type[Exception]]] = None,
        non_retryable_exceptions: Optional[List[Type[Exception]]] = None
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
        self.jitter = jitter
        self.strategy = strategy
        self.retryable_exceptions = retryable_exceptions or [
            APIError, NetworkError, RateLimitError, ConnectionError, TimeoutError
        ]
        self.non_retryable_exceptions = non_retryable_exceptions or [
            ValueError, TypeError, AttributeError
        ]


class CircuitBreaker:
    """Circuit breaker implementation for API calls"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: Type[Exception] = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
        self.logger = get_logger(__name__)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                self.logger.info("Circuit breaker: Attempting reset to HALF_OPEN")
            else:
                raise APIError(
                    f"Circuit breaker is OPEN. Service unavailable. "
                    f"Will retry after {self.recovery_timeout} seconds."
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True
        
        return (datetime.now() - self.last_failure_time).total_seconds() >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.logger.info("Circuit breaker: Reset to CLOSED after successful call")
        
        self.failure_count = 0
        self.state = CircuitState.CLOSED
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.warning(
                f"Circuit breaker: OPENED after {self.failure_count} failures. "
                f"Will remain open for {self.recovery_timeout} seconds."
            )


class RetryHandler:
    """Main retry handler with exponential backoff and circuit breaker"""
    
    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self.circuit_breakers = {}
        self.logger = get_logger(__name__)
    
    def retry(
        self,
        func: Callable,
        *args,
        circuit_breaker_key: Optional[str] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            circuit_breaker_key: Key for circuit breaker (if None, no circuit breaker)
            **kwargs: Keyword arguments for the function
            
        Returns:
            Function result
            
        Raises:
            Exception: After all retry attempts are exhausted
        """
        
        # Get or create circuit breaker
        circuit_breaker = None
        if circuit_breaker_key:
            if circuit_breaker_key not in self.circuit_breakers:
                self.circuit_breakers[circuit_breaker_key] = CircuitBreaker()
            circuit_breaker = self.circuit_breakers[circuit_breaker_key]
        
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                # Execute with circuit breaker if provided
                if circuit_breaker:
                    return circuit_breaker.call(func, *args, **kwargs)
                else:
                    return func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                # Check if exception is retryable
                if not self._is_retryable_exception(e):
                    self.logger.error(f"Non-retryable exception: {type(e).__name__}: {str(e)}")
                    raise e
                
                # Check if this is the last attempt
                if attempt == self.config.max_attempts - 1:
                    self.logger.error(
                        f"All {self.config.max_attempts} retry attempts exhausted. "
                        f"Last exception: {type(e).__name__}: {str(e)}"
                    )
                    break
                
                # Calculate delay and wait
                delay = self._calculate_delay(attempt)
                
                self.logger.warning(
                    f"Attempt {attempt + 1}/{self.config.max_attempts} failed: "
                    f"{type(e).__name__}: {str(e)}. Retrying in {delay:.1f} seconds..."
                )
                
                # Handle rate limit specific delays
                if isinstance(e, RateLimitError) and hasattr(e, 'retry_after'):
                    delay = max(delay, e.retry_after)
                
                time.sleep(delay)
        
        # All attempts failed
        raise last_exception
    
    async def async_retry(
        self,
        func: Callable,
        *args,
        circuit_breaker_key: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Async version of retry handler"""
        
        circuit_breaker = None
        if circuit_breaker_key:
            if circuit_breaker_key not in self.circuit_breakers:
                self.circuit_breakers[circuit_breaker_key] = CircuitBreaker()
            circuit_breaker = self.circuit_breakers[circuit_breaker_key]
        
        last_exception = None
        
        for attempt in range(self.config.max_attempts):
            try:
                if circuit_breaker:
                    return circuit_breaker.call(func, *args, **kwargs)
                else:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
            
            except Exception as e:
                last_exception = e
                
                if not self._is_retryable_exception(e):
                    self.logger.error(f"Non-retryable exception: {type(e).__name__}: {str(e)}")
                    raise e
                
                if attempt == self.config.max_attempts - 1:
                    self.logger.error(
                        f"All {self.config.max_attempts} async retry attempts exhausted. "
                        f"Last exception: {type(e).__name__}: {str(e)}"
                    )
                    break
                
                delay = self._calculate_delay(attempt)
                
                self.logger.warning(
                    f"Async attempt {attempt + 1}/{self.config.max_attempts} failed: "
                    f"{type(e).__name__}: {str(e)}. Retrying in {delay:.1f} seconds..."
                )
                
                if isinstance(e, RateLimitError) and hasattr(e, 'retry_after'):
                    delay = max(delay, e.retry_after)
                
                await asyncio.sleep(delay)
        
        raise last_exception
    
    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Check if exception is retryable"""
        
        # Check non-retryable exceptions first
        for exc_type in self.config.non_retryable_exceptions:
            if isinstance(exception, exc_type):
                return False
        
        # Check retryable exceptions
        for exc_type in self.config.retryable_exceptions:
            if isinstance(exception, exc_type):
                return True
        
        # Default behavior for unknown exceptions
        return False
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for next retry attempt"""
        
        if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.initial_delay * (self.config.backoff_multiplier ** attempt)
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.initial_delay * (attempt + 1)
        elif self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.initial_delay
        else:  # IMMEDIATE
            delay = 0
        
        # Cap at max delay
        delay = min(delay, self.config.max_delay)
        
        # Add jitter to prevent thundering herd
        if self.config.jitter and delay > 0:
            jitter_range = delay * 0.1  # 10% jitter
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(delay, 0)


# ============================================================================
# API-Specific Retry Configurations
# ============================================================================

class APIRetryConfigs:
    """Predefined retry configurations for different APIs"""
    
    GROQ_CONFIG = RetryConfig(
        max_attempts=3,
        initial_delay=1.0,
        max_delay=30.0,
        backoff_multiplier=2.0,
        retryable_exceptions=[APIError, RateLimitError, NetworkError]
    )
    
    JOBSPY_CONFIG = RetryConfig(
        max_attempts=2,  # JobSpy is slower, fewer retries
        initial_delay=5.0,
        max_delay=60.0,
        backoff_multiplier=2.0,
        retryable_exceptions=[APIError, NetworkError, ConnectionError]
    )
    
    ADZUNA_CONFIG = RetryConfig(
        max_attempts=3,
        initial_delay=2.0,
        max_delay=45.0,
        backoff_multiplier=2.0,
        retryable_exceptions=[APIError, RateLimitError, NetworkError]
    )
    
    JOOBLE_CONFIG = RetryConfig(
        max_attempts=3,
        initial_delay=1.5,
        max_delay=30.0,
        backoff_multiplier=2.0,
        retryable_exceptions=[APIError, RateLimitError, NetworkError]
    )
    
    DEFAULT_CONFIG = RetryConfig()


# ============================================================================
# Decorators
# ============================================================================

def retry_on_failure(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    circuit_breaker_key: Optional[str] = None,
    api_name: Optional[str] = None
):
    """
    Decorator for automatic retry on failure
    
    Args:
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay between retries
        backoff_multiplier: Multiplier for exponential backoff
        circuit_breaker_key: Key for circuit breaker
        api_name: API name for predefined configuration
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get configuration
            if api_name:
                config = getattr(APIRetryConfigs, f"{api_name.upper()}_CONFIG", APIRetryConfigs.DEFAULT_CONFIG)
            else:
                config = RetryConfig(
                    max_attempts=max_attempts,
                    initial_delay=initial_delay,
                    backoff_multiplier=backoff_multiplier
                )
            
            handler = RetryHandler(config)
            return handler.retry(func, *args, circuit_breaker_key=circuit_breaker_key, **kwargs)
        
        return wrapper
    return decorator


def async_retry_on_failure(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    circuit_breaker_key: Optional[str] = None,
    api_name: Optional[str] = None
):
    """Async version of retry decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if api_name:
                config = getattr(APIRetryConfigs, f"{api_name.upper()}_CONFIG", APIRetryConfigs.DEFAULT_CONFIG)
            else:
                config = RetryConfig(
                    max_attempts=max_attempts,
                    initial_delay=initial_delay,
                    backoff_multiplier=backoff_multiplier
                )
            
            handler = RetryHandler(config)
            return await handler.async_retry(func, *args, circuit_breaker_key=circuit_breaker_key, **kwargs)
        
        return wrapper
    return decorator


# ============================================================================
# Utility Functions
# ============================================================================

def execute_with_retry(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    circuit_breaker_key: Optional[str] = None,
    **kwargs
) -> Any:
    """Execute function with retry logic"""
    handler = RetryHandler(config or RetryConfig())
    return handler.retry(func, *args, circuit_breaker_key=circuit_breaker_key, **kwargs)


async def execute_with_async_retry(
    func: Callable,
    *args,
    config: Optional[RetryConfig] = None,
    circuit_breaker_key: Optional[str] = None,
    **kwargs
) -> Any:
    """Execute async function with retry logic"""
    handler = RetryHandler(config or RetryConfig())
    return await handler.async_retry(func, *args, circuit_breaker_key=circuit_breaker_key, **kwargs)


def get_api_retry_config(api_name: str) -> RetryConfig:
    """Get predefined retry configuration for an API"""
    config_name = f"{api_name.upper()}_CONFIG"
    return getattr(APIRetryConfigs, config_name, APIRetryConfigs.DEFAULT_CONFIG)


# ============================================================================
# Global Instances
# ============================================================================

# Global retry handler with default configuration
default_retry_handler = RetryHandler()

# API-specific retry handlers
api_retry_handlers = {
    'groq': RetryHandler(APIRetryConfigs.GROQ_CONFIG),
    'jobspy': RetryHandler(APIRetryConfigs.JOBSPY_CONFIG),
    'adzuna': RetryHandler(APIRetryConfigs.ADZUNA_CONFIG),
    'jooble': RetryHandler(APIRetryConfigs.JOOBLE_CONFIG)
}


def get_retry_handler(api_name: Optional[str] = None) -> RetryHandler:
    """Get retry handler for specific API or default"""
    if api_name and api_name.lower() in api_retry_handlers:
        return api_retry_handlers[api_name.lower()]
    return default_retry_handler


# Export main classes and functions
__all__ = [
    'RetryConfig', 'RetryStrategy', 'CircuitBreaker', 'RetryHandler',
    'APIRetryConfigs', 'retry_on_failure', 'async_retry_on_failure',
    'execute_with_retry', 'execute_with_async_retry', 'get_api_retry_config',
    'get_retry_handler', 'default_retry_handler'
] 