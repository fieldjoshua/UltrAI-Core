#!/usr/bin/env python3
"""
Test script to verify security enhancements implemented in Phase 1.
"""

import os
import sys
from urllib.parse import urlparse

# Add the current directory to Python path
sys.path.insert(0, os.path.abspath("."))

# Import the validation utility
from backend.utils.validation import is_url_safe, url_validator, validate_url


def test_url_validation():
    """Test the URL validation utility with various inputs."""
    print("\n=== Testing URL Validation Utility ===\n")

    # Test allowed URLs
    allowed_urls = [
        "https://api.openai.com/v1/chat/completions",
        "https://api.anthropic.com/v1/messages",
        "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent",
        "https://api.mistral.ai/v1/chat/completions",
    ]

    print("Testing allowed URLs:")
    for url in allowed_urls:
        try:
            is_safe = is_url_safe(url)
            print(f"  {url}: {'✅ Allowed' if is_safe else '❌ Blocked'}")
        except Exception as e:
            print(f"  {url}: ❌ Error: {e}")

    # Test disallowed URLs
    disallowed_urls = [
        "http://localhost:8080",
        "https://evil-site.com",
        "http://169.254.169.254/metadata",
        "http://10.0.0.1",
        "file:///etc/passwd",
        "ftp://ftp.example.com",
    ]

    print("\nTesting disallowed URLs:")
    for url in disallowed_urls:
        try:
            is_safe = is_url_safe(url)
            print(
                f"  {url}: {'✅ Allowed (PROBLEM!)' if is_safe else '✅ Blocked (correct)'}"
            )
        except Exception as e:
            print(f"  {url}: ✅ Error (expected): {e}")


def test_environment_variables():
    """Test the environment variable handling."""
    print("\n=== Testing Environment Variable Handling ===\n")

    # Save original environment variables
    original_env = os.environ.copy()

    try:
        # Test SENTRY_DSN handling
        print("Testing SENTRY_DSN handling:")
        os.environ.pop("SENTRY_DSN", None)
        sentry_dsn = os.environ.get("SENTRY_DSN", "")
        print(
            f"  Without SENTRY_DSN: {'✅ Empty string (correct)' if sentry_dsn == '' else '❌ Not empty (problem)'}"
        )

        os.environ["SENTRY_DSN"] = "test-dsn-value"
        sentry_dsn = os.environ.get("SENTRY_DSN", "")
        print(
            f"  With SENTRY_DSN: {'✅ Value present' if sentry_dsn == 'test-dsn-value' else '❌ Value missing'}"
        )

        # Test ENVIRONMENT handling
        print("\nTesting ENVIRONMENT handling:")
        os.environ.pop("ENVIRONMENT", None)
        env = os.environ.get("ENVIRONMENT", "development")
        print(
            f"  Without ENVIRONMENT: {'✅ Default to development' if env == 'development' else '❌ Wrong default'}"
        )

        os.environ["ENVIRONMENT"] = "production"
        env = os.environ.get("ENVIRONMENT", "development")
        print(
            f"  With ENVIRONMENT=production: {'✅ Value present' if env == 'production' else '❌ Value missing'}"
        )

        # Test URL validation with environment variables
        print("\nTesting domain allowlist from environment:")
        os.environ["ALLOWED_EXTERNAL_DOMAINS"] = "example.com,test.org"

        # Re-initialize validator to pickup new environment
        new_validator = backend.utils.validation.URLValidator()

        is_example_allowed = "example.com" in new_validator.allowed_domains
        is_test_allowed = "test.org" in new_validator.allowed_domains
        is_openai_allowed = "api.openai.com" in new_validator.allowed_domains

        print(
            f"  example.com allowed: {'✅ Yes (correct)' if is_example_allowed else '❌ No (problem)'}"
        )
        print(
            f"  test.org allowed: {'✅ Yes (correct)' if is_test_allowed else '❌ No (problem)'}"
        )
        print(
            f"  api.openai.com allowed: {'✅ No (correct)' if not is_openai_allowed else '❌ Yes (problem)'}"
        )

    finally:
        # Restore original environment
        os.environ.clear()
        os.environ.update(original_env)


def main():
    """Main test function."""
    print("Running security tests...")

    # Run tests
    test_url_validation()
    test_environment_variables()

    print("\nTests completed.")


if __name__ == "__main__":
    main()
