import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        async with self.lock:
            now = datetime.now()
            # Remove requests older than 1 minute
            self.requests = [req_time for req_time in self.requests 
                           if now - req_time < timedelta(minutes=1)]
            
            if len(self.requests) >= self.requests_per_minute:
                # Wait until the oldest request is more than 1 minute old
                sleep_time = (self.requests[0] + timedelta(minutes=1) - now).total_seconds()
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            self.requests.append(now)

class UltraError(Exception):
    """Base exception for Ultra platform errors."""
    pass

class APIError(UltraError):
    """Exception for API-related errors."""
    pass

class RateLimitError(UltraError):
    """Exception for rate limit violations."""
    pass

class ConfigurationError(UltraError):
    """Exception for configuration-related errors."""
    pass

class ValidationError(UltraError):
    """Exception for input validation errors."""
    pass

def setup_logging():
    """Configure logging for the Ultra platform."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ultra.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def validate_api_keys(api_keys: Dict[str, str]) -> bool:
    """Validate API keys are present and properly formatted."""
    required_keys = ['openai', 'google', 'llama']
    for key in required_keys:
        if key not in api_keys or not api_keys[key]:
            raise ConfigurationError(f"Missing or invalid API key for {key}")
    return True

def validate_prompt(prompt: str) -> bool:
    """Validate user prompt."""
    if not prompt or not isinstance(prompt, str):
        raise ValidationError("Invalid prompt: must be a non-empty string")
    if len(prompt) > 4000:  # Example limit
        raise ValidationError("Prompt too long: maximum 4000 characters")
    return True

def handle_api_error(func: Callable):
    """Decorator for handling API errors with retries."""
    @wraps(func)
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((APIError, RateLimitError))
    )
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise RateLimitError(f"Rate limit exceeded: {str(e)}")
            raise APIError(f"API error in {func.__name__}: {str(e)}")
    return wrapper

def handle_validation_error(func: Callable):
    """Decorator for handling validation errors."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            logging.error(f"Validation error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            raise ValidationError(f"Unexpected validation error in {func.__name__}: {str(e)}")
    return wrapper

def handle_configuration_error(func: Callable):
    """Decorator for handling configuration errors."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConfigurationError as e:
            logging.error(f"Configuration error in {func.__name__}: {str(e)}")
            raise
        except Exception as e:
            raise ConfigurationError(f"Unexpected configuration error in {func.__name__}: {str(e)}")
    return wrapper

class ErrorTracker:
    """Track and manage errors across the platform."""
    def __init__(self):
        self.errors = []
        self.logger = setup_logging()
    
    def add_error(self, error: Exception, context: Dict[str, Any]):
        """Add an error with context to the tracker."""
        error_entry = {
            'timestamp': datetime.now(),
            'error_type': type(error).__name__,
            'message': str(error),
            'context': context
        }
        self.errors.append(error_entry)
        self.logger.error(f"Error tracked: {error_entry}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of tracked errors."""
        return {
            'total_errors': len(self.errors),
            'error_types': {
                error_type: len([e for e in self.errors if e['error_type'] == error_type])
                for error_type in set(e['error_type'] for e in self.errors)
            },
            'latest_errors': self.errors[-5:] if self.errors else []
        }
    
    def clear_errors(self):
        """Clear all tracked errors."""
        self.errors = []
        self.logger.info("Error tracker cleared") 