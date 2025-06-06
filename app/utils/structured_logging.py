"""
Enhanced structured logging for Ultra.

This module provides a comprehensive structured logging system that builds on
the existing logging infrastructure with additional features:

1. JSON-formatted logs for better machine readability
2. Request ID tracking for tracing requests across components
3. User ID and correlation ID inclusion in logs
4. Performance metrics and audit logging
5. Integration with cloud logging services
6. Standardized log levels and categories
7. Log sampling for high-volume endpoints
8. PII redaction for sensitive data

The module is designed to be used across all Ultra components to provide
consistent, searchable logs that can be easily aggregated and analyzed.
"""

import asyncio
import datetime
import functools
import inspect
import json
import logging
import os
import re
import sys
import threading
import time
import traceback
import uuid
from contextlib import contextmanager
from enum import Enum
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from typing import Any, Callable, Dict, List, Optional, Set, TypeVar, Union, cast

# Import existing logger if available, otherwise use a placeholder
try:
    from app.utils.logging import CorrelationContext
    from app.utils.logging import get_logger as base_get_logger
except ImportError:
    # Fallback implementation if the existing logger is not available
    class CorrelationContext:
        """Thread-local storage for correlation IDs"""

        _context = {}

        @classmethod
        def get_correlation_id(cls) -> str:
            """Get the current correlation ID or generate a new one"""
            if "correlation_id" not in cls._context:
                cls._context["correlation_id"] = str(uuid.uuid4())
            return cls._context["correlation_id"]

        @classmethod
        def set_correlation_id(cls, correlation_id: str) -> None:
            """Set the correlation ID for the current context"""
            cls._context["correlation_id"] = correlation_id

        @classmethod
        def clear_correlation_id(cls) -> None:
            """Clear the correlation ID from the current context"""
            if "correlation_id" in cls._context:
                del cls._context["correlation_id"]

    def base_get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
        """Basic logger factory if the real one is not available"""
        logger = logging.getLogger(name)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger


# Context variables for request tracking
class RequestContext:
    """Thread-local storage for request context"""

    _local = threading.local()

    @classmethod
    def get_request_id(cls) -> Optional[str]:
        """Get the current request ID"""
        return getattr(cls._local, "request_id", None)

    @classmethod
    def set_request_id(cls, request_id: str) -> None:
        """Set the request ID for the current thread"""
        setattr(cls._local, "request_id", request_id)

    @classmethod
    def get_user_id(cls) -> Optional[str]:
        """Get the current user ID"""
        return getattr(cls._local, "user_id", None)

    @classmethod
    def set_user_id(cls, user_id: str) -> None:
        """Set the user ID for the current thread"""
        setattr(cls._local, "user_id", user_id)

    @classmethod
    def get_session_id(cls) -> Optional[str]:
        """Get the current session ID"""
        return getattr(cls._local, "session_id", None)

    @classmethod
    def set_session_id(cls, session_id: str) -> None:
        """Set the session ID for the current thread"""
        setattr(cls._local, "session_id", session_id)

    @classmethod
    def get_context_data(cls) -> Dict[str, Any]:
        """Get all context data for the current thread"""
        return {
            "request_id": cls.get_request_id(),
            "user_id": cls.get_user_id(),
            "session_id": cls.get_session_id(),
            "correlation_id": CorrelationContext.get_correlation_id(),
        }

    @classmethod
    def clear(cls) -> None:
        """Clear all context data for the current thread"""
        if hasattr(cls._local, "request_id"):
            delattr(cls._local, "request_id")
        if hasattr(cls._local, "user_id"):
            delattr(cls._local, "user_id")
        if hasattr(cls._local, "session_id"):
            delattr(cls._local, "session_id")
        CorrelationContext.clear_correlation_id()


class LogLevel(str, Enum):
    """Log levels with standardized names"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(str, Enum):
    """Standardized log categories for organization"""

    REQUEST = "REQUEST"
    RESPONSE = "RESPONSE"
    ERROR = "ERROR"
    AUDIT = "AUDIT"
    PERFORMANCE = "PERFORMANCE"
    SECURITY = "SECURITY"
    DATABASE = "DATABASE"
    CACHE = "CACHE"
    INTEGRATION = "INTEGRATION"
    SYSTEM = "SYSTEM"


class EnhancedJSONFormatter(logging.Formatter):
    """Enhanced JSON formatter with support for complex objects and context data"""

    # Fields to redact (PII and sensitive data)
    SENSITIVE_FIELDS = {
        "password",
        "token",
        "api_key",
        "secret",
        "credit_card",
        "social_security",
        "ssn",
        "auth",
        "bearer",
    }

    # Regex patterns for PII detection
    PII_PATTERNS = [
        # Credit card numbers
        re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
        # Social security numbers
        re.compile(r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b"),
        # Email addresses
        re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
    ]

    def __init__(self, redact_pii: bool = True, include_traceback: bool = True):
        """
        Initialize formatter

        Args:
            redact_pii: Whether to redact PII from logs
            include_traceback: Whether to include traceback in error logs
        """
        super().__init__()
        self.redact_pii = redact_pii
        self.include_traceback = include_traceback

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        # Base log data
        timestamp = self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S.%fZ")
        log_data = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }

        # Add request context if available
        request_id = getattr(record, "request_id", RequestContext.get_request_id())
        if request_id:
            log_data["request_id"] = request_id

        user_id = getattr(record, "user_id", RequestContext.get_user_id())
        if user_id:
            log_data["user_id"] = user_id

        session_id = getattr(record, "session_id", RequestContext.get_session_id())
        if session_id:
            log_data["session_id"] = session_id

        correlation_id = getattr(
            record, "correlation_id", CorrelationContext.get_correlation_id()
        )
        if correlation_id:
            log_data["correlation_id"] = correlation_id

        # Add log category if available
        category = getattr(record, "category", None)
        if category:
            log_data["category"] = category

        # Add exception info if available
        if record.exc_info and self.include_traceback:
            exception_type = (
                record.exc_info[0].__name__ if record.exc_info[0] else "Unknown"
            )
            exception_value = str(record.exc_info[1]) if record.exc_info[1] else ""
            formatted_traceback = (
                self.formatException(record.exc_info) if record.exc_info else ""
            )

            log_data["exception"] = {
                "type": exception_type,
                "message": exception_value,
                "traceback": formatted_traceback,
            }

        # Add any extra attributes from the record
        for key, value in record.__dict__.items():
            if key not in {
                "args",
                "asctime",
                "created",
                "exc_info",
                "exc_text",
                "filename",
                "funcName",
                "id",
                "levelname",
                "levelno",
                "lineno",
                "module",
                "msecs",
                "message",
                "msg",
                "name",
                "pathname",
                "process",
                "processName",
                "relativeCreated",
                "stack_info",
                "thread",
                "threadName",
                "request_id",
                "user_id",
                "session_id",
                "correlation_id",
                "category",
            }:
                if key == "extra" and isinstance(value, dict):
                    # If there's an 'extra' dict, add its contents directly
                    for extra_key, extra_value in value.items():
                        log_data[extra_key] = extra_value
                else:
                    # Add other custom attributes
                    log_data[key] = value

        # Redact PII if enabled
        if self.redact_pii:
            log_data = self._redact_sensitive_data(log_data)

        try:
            return json.dumps(log_data, default=self._json_serializer)
        except Exception as e:
            # If serialization fails, create a simpler version that will definitely serialize
            return json.dumps(
                {
                    "timestamp": timestamp,
                    "level": record.levelname,
                    "logger": record.name,
                    "message": f"Error serializing log: {str(e)}",
                    "original_message": str(record.getMessage()),
                }
            )

    def _json_serializer(self, obj: Any) -> Any:
        """Custom JSON serializer for handling non-serializable objects"""
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        elif isinstance(obj, Exception):
            return str(obj)
        elif isinstance(obj, set):
            return list(obj)
        elif hasattr(obj, "__dict__"):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}
        elif hasattr(obj, "__str__"):
            return str(obj)
        return repr(obj)

    def _redact_sensitive_data(self, data: Any) -> Any:
        """Recursively redact sensitive information from log data"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Check if the key contains sensitive information
                if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                    result[key] = "[REDACTED]"
                else:
                    # Recursively check the value
                    result[key] = self._redact_sensitive_data(value)
            return result
        elif isinstance(data, list):
            return [self._redact_sensitive_data(item) for item in data]
        elif isinstance(data, str):
            # Check for PII patterns in strings
            for pattern in self.PII_PATTERNS:
                data = pattern.sub("[REDACTED]", data)
            return data
        else:
            return data


class EnhancedLogger:
    """
    Enhanced logger that wraps a standard logger with additional functionality

    This class provides structured logging methods with standardized formats,
    context data, and additional metadata for better organization and searchability.
    """

    def __init__(self, logger: logging.Logger):
        """
        Initialize with a standard logger

        Args:
            logger: Standard Python logger to wrap
        """
        self._logger = logger
        self._sampling_rates = {}  # Endpoint -> sample rate mapping

    def set_sampling_rate(self, endpoint: str, rate: float) -> None:
        """
        Set sampling rate for an endpoint (0.0 - 1.0)

        Args:
            endpoint: Endpoint path to set sampling for
            rate: Sampling rate (0.0 = log nothing, 1.0 = log everything)
        """
        if rate < 0.0 or rate > 1.0:
            raise ValueError("Sampling rate must be between 0.0 and 1.0")
        self._sampling_rates[endpoint] = rate

    def should_sample(self, endpoint: Optional[str] = None) -> bool:
        """
        Determine if a log entry should be sampled based on endpoint

        Args:
            endpoint: Optional endpoint to check sampling rate for

        Returns:
            True if the log should be included, False if it should be dropped
        """
        if endpoint is None:
            return True

        sample_rate = self._sampling_rates.get(endpoint, 1.0)
        if sample_rate >= 1.0:
            return True
        elif sample_rate <= 0.0:
            return False

        # Deterministic sampling based on endpoint to ensure consistent sampling
        # of related logs
        return hash(endpoint) % 100 < sample_rate * 100

    def debug(
        self, message: str, category: Optional[LogCategory] = None, **kwargs
    ) -> None:
        """
        Log a debug message

        Args:
            message: Log message
            category: Optional log category
            **kwargs: Additional log data
        """
        endpoint = kwargs.get("endpoint")
        if not self.should_sample(endpoint):
            return

        extra = kwargs.get("extra", {})
        if category:
            extra["category"] = (
                category.value if isinstance(category, LogCategory) else category
            )
        extra.update(RequestContext.get_context_data())

        self._logger.debug(message, extra=extra)

    def info(
        self, message: str, category: Optional[LogCategory] = None, **kwargs
    ) -> None:
        """
        Log an info message

        Args:
            message: Log message
            category: Optional log category
            **kwargs: Additional log data
        """
        endpoint = kwargs.get("endpoint")
        if not self.should_sample(endpoint):
            return

        extra = kwargs.get("extra", {})
        if category:
            extra["category"] = (
                category.value if isinstance(category, LogCategory) else category
            )
        extra.update(RequestContext.get_context_data())

        self._logger.info(message, extra=extra)

    def warning(
        self, message: str, category: Optional[LogCategory] = None, **kwargs
    ) -> None:
        """
        Log a warning message

        Args:
            message: Log message
            category: Optional log category
            **kwargs: Additional log data
        """
        endpoint = kwargs.get("endpoint")
        if not self.should_sample(endpoint):
            return

        extra = kwargs.get("extra", {})
        if category:
            extra["category"] = (
                category.value if isinstance(category, LogCategory) else category
            )
        extra.update(RequestContext.get_context_data())

        self._logger.warning(message, extra=extra)

    def error(
        self,
        message: str,
        exc_info: Optional[Exception] = None,
        category: Optional[LogCategory] = None,
        **kwargs,
    ) -> None:
        """
        Log an error message

        Args:
            message: Error message
            exc_info: Optional exception object
            category: Optional log category
            **kwargs: Additional log data
        """
        # Don't sample errors - always log them
        extra = kwargs.get("extra", {})
        if category:
            extra["category"] = (
                category.value if isinstance(category, LogCategory) else category
            )
        extra.update(RequestContext.get_context_data())

        if exc_info:
            self._logger.error(message, exc_info=exc_info, extra=extra)
        else:
            self._logger.error(message, extra=extra)

    def critical(
        self,
        message: str,
        exc_info: Optional[Exception] = None,
        category: Optional[LogCategory] = None,
        **kwargs,
    ) -> None:
        """
        Log a critical message

        Args:
            message: Critical error message
            exc_info: Optional exception object
            category: Optional log category
            **kwargs: Additional log data
        """
        # Don't sample critical errors - always log them
        extra = kwargs.get("extra", {})
        if category:
            extra["category"] = (
                category.value if isinstance(category, LogCategory) else category
            )
        extra.update(RequestContext.get_context_data())

        if exc_info:
            self._logger.critical(message, exc_info=exc_info, extra=extra)
        else:
            self._logger.critical(message, extra=extra)

    def request(
        self,
        method: str,
        path: str,
        status_code: Optional[int] = None,
        duration_ms: Optional[float] = None,
        **kwargs,
    ) -> None:
        """
        Log a request with standardized format

        Args:
            method: HTTP method
            path: Request path
            status_code: Optional HTTP status code
            duration_ms: Optional request duration in milliseconds
            **kwargs: Additional request data
        """
        if not self.should_sample(path):
            return

        extra = kwargs.get("extra", {})
        extra.update(RequestContext.get_context_data())
        extra.update(
            {
                "category": LogCategory.REQUEST.value,
                "http_method": method,
                "path": path,
            }
        )

        if status_code is not None:
            extra["status_code"] = status_code

        if duration_ms is not None:
            extra["duration_ms"] = duration_ms

        # Add client details if provided
        client_ip = kwargs.get("client_ip")
        if client_ip:
            extra["client_ip"] = client_ip

        # Add request size if provided
        request_size = kwargs.get("request_size")
        if request_size:
            extra["request_size"] = request_size

        # Log headers if provided (and configured to log them)
        headers = kwargs.get("headers")
        if headers and os.environ.get("LOG_HEADERS", "false").lower() == "true":
            # Filter out sensitive headers
            filtered_headers = {}
            for header, value in headers.items():
                header_lower = header.lower()
                if any(
                    sensitive in header_lower
                    for sensitive in EnhancedJSONFormatter.SENSITIVE_FIELDS
                ):
                    filtered_headers[header] = "[REDACTED]"
                else:
                    filtered_headers[header] = value
            extra["headers"] = filtered_headers

        message = f"{method} {path}"
        if status_code is not None:
            message += f" {status_code}"
        if duration_ms is not None:
            message += f" ({duration_ms:.2f}ms)"

        self._logger.info(message, extra=extra)

    def response(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: Optional[float] = None,
        **kwargs,
    ) -> None:
        """
        Log a response with standardized format

        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            duration_ms: Optional request duration in milliseconds
            **kwargs: Additional response data
        """
        if not self.should_sample(path):
            return

        extra = kwargs.get("extra", {})
        extra.update(RequestContext.get_context_data())
        extra.update(
            {
                "category": LogCategory.RESPONSE.value,
                "http_method": method,
                "path": path,
                "status_code": status_code,
            }
        )

        if duration_ms is not None:
            extra["duration_ms"] = duration_ms

        # Add response size if provided
        response_size = kwargs.get("response_size")
        if response_size:
            extra["response_size"] = response_size

        message = f"{method} {path} {status_code}"
        if duration_ms is not None:
            message += f" ({duration_ms:.2f}ms)"

        # Log at appropriate level based on status code
        if status_code >= 500:
            self._logger.error(message, extra=extra)
        elif status_code >= 400:
            self._logger.warning(message, extra=extra)
        else:
            self._logger.info(message, extra=extra)

    def performance(self, operation: str, duration_ms: float, **kwargs) -> None:
        """
        Log performance metrics with standardized format

        Args:
            operation: Name of the operation being measured
            duration_ms: Duration in milliseconds
            **kwargs: Additional performance data
        """
        extra = kwargs.get("extra", {})
        extra.update(RequestContext.get_context_data())
        extra.update(
            {
                "category": LogCategory.PERFORMANCE.value,
                "operation": operation,
                "duration_ms": duration_ms,
            }
        )

        # Add resource usage if provided
        cpu_percent = kwargs.get("cpu_percent")
        if cpu_percent is not None:
            extra["cpu_percent"] = cpu_percent

        memory_mb = kwargs.get("memory_mb")
        if memory_mb is not None:
            extra["memory_mb"] = memory_mb

        self._logger.info(
            f"Performance: {operation} took {duration_ms:.2f}ms", extra=extra
        )

    def audit(
        self,
        action: str,
        status: str = "success",
        resource: Optional[str] = None,
        user_id: Optional[str] = None,
        **kwargs,
    ) -> None:
        """
        Log an audit event with standardized format

        Args:
            action: The action being performed
            status: Status of the action (success/failure)
            resource: Optional resource being acted upon
            user_id: Optional ID of the user performing the action
            **kwargs: Additional audit data
        """
        extra = kwargs.get("extra", {})
        extra.update(RequestContext.get_context_data())

        # Override user_id if explicitly provided
        if user_id:
            extra["user_id"] = user_id

        extra.update(
            {
                "category": LogCategory.AUDIT.value,
                "action": action,
                "status": status,
            }
        )

        if resource:
            extra["resource"] = resource

        self._logger.info(f"Audit: {action} {status}", extra=extra)

    def security(self, event: str, severity: str = "info", **kwargs) -> None:
        """
        Log a security event with standardized format

        Args:
            event: Security event description
            severity: Event severity (info/warning/critical)
            **kwargs: Additional security data
        """
        extra = kwargs.get("extra", {})
        extra.update(RequestContext.get_context_data())
        extra.update(
            {
                "category": LogCategory.SECURITY.value,
                "security_event": event,
                "severity": severity,
            }
        )

        # Map severity to log level
        if severity == "critical":
            self._logger.critical(f"Security: {event}", extra=extra)
        elif severity == "warning":
            self._logger.warning(f"Security: {event}", extra=extra)
        else:
            self._logger.info(f"Security: {event}", extra=extra)

    def exception(
        self, message: str, category: Optional[LogCategory] = None, **kwargs
    ) -> None:
        """
        Log an exception with current exception info

        Args:
            message: Error message
            category: Optional log category
            **kwargs: Additional log data
        """
        extra = kwargs.get("extra", {})
        if category:
            extra["category"] = (
                category.value if isinstance(category, LogCategory) else category
            )
        extra.update(RequestContext.get_context_data())

        self._logger.exception(message, extra=extra)


# Generic type for functions
F = TypeVar("F", bound=Callable[..., Any])


def with_request_context(func: F) -> F:
    """
    Decorator to set request context for a function

    Args:
        func: Function to decorate

    Returns:
        Decorated function with request context handling
    """

    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        # Extract request from positional or keyword arguments
        request = None
        for arg in args:
            if hasattr(arg, "headers") and hasattr(arg, "client"):
                request = arg
                break

        if not request and "request" in kwargs:
            request = kwargs["request"]

        if request:
            # Extract request ID from headers or generate a new one
            request_id = request.headers.get("X-Request-ID")
            if not request_id:
                request_id = str(uuid.uuid4())

            # Set request context
            RequestContext.set_request_id(request_id)

            # Extract user ID from request if available
            if hasattr(request, "state") and hasattr(request.state, "user_id"):
                RequestContext.set_user_id(request.state.user_id)

            # Extract session ID from request if available
            session_id = request.cookies.get("session_id")
            if session_id:
                RequestContext.set_session_id(session_id)

        try:
            return await func(*args, **kwargs)
        finally:
            # Clear request context
            RequestContext.clear()

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        # Extract request from positional or keyword arguments
        request = None
        for arg in args:
            if hasattr(arg, "headers") and hasattr(arg, "client"):
                request = arg
                break

        if not request and "request" in kwargs:
            request = kwargs["request"]

        if request:
            # Extract request ID from headers or generate a new one
            request_id = request.headers.get("X-Request-ID")
            if not request_id:
                request_id = str(uuid.uuid4())

            # Set request context
            RequestContext.set_request_id(request_id)

            # Extract user ID from request if available
            if hasattr(request, "state") and hasattr(request.state, "user_id"):
                RequestContext.set_user_id(request.state.user_id)

            # Extract session ID from request if available
            session_id = request.cookies.get("session_id")
            if session_id:
                RequestContext.set_session_id(session_id)

        try:
            return func(*args, **kwargs)
        finally:
            # Clear request context
            RequestContext.clear()

    # Choose appropriate wrapper based on whether the function is async
    if asyncio.iscoroutinefunction(func):
        return cast(F, async_wrapper)
    return cast(F, sync_wrapper)


def with_performance_logging(
    operation: Optional[str] = None, logger: Optional[EnhancedLogger] = None
):
    """
    Decorator to log the performance of a function

    Args:
        operation: Optional name for the operation (defaults to function name)
        logger: Optional logger to use (defaults to creating a new one)

    Returns:
        Decorated function with performance logging
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create or use provided logger
            nonlocal logger
            if not logger:
                base_logger = base_get_logger(func.__module__)
                logger = EnhancedLogger(base_logger)

            # Get operation name
            op_name = operation or func.__qualname__

            # Start timing
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                # Log performance
                duration_ms = (time.time() - start_time) * 1000
                logger.performance(op_name, duration_ms)
                return result
            except Exception as e:
                # Log performance with error flag
                duration_ms = (time.time() - start_time) * 1000
                logger.performance(
                    op_name, duration_ms, extra={"error": True, "exception": str(e)}
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create or use provided logger
            nonlocal logger
            if not logger:
                base_logger = base_get_logger(func.__module__)
                logger = EnhancedLogger(base_logger)

            # Get operation name
            op_name = operation or func.__qualname__

            # Start timing
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                # Log performance
                duration_ms = (time.time() - start_time) * 1000
                logger.performance(op_name, duration_ms)
                return result
            except Exception as e:
                # Log performance with error flag
                duration_ms = (time.time() - start_time) * 1000
                logger.performance(
                    op_name, duration_ms, extra={"error": True, "exception": str(e)}
                )
                raise

        # Choose appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)

    return decorator


@contextmanager
def performance_timing(operation: str, logger: EnhancedLogger):
    """
    Context manager for timing operations

    Args:
        operation: Name of the operation being timed
        logger: Logger to use for logging
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        logger.performance(operation, duration_ms)


def configure_logging(
    app_name: str,
    log_level: str = "INFO",
    log_dir: str = "logs",
    enable_json_logging: bool = True,
    console_output: bool = True,
    log_file_output: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_handlers: Optional[List[logging.Handler]] = None,
) -> None:
    """
    Configure logging for the application

    Args:
        app_name: Application name for logger
        log_level: Default log level
        log_dir: Directory for log files
        enable_json_logging: Whether to use JSON formatting
        console_output: Whether to output logs to console
        log_file_output: Whether to output logs to files
        max_bytes: Max size per log file before rotation
        backup_count: Number of backup log files to keep
        log_handlers: Optional list of additional log handlers
    """
    # Create log directory if it doesn't exist
    if log_file_output:
        os.makedirs(log_dir, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()

    # Set log level
    log_level_num = getattr(logging, log_level.upper(), logging.INFO)
    root_logger.setLevel(log_level_num)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create formatter
    if enable_json_logging:
        formatter = EnhancedJSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    # Add console handler if enabled
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Add file handlers if enabled
    if log_file_output:
        # Create loggers for different log types
        handlers = {}
        log_types = [
            ("app", f"{app_name}.log"),
            ("error", f"{app_name}_error.log"),
            ("request", f"{app_name}_request.log"),
            ("performance", f"{app_name}_performance.log"),
            ("security", f"{app_name}_security.log"),
        ]

        for log_type, filename in log_types:
            file_handler = RotatingFileHandler(
                os.path.join(log_dir, filename),
                maxBytes=max_bytes,
                backupCount=backup_count,
            )
            file_handler.setFormatter(formatter)

            # Set specific log levels for different log types
            if log_type == "error":
                file_handler.setLevel(logging.ERROR)
            else:
                file_handler.setLevel(log_level_num)

            # Add filter for log categories
            if log_type != "app":  # App log gets everything

                def category_filter(record, category=log_type.upper()):
                    # Check if record has category attribute matching the log type
                    return hasattr(record, "category") and record.category == category

                file_handler.addFilter(category_filter)

            root_logger.addHandler(file_handler)
            handlers[log_type] = file_handler

    # Add any additional handlers
    if log_handlers:
        for handler in log_handlers:
            root_logger.addHandler(handler)

    # Log configuration
    logging.info(f"Logging configured for {app_name} at level {log_level}")


def get_enhanced_logger(name: str, log_file: Optional[str] = None) -> EnhancedLogger:
    """
    Get an enhanced logger with the specified name

    Args:
        name: Logger name
        log_file: Optional log file path

    Returns:
        Enhanced logger instance
    """
    logger = base_get_logger(name, log_file)
    return EnhancedLogger(logger)


class LoggingMiddleware:
    """ASGI middleware for request logging"""

    def __init__(self, app, logger: Optional[EnhancedLogger] = None):
        """
        Initialize logging middleware

        Args:
            app: ASGI application
            logger: Optional logger to use (creates one if not provided)
        """
        self.app = app
        self.logger = logger or get_enhanced_logger("request")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Get request info
        path = scope.get("path", "")
        method = scope.get("method", "UNKNOWN")

        # Check if this endpoint should be sampled
        if not self.logger.should_sample(path):
            # Just pass through to the app without logging
            return await self.app(scope, receive, send)

        # Generate or extract request ID
        headers = dict(scope.get("headers", []))
        request_id = None
        if b"x-request-id" in headers:
            request_id = headers[b"x-request-id"].decode("utf-8")
        else:
            request_id = str(uuid.uuid4())

        # Set request context
        RequestContext.set_request_id(request_id)

        # Get client info
        client = scope.get("client")
        client_host = client[0] if client else "unknown"

        # Log request
        self.logger.request(
            method,
            path,
            client_ip=client_host,
            headers={k.decode("utf-8"): v.decode("utf-8") for k, v in headers.items()},
        )

        # Track response info
        start_time = time.time()
        response_status = 500  # Default to error status
        response_headers = []

        # Custom send function to capture response info
        async def wrapped_send(message):
            nonlocal response_status, response_headers

            if message["type"] == "http.response.start":
                response_status = message["status"]
                response_headers = message.get("headers", [])

                # Add request ID to response headers
                response_headers.append((b"X-Request-ID", request_id.encode("utf-8")))
                message["headers"] = response_headers

            return await send(message)

        try:
            await self.app(scope, receive, wrapped_send)
        except Exception as e:
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log error
            self.logger.error(
                f"Error processing request: {method} {path}",
                exc_info=e,
                extra={
                    "duration_ms": duration_ms,
                    "path": path,
                    "method": method,
                },
            )

            # Re-raise the exception
            raise
        finally:
            # Calculate request duration
            duration_ms = (time.time() - start_time) * 1000

            # Log response
            self.logger.response(
                method,
                path,
                response_status,
                duration_ms=duration_ms,
            )

            # Clear request context
            RequestContext.clear()


def setup_structured_logging_middleware(app):
    """
    Set up structured logging middleware for a FastAPI application

    Args:
        app: FastAPI application
    """
    # Initialize enhanced logger
    logger = get_enhanced_logger("request", "logs/requests.log")

    # Set sampling rates for high-volume endpoints
    logger.set_sampling_rate("/api/analyze", 0.1)  # Sample 10% of analyze requests
    logger.set_sampling_rate("/health", 0.01)  # Sample 1% of health checks

    # Instead of adding middleware directly, add it to app's state
    # so it can be added at the right time in the initialization flow
    if not hasattr(app, "state"):
        app.state = type("obj", (object,), {})

    app.state.structured_logging_logger = logger

    return app


def apply_structured_logging_middleware(app):
    """
    Apply the structured logging middleware to the FastAPI application.
    This should be called before the application starts.

    Args:
        app: FastAPI application
    """
    if hasattr(app, "state") and hasattr(app.state, "structured_logging_logger"):
        logger = app.state.structured_logging_logger
        app.add_middleware(LoggingMiddleware, logger=logger)
    else:
        # If logger wasn't properly initialized, create a new one
        logger = get_enhanced_logger("request", "logs/requests.log")
        app.add_middleware(LoggingMiddleware, logger=logger)

    return app
