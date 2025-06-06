"""
Password handling utilities.

This module provides functions for securely hashing and verifying passwords
using industry-standard password hashing algorithms.
"""

import base64
import hashlib
import hmac
import os
import secrets
from typing import Optional, Tuple

# Constants for password hashing
HASH_ALGORITHM = "sha256"
ITERATIONS = 600000  # High iteration count for security
KEY_LENGTH = 32  # 256 bits
SALT_SIZE = 16  # 128 bits


def hash_password(password: str) -> str:
    """
    Hash a password securely using PBKDF2 with a random salt.

    Args:
        password: The plaintext password to hash

    Returns:
        A string containing the algorithm, iterations, salt, and hash,
        all encoded in a format suitable for storage.
    """
    # Generate a random salt
    salt = os.urandom(SALT_SIZE)

    # Hash the password using PBKDF2
    hash_bytes = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM, password.encode("utf-8"), salt, ITERATIONS, KEY_LENGTH
    )

    # Encode the salt and hash for storage
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(hash_bytes).decode("ascii")

    # Format: algorithm$iterations$salt$hash
    return f"{HASH_ALGORITHM}${ITERATIONS}${salt_b64}${hash_b64}"


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a stored hash.

    Args:
        password: The plaintext password to verify
        hashed_password: The stored password hash

    Returns:
        True if the password matches the hash, False otherwise
    """
    # Parse the stored hash
    try:
        algorithm, iterations_str, salt_b64, hash_b64 = hashed_password.split("$")
        iterations = int(iterations_str)
        salt = base64.b64decode(salt_b64)
        stored_hash = base64.b64decode(hash_b64)
    except (ValueError, TypeError):
        # If the hash is malformed, the password is invalid
        return False

    # Only support our current algorithm
    if algorithm != HASH_ALGORITHM:
        return False

    # Hash the provided password with the same salt and iterations
    hash_bytes = hashlib.pbkdf2_hmac(
        algorithm, password.encode("utf-8"), salt, iterations, len(stored_hash)
    )

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(hash_bytes, stored_hash)


def generate_reset_token() -> str:
    """
    Generate a secure token for password reset.

    Returns:
        A secure random token encoded as a URL-safe base64 string
    """
    # Generate 32 random bytes (256 bits)
    token_bytes = secrets.token_bytes(32)

    # Encode as URL-safe base64
    return base64.urlsafe_b64encode(token_bytes).decode("ascii")


def check_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Check if a password meets minimum strength requirements.

    Args:
        password: The password to check

    Returns:
        A tuple of (is_valid, error_message) where is_valid is a boolean
        indicating if the password is strong enough, and error_message
        is None if valid, or a string describing the issue if invalid.
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Check for different character classes
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)

    # Calculate strength score (0-4)
    strength = sum([has_lower, has_upper, has_digit, has_special])

    if strength < 3:
        return (
            False,
            "Password must contain at least 3 of the following: lowercase letters, uppercase letters, digits, special characters",
        )

    return True, None
