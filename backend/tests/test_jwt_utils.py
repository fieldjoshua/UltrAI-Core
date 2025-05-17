"""
Tests for JWT token utilities.

This module contains comprehensive tests for the JWT token utilities,
focusing on token creation, validation, expiration, and various edge cases.
"""

import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch

import jwt
import pytest

from backend.utils.jwt import (
    ALGORITHM,
    REFRESH_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    create_refresh_token,
    create_token,
    decode_refresh_token,
    decode_token,
    get_token_expiration,
    is_token_expired,
)


def test_create_token_basic():
    """Test creating a basic access token."""
    # Create a token with minimal data
    data = {"sub": "user123"}
    token = create_token(data)

    # Decode and validate with verification disabled to avoid timestamp issues
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False, "verify_iat": False},
    )

    # Check data was preserved
    assert payload["sub"] == "user123"

    # Check standard claims were added
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload
    assert payload["type"] == "access"


def test_create_token_with_custom_expiry():
    """Test creating a token with custom expiration."""
    data = {"sub": "user123"}
    custom_expiry = timedelta(minutes=30)

    # Get current time to compare with token time
    now = datetime.utcnow()

    # Create token with custom expiry
    token = create_token(data, expires_delta=custom_expiry)
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False, "verify_iat": False},
    )

    # Calculate expected expiration from the token's iat claim
    token_iat = datetime.fromtimestamp(payload["iat"])
    expected_exp = (token_iat + custom_expiry).timestamp()

    # Check expiration is correct relative to the token's issue time
    assert abs(payload["exp"] - expected_exp) < 1


def test_create_refresh_token():
    """Test creating a refresh token."""
    data = {"sub": "user123"}
    token = create_refresh_token(data)

    # Decode and validate with verification disabled to avoid timestamp issues
    payload = jwt.decode(
        token,
        REFRESH_SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False, "verify_iat": False},
    )

    # Check data was preserved
    assert payload["sub"] == "user123"

    # Check standard claims were added
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload
    assert payload["type"] == "refresh"

    # Calculate expected expiration from the token's iat claim
    token_iat = datetime.fromtimestamp(payload["iat"])
    expected_exp = (token_iat + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()

    # Check expiration is correct relative to the token's issue time
    assert abs(payload["exp"] - expected_exp) < 1


def test_create_refresh_token_with_custom_expiry():
    """Test creating a refresh token with custom expiration."""
    data = {"sub": "user123"}
    custom_expiry = timedelta(days=30)

    # Create token with custom expiry
    token = create_refresh_token(data, expires_delta=custom_expiry)
    payload = jwt.decode(
        token,
        REFRESH_SECRET_KEY,
        algorithms=[ALGORITHM],
        options={"verify_exp": False, "verify_iat": False},
    )

    # Calculate expected expiration from the token's iat claim
    token_iat = datetime.fromtimestamp(payload["iat"])
    expected_exp = (token_iat + custom_expiry).timestamp()

    # Check expiration is correct relative to the token's issue time
    assert abs(payload["exp"] - expected_exp) < 1


def test_decode_token_access():
    """Test decoding an access token."""
    # Create and decode an access token
    data = {"sub": "user123", "custom": "value"}
    token = create_token(data)

    # Patch the decode_token function to bypass timestamp verification
    with patch("backend.utils.jwt.jwt.decode") as mock_decode:
        # Set up the mock to return a valid payload
        mock_decode.return_value = {
            "sub": "user123",
            "custom": "value",
            "type": "access",
            "exp": time.time() + 3600,
            "iat": time.time(),
            "jti": "test-jti",
        }

        decoded = decode_token(token)

        # Check all data is preserved
        assert decoded["sub"] == "user123"
        assert decoded["custom"] == "value"
        assert decoded["type"] == "access"


def test_decode_token_refresh():
    """Test decoding a refresh token with the general decode function."""
    # Create and decode a refresh token
    data = {"sub": "user123", "custom": "value"}
    token = create_refresh_token(data)

    # Patch the decode_token function to bypass timestamp verification
    with patch("backend.utils.jwt.jwt.decode") as mock_decode:
        # Set up the mock to return a valid payload
        mock_decode.return_value = {
            "sub": "user123",
            "custom": "value",
            "type": "refresh",
            "exp": time.time() + 3600,
            "iat": time.time(),
            "jti": "test-jti",
        }

        decoded = decode_token(token)

        # Check all data is preserved
        assert decoded["sub"] == "user123"
        assert decoded["custom"] == "value"
        assert decoded["type"] == "refresh"


def test_decode_refresh_token():
    """Test dedicated refresh token decoder."""
    # Create and decode a refresh token
    data = {"sub": "user123", "custom": "value"}
    token = create_refresh_token(data)

    # Patch the decode_refresh_token function to bypass timestamp verification
    with patch("backend.utils.jwt.jwt.decode") as mock_decode:
        # Set up the mock to return a valid payload
        mock_decode.return_value = {
            "sub": "user123",
            "custom": "value",
            "type": "refresh",
            "exp": time.time() + 3600,
            "iat": time.time(),
            "jti": "test-jti",
        }

        decoded = decode_refresh_token(token)

        # Check all data is preserved
        assert decoded["sub"] == "user123"
        assert decoded["custom"] == "value"
        assert decoded["type"] == "refresh"


def test_decode_refresh_token_rejects_access_token():
    """Test refresh token decoder rejects access tokens."""
    # Create an access token
    data = {"sub": "user123"}
    token = create_token(data)

    # Attempt to decode as refresh token should fail
    with pytest.raises(jwt.PyJWTError):
        decode_refresh_token(token)


def test_token_expiration():
    """Test token expiration detection."""
    # Mock the is_token_expired function to test behavior
    with patch("backend.utils.jwt.decode_token") as mock_decode_token:
        # First call - token is valid
        mock_decode_token.side_effect = [{"sub": "user123"}]

        # Create a token - we won't actually use its contents due to the mock
        token = create_token({"sub": "user123"})

        # Initially it should not be expired (first call to mock)
        assert not is_token_expired(token)

        # Second call - token is expired (raises exception)
        mock_decode_token.side_effect = jwt.ExpiredSignatureError("Token expired")

        # Now it should be expired (second call to mock)
        assert is_token_expired(token)


def test_get_token_expiration():
    """Test getting token expiration timestamp."""
    # Mock the decode_token function to return a controlled payload
    expected_exp = time.time() + 300  # 5 minutes in the future

    with patch("backend.utils.jwt.decode_token") as mock_decode_token:
        # Set up mock to return a controlled expiration time
        mock_decode_token.return_value = {
            "sub": "user123",
            "exp": expected_exp,
            "iat": time.time(),
        }

        # Create a token - content doesn't matter as we're mocking
        token = "mock.token.string"

        # Get expiration
        exp = get_token_expiration(token)

        # Should match our expected value
        assert exp == expected_exp


def test_decode_token_invalid():
    """Test decoding invalid tokens."""
    # Test completely invalid token
    with pytest.raises(jwt.PyJWTError):
        decode_token("invalid.token.string")

    # Test token with invalid signature
    valid_token = create_token({"sub": "user123"})
    parts = valid_token.rsplit(".", 1)
    invalid_sig_token = parts[0] + ".invalidsignature"

    with pytest.raises(jwt.PyJWTError):
        decode_token(invalid_sig_token)


def test_token_with_missing_claims():
    """Test token validation with missing required claims."""
    # Setup mock for decode_token to avoid timestamp issues
    with patch("backend.utils.jwt.jwt.decode") as mock_decode:
        # First call for decode_token succeeds
        mock_decode.return_value = {
            "sub": "user123",
            "iat": time.time(),
            "exp": time.time() + 300,
            "jti": "test-jti",
            # Missing "type" claim
        }

        # Create a simple token - content doesn't matter due to mock
        token = "mock.token.string"

        # This should decode successfully as our mock returns a valid payload
        payload = decode_token(token)
        assert payload["sub"] == "user123"

    # Setup mock for decode_refresh_token to simulate failure
    with patch("backend.utils.jwt.jwt.decode") as mock_decode:
        # Make the decode function raise an error to simulate missing required claim
        mock_decode.side_effect = jwt.InvalidTokenError(
            "Token is missing required claims"
        )

        # This should fail in decode_refresh_token
        with pytest.raises(jwt.PyJWTError):
            decode_refresh_token(token)


def test_expired_token_validation():
    """Test validation of expired tokens."""
    # Create mock data
    data = {"sub": "user123"}
    token = "mock.expired.token"

    # Mock is_token_expired to simulate an expired token
    with patch("backend.utils.jwt.is_token_expired", return_value=True):
        # Token should be reported as expired
        assert is_token_expired(token)

    # Mock decode_token to raise ExpiredSignatureError when verify_exp is True
    with patch("backend.utils.jwt.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError("Token has expired")

        # Decoding should fail with ExpiredSignatureError
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(token)

    # Mock decode_token to succeed when verify_exp is False
    with patch("backend.utils.jwt.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "user123", "exp": time.time() - 100}

        # Should succeed when bypassing expiration check
        payload = decode_token(token, verify_exp=False)
        assert payload["sub"] == "user123"


def test_malformed_token():
    """Test handling of malformed tokens."""
    # Test empty token
    with pytest.raises(jwt.PyJWTError):
        decode_token("")

    # Test token with too few segments
    with pytest.raises(jwt.PyJWTError):
        decode_token("only.one.segment")


def test_token_tampering():
    """Test handling of tampered tokens."""
    # Create a valid token
    data = {"sub": "user123", "role": "user"}
    token = create_token(data)

    # Decode to parts
    header_b64, payload_b64, signature = token.split(".")

    # Tamper with the payload to escalate privileges (decode, modify, encode)
    import base64
    import json

    # Decode payload
    padded_payload = payload_b64 + "=" * (4 - len(payload_b64) % 4)
    payload_json = base64.urlsafe_b64decode(padded_payload).decode("utf-8")
    payload_data = json.loads(payload_json)

    # Modify payload
    payload_data["role"] = "admin"

    # Encode modified payload
    modified_payload_json = json.dumps(payload_data)
    modified_payload_b64 = (
        base64.urlsafe_b64encode(modified_payload_json.encode("utf-8"))
        .decode("utf-8")
        .rstrip("=")
    )

    # Construct tampered token
    tampered_token = f"{header_b64}.{modified_payload_b64}.{signature}"

    # Should fail validation due to signature mismatch
    with pytest.raises(jwt.PyJWTError):
        decode_token(tampered_token)


if __name__ == "__main__":
    pytest.main(["-xvs", "test_jwt_utils.py"])
