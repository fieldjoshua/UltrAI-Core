"""User-friendly error message mappings and localization support."""

from enum import Enum
from typing import Dict, Optional


class Locale(str, Enum):
    """Supported locales for error messages."""

    EN_US = "en_US"
    ES_ES = "es_ES"
    FR_FR = "fr_FR"
    DE_DE = "de_DE"
    JA_JP = "ja_JP"
    ZH_CN = "zh_CN"


class ErrorMessageManager:
    """Manages user-friendly error messages with localization support."""

    def __init__(self, default_locale: Locale = Locale.EN_US):
        self.default_locale = default_locale
        self.messages = self._load_messages()

    def _load_messages(self) -> Dict[str, Dict[str, str]]:
        """Load error message mappings for all locales."""
        return {
            Locale.EN_US: {
                # Authentication errors
                "AUTH_001": "The email or password you entered is incorrect. Please try again.",
                "AUTH_002": "Your session has expired. Please log in again.",
                "AUTH_003": "Invalid authentication token. Please log in again.",
                "AUTH_004": "Your account has been locked. Please contact support.",
                "AUTH_005": "Two-factor authentication required. Please enter your code.",
                # Authorization errors
                "AUTHZ_001": "You don't have permission to perform this action.",
                "AUTHZ_002": "You don't have access to this resource.",
                "AUTHZ_003": "This action is not allowed for your account type.",
                "AUTHZ_004": "Your subscription plan doesn't include this feature.",
                # Validation errors
                "VAL_001": "Please fill in all required fields.",
                "VAL_002": "Please check the format of your input.",
                "VAL_003": "The value you entered is outside the acceptable range.",
                "VAL_004": "This file type is not supported. Please use a supported format.",
                "VAL_005": "The file size exceeds the maximum allowed limit.",
                "VAL_006": "Invalid email address format.",
                "VAL_007": "Password must be at least 8 characters long.",
                # LLM/Model errors
                "LLM_001": "The AI service is temporarily unavailable. Please try again later.",
                "LLM_002": "Too many requests. Please wait a moment before trying again.",
                "LLM_003": "Your message is too long. Please shorten it and try again.",
                "LLM_004": "The selected model is not available. Please choose another.",
                "LLM_005": "The AI service is taking too long to respond. Please try again.",
                "LLM_006": "Content filtered due to safety guidelines. Please modify your request.",
                # System errors
                "SYS_001": "Something went wrong on our end. Please try again later.",
                "SYS_002": "Database service is temporarily unavailable.",
                "SYS_003": "The service is currently overloaded. Please try again in a few minutes.",
                "SYS_004": "System configuration error. Please contact support.",
                "SYS_005": "Maintenance in progress. Service will be back soon.",
                # Network errors
                "NET_001": "Connection timed out. Please check your internet connection.",
                "NET_002": "Network error. Please check your connection and try again.",
                "NET_003": "Secure connection failed. Please try again.",
                "NET_004": "Unable to reach the server. Please try again later.",
                # Business logic errors
                "BUS_001": "This operation cannot be completed at this time.",
                "BUS_002": "Invalid operation for the current state.",
                "BUS_003": "This feature is not yet available.",
                "BUS_004": "Operation cancelled by user.",
                "BUS_005": "Duplicate entry detected. Please use a unique value.",
                # Rate limiting
                "RATE_001": "You've made too many requests. Please wait before trying again.",
                "RATE_002": "Daily limit exceeded. Please try again tomorrow.",
                "RATE_003": "Monthly quota reached. Please upgrade your plan.",
                # Document/File errors
                "DOC_001": "Document not found. It may have been moved or deleted.",
                "DOC_002": "Unable to process this document format.",
                "DOC_003": "Document is too large. Maximum size is 50MB.",
                "DOC_004": "Document processing failed. Please try a different file.",
                "DOC_005": "Document is corrupted or invalid.",
                # Payment errors
                "PAY_001": "Payment failed. Please check your payment method.",
                "PAY_002": "Insufficient funds. Please add funds or use a different method.",
                "PAY_003": "Card declined. Please contact your bank or use another card.",
                "PAY_004": "Subscription required. Please subscribe to access this feature.",
                "PAY_005": "Payment processing error. Please try again later.",
            },
            Locale.ES_ES: {
                # Spanish translations
                "AUTH_001": "El correo o contraseña que ingresaste es incorrecto. Por favor, inténtalo de nuevo.",
                "AUTH_002": "Tu sesión ha expirado. Por favor, inicia sesión nuevamente.",
                "AUTH_003": "Token de autenticación inválido. Por favor, inicia sesión nuevamente.",
                "AUTHZ_001": "No tienes permiso para realizar esta acción.",
                "VAL_001": "Por favor, completa todos los campos obligatorios.",
                "LLM_001": "El servicio de IA no está disponible temporalmente. Por favor, inténtalo más tarde.",
                "SYS_001": "Algo salió mal de nuestro lado. Por favor, inténtalo más tarde.",
                "NET_001": "Tiempo de conexión agotado. Por favor, verifica tu conexión a internet.",
                # Add more Spanish translations as needed
            },
            # Add more locales as needed
        }

    def get_message(
        self,
        error_code: str,
        locale: Optional[Locale] = None,
        fallback_message: Optional[str] = None,
    ) -> str:
        """
        Get user-friendly message for error code.

        Args:
            error_code: The error code to look up
            locale: The locale to use (defaults to default_locale)
            fallback_message: Message to use if code not found

        Returns:
            User-friendly error message
        """
        locale = locale or self.default_locale

        # Try to get message for specified locale
        locale_messages = self.messages.get(locale, {})
        message = locale_messages.get(error_code)

        # If not found, try default locale
        if not message and locale != self.default_locale:
            default_messages = self.messages.get(self.default_locale, {})
            message = default_messages.get(error_code)

        # Use fallback if still not found
        if not message:
            message = fallback_message or f"An error occurred (code: {error_code})"

        return message

    def add_message(self, error_code: str, message: str, locale: Locale = None) -> None:
        """Add or update an error message."""
        locale = locale or self.default_locale

        if locale not in self.messages:
            self.messages[locale] = {}

        self.messages[locale][error_code] = message

    def get_available_locales(self) -> list[Locale]:
        """Get list of available locales."""
        return list(self.messages.keys())

    def has_message(self, error_code: str, locale: Optional[Locale] = None) -> bool:
        """Check if a message exists for the given code and locale."""
        locale = locale or self.default_locale
        locale_messages = self.messages.get(locale, {})
        return error_code in locale_messages


# Global message manager instance
message_manager = ErrorMessageManager()


def get_user_message(error_code: str, locale: Optional[str] = None, **kwargs) -> str:
    """
    Get a user-friendly error message with optional formatting.

    Args:
        error_code: The error code to look up
        locale: The locale string (e.g., "en_US")
        **kwargs: Format parameters for string interpolation

    Returns:
        Formatted user-friendly error message
    """
    # Convert locale string to Locale enum
    locale_enum = None
    if locale:
        try:
            locale_enum = Locale(locale)
        except ValueError:
            locale_enum = None

    # Get base message
    message = message_manager.get_message(error_code, locale_enum)

    # Apply formatting if kwargs provided
    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return unformatted message
            pass

    return message
