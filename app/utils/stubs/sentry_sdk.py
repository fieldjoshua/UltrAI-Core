"""
Stub implementation of sentry_sdk for when the real module is not installed.
"""

import logging

logger = logging.getLogger(__name__)
logger.warning("Using stub sentry_sdk module. Error tracking disabled.")


def init(*args, **kwargs):
    logger.info("Stub sentry_sdk.init called with args: %s, kwargs: %s", args, kwargs)


def capture_exception(exc):
    logger.info("Stub sentry_sdk.capture_exception called for exception: %s", exc)
