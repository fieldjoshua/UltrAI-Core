"""
Structured logging configuration for the UltraAI backend.

This module provides a centralized logging configuration with:
- Log formatting with timestamps, log levels, and structured data
- Log rotation based on file size with automatic archiving
- Separate handling for different log types (request, error, audit)
- Correlation ID tracking across services
- Environment-specific logging configurations
"""

import json
import logging
import logging.handlers
import os
import sys
import time
import uuid
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, Optional

# Create logs directory if it doesn't exist
logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

# Log file paths
REQUEST_LOG = logs_dir / "requests.log"
ERROR_LOG = logs_dir / "errors.log"
AUDIT_LOG = logs_dir / "audit.log"
PERFORMANCE_LOG = logs_dir / "performance.log"

# Maximum log file size (10MB)
MAX_LOG_SIZE = 10 * 1024 * 1024
# Number of backup files to keep
BACKUP_COUNT = 5


# Correlation ID context
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


class StructuredLogFormatter(logging.Formatter):
    """Formatter that outputs JSON formatted logs"""

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record as a JSON string"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": getattr(
                record, "correlation_id", CorrelationContext.get_correlation_id()
            ),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if available
        if record.exc_info and record.exc_info[0]:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": self.formatException(record.exc_info),
            }

        # Add extra fields from record
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


class CorrelationFilter(logging.Filter):
    """Filter that adds correlation ID to log records"""

    def filter(self, record):
        """Add correlation ID to the log record"""
        if not hasattr(record, "correlation_id"):
            record.correlation_id = CorrelationContext.get_correlation_id()
        return True


def get_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Get a configured logger with the specified name and optional log file

    Args:
        name: Name of the logger
        log_file: Optional path to a log file

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Environment-specific configuration
    env = os.environ.get("ENVIRONMENT", "development")
    if env == "production":
        logger.setLevel(logging.WARNING)
    elif env == "development":
        logger.setLevel(logging.DEBUG)

    # Add correlation ID filter
    logger.addFilter(CorrelationFilter())

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(StructuredLogFormatter())
    logger.addHandler(console_handler)

    # File handler with rotation (if log_file is specified)
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
        )
        file_handler.setFormatter(StructuredLogFormatter())
        logger.addHandler(file_handler)

    return logger


# Create specialized loggers
request_logger = get_logger("request", REQUEST_LOG)
error_logger = get_logger("error", ERROR_LOG)
audit_logger = get_logger("audit", AUDIT_LOG)
performance_logger = get_logger("performance", PERFORMANCE_LOG)


def log_request(request_data: Dict[str, Any]) -> None:
    """
    Log a request with standardized format

    Args:
        request_data: Request data to log
    """
    request_logger.info("API Request", extra={"request": request_data})


def log_error(
    message: str,
    error: Optional[Exception] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log an error with standardized format

    Args:
        message: Error message
        error: Optional exception object
        extra: Optional extra data to include in the log
    """
    log_data = extra or {}
    log_data["error_message"] = message

    if error:
        error_logger.error(message, exc_info=error, extra=log_data)
    else:
        error_logger.error(message, extra=log_data)


def log_audit(
    action: str,
    user_id: Optional[str] = None,
    resource: Optional[str] = None,
    status: str = "success",
    details: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log an audit event with standardized format

    Args:
        action: The action being performed
        user_id: Optional ID of the user performing the action
        resource: Optional resource being acted upon
        status: Status of the action (success/failure)
        details: Optional details about the action
    """
    log_data = {
        "action": action,
        "status": status,
    }

    if user_id:
        log_data["user_id"] = user_id

    if resource:
        log_data["resource"] = resource

    if details:
        log_data["details"] = details

    audit_logger.info(f"Audit: {action}", extra=log_data)


def log_performance(
    operation: str, duration_ms: float, metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log performance metrics with standardized format

    Args:
        operation: Name of the operation being measured
        duration_ms: Duration in milliseconds
        metadata: Optional metadata about the operation
    """
    log_data = {
        "operation": operation,
        "duration_ms": duration_ms,
    }

    if metadata:
        log_data["metadata"] = metadata

    performance_logger.info(
        f"Performance: {operation} took {duration_ms:.2f}ms", extra=log_data
    )


def with_performance_logging(operation: str = None):
    """
    Decorator to log the performance of a function

    Args:
        operation: Optional name for the operation (defaults to function name)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            operation_name = operation or func.__name__
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                log_performance(operation_name, duration_ms)
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                log_performance(operation_name, duration_ms, {"error": str(e)})
                raise

        return wrapper

    return decorator


def with_correlation_id(correlation_id: Optional[str] = None):
    """
    Decorator to set a correlation ID for a function call

    Args:
        correlation_id: Optional correlation ID to use (generates new one if not provided)
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_id = correlation_id or str(uuid.uuid4())
            previous_id = (
                CorrelationContext.get_correlation_id()
                if "correlation_id" in CorrelationContext._context
                else None
            )
            try:
                CorrelationContext.set_correlation_id(current_id)
                return func(*args, **kwargs)
            finally:
                if previous_id:
                    CorrelationContext.set_correlation_id(previous_id)
                else:
                    CorrelationContext.clear_correlation_id()

        return wrapper

    return decorator
