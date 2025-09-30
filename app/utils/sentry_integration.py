"""
Sentry integration for error tracking and performance monitoring.
"""

import os
import logging
from typing import Optional, Dict, Any
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk import set_context, set_tag, set_user, capture_exception, capture_message
from app.config import Config

logger = logging.getLogger(__name__)


def init_sentry() -> bool:
    """
    Initialize Sentry SDK for error tracking and performance monitoring.

    Returns:
        bool: True if Sentry was initialized, False otherwise
    """
    sentry_dsn = os.getenv("SENTRY_DSN")

    if not sentry_dsn:
        logger.info("Sentry DSN not configured, skipping Sentry initialization")
        return False

    try:
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )

        # Initialize Sentry
        sentry_sdk.init(
            dsn=sentry_dsn,
            environment=Config.ENVIRONMENT,
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint",
                    failed_request_status_codes={403, 404, 429, 500, 503}
                ),
                StarletteIntegration(),
                logging_integration,
                SqlalchemyIntegration(),
                HttpxIntegration(),
            ],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
            profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send personally identifiable information
            before_send=before_send_filter,
            before_send_transaction=before_send_transaction_filter,
            debug=Config.DEBUG,
            release=os.getenv("APP_VERSION", "unknown"),
            server_name=os.getenv("SERVER_NAME", "ultrai-backend"),
        )

        logger.info(f"Sentry initialized for environment: {Config.ENVIRONMENT}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def before_send_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter events before sending to Sentry.

    Args:
        event: The event dictionary
        hint: Additional information about the event

    Returns:
        The filtered event or None to drop it
    """
    # Filter out specific errors we don't want to track
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]

        # Don't send rate limit errors
        if exc_type.__name__ == "RateLimitError":
            return None

        # Don't send authentication errors (too noisy)
        if exc_type.__name__ in ["AuthenticationError", "InvalidTokenError"]:
            return None

    # Remove sensitive data from request
    if "request" in event:
        request = event["request"]

        # Remove authorization headers
        if "headers" in request:
            headers = dict(request["headers"])
            for key in ["authorization", "x-api-key", "cookie"]:
                headers.pop(key, None)
            request["headers"] = headers

        # Remove sensitive query params
        if "query_string" in request:
            # Parse and filter query string
            pass

    return event


def before_send_transaction_filter(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter transaction events (performance monitoring).

    Args:
        event: The transaction event
        hint: Additional information

    Returns:
        The filtered event or None to drop it
    """
    # Skip health check transactions
    if event.get("transaction") in ["/health", "/api/health", "/ping"]:
        return None

    # Skip metrics endpoint
    if event.get("transaction") == "/api/metrics":
        return None

    return event


class SentryContextManager:
    """Context manager for Sentry operations."""

    @staticmethod
    def set_user_context(user_id: str, email: Optional[str] = None, username: Optional[str] = None):
        """Set user context for Sentry."""
        set_user({
            "id": user_id,
            "email": email,
            "username": username,
        })

    @staticmethod
    def set_request_context(request_id: str, correlation_id: str, endpoint: str):
        """Set request context for Sentry."""
        set_context("request", {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "endpoint": endpoint,
        })

    @staticmethod
    def set_orchestration_context(
        models: list[str],
        stage: str,
        query_type: str,
        model_count: int
    ):
        """Set orchestration context for Sentry."""
        set_context("orchestration", {
            "models": models,
            "stage": stage,
            "query_type": query_type,
            "model_count": model_count,
        })

        # Also set tags for easier filtering
        set_tag("orchestration.stage", stage)
        set_tag("orchestration.model_count", str(model_count))
        set_tag("orchestration.query_type", query_type)

    @staticmethod
    def capture_model_error(
        model: str,
        error: Exception,
        stage: str,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Capture model-specific errors with context."""
        set_tag("model", model)
        set_tag("error.stage", stage)

        if additional_data:
            set_context("model_error", additional_data)

        capture_exception(error)

    @staticmethod
    def capture_performance_warning(
        message: str,
        duration: float,
        threshold: float,
        stage: str,
        additional_data: Optional[Dict[str, Any]] = None
    ):
        """Capture performance warnings."""
        data = {
            "duration": duration,
            "threshold": threshold,
            "stage": stage,
            "exceeded_by": duration - threshold,
        }

        if additional_data:
            data.update(additional_data)

        set_context("performance", data)
        capture_message(message, level="warning")


# Export convenience functions
sentry_context = SentryContextManager()
