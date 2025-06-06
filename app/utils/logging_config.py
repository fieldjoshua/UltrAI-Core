"""
Logging configuration for the Ultra backend.

This module provides logging configuration for different components.
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

# Log directory
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Log levels
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
RATE_LIMIT_LOG_LEVEL = os.getenv("RATE_LIMIT_LOG_LEVEL", "INFO")
API_LOG_LEVEL = os.getenv("API_LOG_LEVEL", "INFO")
ERROR_LOG_LEVEL = os.getenv("ERROR_LOG_LEVEL", "ERROR")

# Log file sizes and rotation
MAX_BYTES = 10 * 1024 * 1024  # 10MB
BACKUP_COUNT = 5
ROTATION_INTERVAL = "midnight"

# Component-specific log files
LOG_FILES = {
    "api": "api.log",
    "rate_limit": "rate_limit.log",
    "error": "error.log",
    "performance": "performance.log",
    "security": "security.log",
}

# Log formatters
FORMATTERS = {
    "default": logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT),
    "detailed": logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(filename)s:%(lineno)d] - %(message)s",
        datefmt=LOG_DATE_FORMAT,
    ),
    "simple": logging.Formatter("%(levelname)s - %(message)s"),
}


def setup_logger(
    name: str,
    log_file: str,
    level: str = LOG_LEVEL,
    formatter: str = "default",
    rotation: str = "size",
) -> logging.Logger:
    """
    Set up a logger with file and console handlers

    Args:
        name: Logger name
        log_file: Log file path
        level: Log level
        formatter: Formatter to use
        rotation: Rotation type ('size' or 'time')

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create formatter
    formatter_obj = FORMATTERS.get(formatter, FORMATTERS["default"])

    # Create file handler
    if rotation == "size":
        file_handler = RotatingFileHandler(
            os.path.join(LOG_DIR, log_file),
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
        )
    else:
        file_handler = TimedRotatingFileHandler(
            os.path.join(LOG_DIR, log_file),
            when=ROTATION_INTERVAL,
            backupCount=BACKUP_COUNT,
        )

    file_handler.setFormatter(formatter_obj)
    logger.addHandler(file_handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter_obj)
    logger.addHandler(console_handler)

    return logger


# Create component-specific loggers
api_logger = setup_logger("api", LOG_FILES["api"], level=API_LOG_LEVEL)
rate_limit_logger = setup_logger(
    "rate_limit",
    LOG_FILES["rate_limit"],
    level=RATE_LIMIT_LOG_LEVEL,
    formatter="detailed",
)
error_logger = setup_logger(
    "error", LOG_FILES["error"], level=ERROR_LOG_LEVEL, formatter="detailed"
)
performance_logger = setup_logger(
    "performance", LOG_FILES["performance"], level=LOG_LEVEL, formatter="simple"
)
security_logger = setup_logger(
    "security", LOG_FILES["security"], level=LOG_LEVEL, formatter="detailed"
)


# Logging middleware
class LoggingMiddleware:
    """Middleware for logging API requests and responses"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, request, call_next):
        # Log request
        api_logger.info(
            f"Request: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )

        # Process request
        try:
            response = await call_next(request)

            # Log response
            api_logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code}"
            )

            return response
        except Exception as e:
            # Log error
            error_logger.error(
                f"Error processing request: {request.method} {request.url.path} - "
                f"{str(e)}"
            )
            raise
