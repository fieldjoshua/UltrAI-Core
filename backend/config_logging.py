"""Logging configuration for production environment."""

import os
import sys
from pathlib import Path
from typing import Dict, Optional

import structlog


def get_log_level() -> str:
    """Get log level from environment."""
    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    valid_levels = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]
    return level if level in valid_levels else "INFO"


def get_logging_config() -> Dict[str, any]:
    """Get logging configuration for production."""
    config = {
        "level": get_log_level(),
        "format": os.environ.get("LOG_FORMAT", "json"),  # json or text
        "output": os.environ.get("LOG_OUTPUT", "file"),  # file, stdout, both
        "file_path": os.environ.get("LOG_FILE_PATH", "/var/log/ultra/production.log"),
        "max_file_size": int(os.environ.get("LOG_MAX_FILE_SIZE", "10485760")),  # 10MB
        "backup_count": int(os.environ.get("LOG_BACKUP_COUNT", "5")),
        "enable_metrics": os.environ.get("ENABLE_METRICS", "true").lower() == "true",
        "enable_tracing": os.environ.get("ENABLE_TRACING", "false").lower() == "true",
    }
    
    # Sentry configuration
    config["sentry_dsn"] = os.environ.get("SENTRY_DSN", "")
    config["sentry_environment"] = os.environ.get("ENVIRONMENT", "production")
    config["sentry_traces_sample_rate"] = float(
        os.environ.get("SENTRY_TRACES_SAMPLE_RATE", "0.1")
    )
    
    return config


def setup_production_logging(config: Dict[str, any]) -> None:
    """Setup production logging with structured logging."""
    
    # Create log directory if it doesn't exist
    if config["output"] in ["file", "both"]:
        log_dir = Path(config["file_path"]).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    # Setup structlog processors
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]
    
    # Add call site information in debug mode
    if config["level"] == "DEBUG":
        processors.append(structlog.processors.CallsiteParameterAdder())
    
    # Format based on configuration
    if config["format"] == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Setup standard library logging
    import logging.config
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
            },
            "verbose": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": config["level"],
                "formatter": "json" if config["format"] == "json" else "verbose",
                "stream": sys.stdout,
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": config["level"],
                "formatter": "json",
                "filename": config["file_path"],
                "maxBytes": config["max_file_size"],
                "backupCount": config["backup_count"],
            },
        },
        "root": {
            "level": config["level"],
            "handlers": [],
        },
        "loggers": {
            "ultra": {
                "level": config["level"],
                "handlers": [],
                "propagate": True,
            },
            "backend": {
                "level": config["level"],
                "handlers": [],
                "propagate": True,
            },
            "uvicorn": {
                "level": config["level"],
                "handlers": [],
                "propagate": True,
            },
            "fastapi": {
                "level": config["level"],
                "handlers": [],
                "propagate": True,
            },
        },
    }
    
    # Setup handlers based on output configuration
    handlers = []
    if config["output"] in ["stdout", "both"]:
        handlers.append("console")
    if config["output"] in ["file", "both"]:
        handlers.append("file")
    
    # Apply handlers to all loggers
    logging_config["root"]["handlers"] = handlers
    for logger_name in logging_config["loggers"]:
        logging_config["loggers"][logger_name]["handlers"] = handlers
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Setup Sentry if configured
    if config["sentry_dsn"]:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.logging import LoggingIntegration
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            
            sentry_logging = LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            )
            
            sentry_sdk.init(
                dsn=config["sentry_dsn"],
                environment=config["sentry_environment"],
                integrations=[
                    sentry_logging,
                    FastApiIntegration(transaction_style="endpoint"),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=config["sentry_traces_sample_rate"],
                send_default_pii=True,
            )
            
            logging.info("Sentry error tracking initialized")
        except ImportError:
            logging.warning("Sentry SDK not installed, error tracking disabled")
        except Exception as e:
            logging.error(f"Failed to initialize Sentry: {str(e)}")


def get_logger(name: str, log_file: Optional[str] = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)