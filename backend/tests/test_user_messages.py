"""Test user message localization system."""

import pytest

from backend.utils.user_messages import (
    ErrorMessageManager,
    Locale,
    get_user_message,
    message_manager,
)


def test_message_manager_default_locale():
    """Test message manager with default locale."""
    manager = ErrorMessageManager()

    # Test getting English message
    message = manager.get_message("AUTH_001")
    assert "email or password" in message

    # Test non-existent code
    message = manager.get_message("NONEXISTENT", fallback_message="Custom fallback")
    assert message == "Custom fallback"


def test_message_manager_spanish_locale():
    """Test message manager with Spanish locale."""
    manager = ErrorMessageManager()

    # Test getting Spanish message
    message = manager.get_message("AUTH_001", locale=Locale.ES_ES)
    assert "correo o contraseña" in message

    # Test fallback to English for non-translated message
    message = manager.get_message("VAL_002", locale=Locale.ES_ES)
    assert "check the format" in message  # Should fallback to English


def test_add_custom_message():
    """Test adding custom messages."""
    manager = ErrorMessageManager()

    # Add custom message
    manager.add_message("CUSTOM_001", "This is a custom error message")

    # Verify it can be retrieved
    message = manager.get_message("CUSTOM_001")
    assert message == "This is a custom error message"

    # Add message for specific locale
    manager.add_message("CUSTOM_002", "Mensaje personalizado", locale=Locale.ES_ES)
    message = manager.get_message("CUSTOM_002", locale=Locale.ES_ES)
    assert message == "Mensaje personalizado"


def test_available_locales():
    """Test getting available locales."""
    manager = ErrorMessageManager()
    locales = manager.get_available_locales()

    assert Locale.EN_US in locales
    assert Locale.ES_ES in locales


def test_has_message():
    """Test checking message existence."""
    manager = ErrorMessageManager()

    # Check existing message
    assert manager.has_message("AUTH_001")
    assert manager.has_message("AUTH_001", locale=Locale.ES_ES)

    # Check non-existent message
    assert not manager.has_message("NONEXISTENT")


def test_get_user_message_function():
    """Test the global get_user_message function."""
    # Test with default locale
    message = get_user_message("AUTH_001")
    assert "email or password" in message

    # Test with string locale
    message = get_user_message("AUTH_001", locale="es_ES")
    assert "correo o contraseña" in message

    # Test with invalid locale (should use default)
    message = get_user_message("AUTH_001", locale="invalid_locale")
    assert "email or password" in message


def test_message_formatting():
    """Test message formatting with parameters."""
    # Add a message with format placeholders
    message_manager.add_message(
        "TEST_FORMAT", "Hello {name}, your order #{order_id} is ready."
    )

    # Test formatting
    message = get_user_message("TEST_FORMAT", name="John", order_id=12345)
    assert message == "Hello John, your order #12345 is ready."

    # Test with missing parameters (should return unformatted)
    message = get_user_message("TEST_FORMAT")
    assert "{name}" in message


def test_comprehensive_error_codes():
    """Test that all major error code categories have messages."""
    categories = ["AUTH", "AUTHZ", "VAL", "LLM", "SYS", "NET", "DOC", "PAY"]

    for category in categories:
        # Test first error code in each category
        code = f"{category}_001"
        assert message_manager.has_message(code), f"Missing message for {code}"

        message = message_manager.get_message(code)
        assert len(message) > 0, f"Empty message for {code}"
        assert "(" not in message, f"Message contains error code: {message}"


if __name__ == "__main__":
    # Run basic tests
    print("Testing message manager...")
    test_message_manager_default_locale()
    print("✓ Default locale tests passed")

    print("\nTesting Spanish locale...")
    test_message_manager_spanish_locale()
    print("✓ Spanish locale tests passed")

    print("\nTesting custom messages...")
    test_add_custom_message()
    print("✓ Custom message tests passed")

    print("\nTesting comprehensive error codes...")
    test_comprehensive_error_codes()
    print("✓ Error code coverage tests passed")

    print("\nAll tests passed!")
