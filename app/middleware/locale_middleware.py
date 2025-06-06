"""Middleware for extracting and managing locale information from requests."""

from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from backend.utils.logging import get_logger
from backend.utils.user_messages import Locale

logger = get_logger(__name__)


class LocaleMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and set locale information from requests."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Extract locale from request headers and set in request state."""
        # Get locale from Accept-Language header
        accept_language = request.headers.get("Accept-Language", "en-US")

        # Parse the primary locale
        locale_str = self._parse_accept_language(accept_language)

        # Convert to our Locale enum if valid
        locale = self._validate_locale(locale_str)

        # Store in request state
        request.state.locale = locale

        logger.debug(f"Request locale set to: {locale}")

        # Process request
        response = await call_next(request)

        # Add Content-Language header to response
        response.headers["Content-Language"] = locale

        return response

    def _parse_accept_language(self, accept_language: str) -> str:
        """Parse Accept-Language header to extract primary locale."""
        # Accept-Language format: "en-US,en;q=0.9,es;q=0.8"
        if not accept_language:
            return "en-US"

        # Split by comma and take the first one
        languages = accept_language.split(",")
        if not languages:
            return "en-US"

        # Get the first language
        primary = languages[0].split(";")[0].strip()

        # Convert to our format (e.g., "en-US" -> "en_US")
        return primary.replace("-", "_")

    def _validate_locale(self, locale_str: str) -> str:
        """Validate locale string and return valid Locale or default."""
        try:
            # Check if it's a valid locale
            locale_enum = Locale(locale_str)
            return locale_str
        except ValueError:
            # Try to match by language code only
            language_code = locale_str.split("_")[0].lower()

            # Map common language codes to our supported locales
            language_mapping = {
                "en": Locale.EN_US,
                "es": Locale.ES_ES,
                "fr": Locale.FR_FR,
                "de": Locale.DE_DE,
                "ja": Locale.JA_JP,
                "zh": Locale.ZH_CN,
            }

            if language_code in language_mapping:
                return language_mapping[language_code].value

            # Default to English
            return Locale.EN_US.value


def setup_locale_middleware(app):
    """Set up locale middleware for the application."""
    app.add_middleware(LocaleMiddleware)
    logger.info("Locale middleware configured")
