import logging
import sys
from pathlib import Path
from typing import Any, Dict

from loguru import logger


class InterceptHandler(logging.Handler):
    """Intercept standard logging messages and redirect them to loguru."""

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging(
    log_path: Path = Path("logs"),
    level: str = "INFO",
    rotation: str = "500 MB",
    retention: str = "10 days",
    format: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
) -> None:
    """Configure logging for the application.

    Args:
        log_path: Directory to store log files
        level: Logging level
        rotation: When to rotate log files
        retention: How long to keep log files
        format: Log message format
    """
    # Create logs directory if it doesn't exist
    log_path.mkdir(parents=True, exist_ok=True)

    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format=format,
        level=level,
        colorize=True,
    )

    # Add file handler
    logger.add(
        log_path / "app.log",
        format=format,
        level=level,
        rotation=rotation,
        retention=retention,
        compression="zip",
    )

    # Add error file handler
    logger.add(
        log_path / "error.log",
        format=format,
        level="ERROR",
        rotation=rotation,
        retention=retention,
        compression="zip",
    )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set loguru as the default logger for all libraries
    for name in logging.root.manager.loggerDict:
        logging.getLogger(name).handlers = [InterceptHandler()]

    logger.info("Logging system initialized")


def log_error(
    error: Exception,
    context: Dict[str, Any] = None,
    level: str = "ERROR",
) -> None:
    """Log an error with context.

    Args:
        error: The exception to log
        context: Additional context to include in the log
        level: Logging level
    """
    context = context or {}
    logger.opt(exception=error).log(
        level, "Error occurred: {error}", error=str(error), **context
    )
