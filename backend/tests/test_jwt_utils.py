"""
Tests for JWT token utilities.

This module contains comprehensive tests for the JWT token utilities,
focusing on token creation, validation, expiration, and various edge cases.
"""

import time
import uuid
import pytest
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch

from backend.utils.jwt import (
    create_token,
    create_refresh_token,
    decode_token,
    decode_refresh_token,
    is_token_expired,
    get_token_expiration,
    SECRET_KEY,
    REFRESH_SECRET_KEY,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
)


def test_create_token_basic():
    """Test creating a basic access token."""
    # Create a token with minimal data
    data = {"sub": "user123"}
    token = create_token(data)
    
    # Decode and validate
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
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
    
    # Create token with custom expiry
    token = create_token(data, expires_delta=custom_expiry)
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # Check expiration is approximately correct (within 1 second)
    expected_exp = (datetime.utcnow() + custom_expiry).timestamp()
    assert abs(payload["exp"] - expected_exp) < 1


def test_create_refresh_token():
    """Test creating a refresh token."""
    data = {"sub": "user123"}
    token = create_refresh_token(data)
    
    # Decode and validate
    payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    
    # Check data was preserved
    assert payload["sub"] == "user123"
    
    # Check standard claims were added
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload
    assert payload["type"] == "refresh"
    
    # Check expiration is set correctly
    expected_exp = (datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
    assert abs(payload["exp"] - expected_exp) < 1


def test_create_refresh_token_with_custom_expiry():
    """Test creating a refresh token with custom expiration."""
    data = {"sub": "user123"}
    custom_expiry = timedelta(days=30)
    
    # Create token with custom expiry
    token = create_refresh_token(data, expires_delta=custom_expiry)
    payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
    
    # Check expiration is approximately correct (within 1 second)
    expected_exp = (datetime.utcnow() + custom_expiry).timestamp()
    assert abs(payload["exp"] - expected_exp) < 1


def test_decode_token_access():
    """Test decoding an access token."""
    # Create and decode an access token
    data = {"sub": "user123", "custom": "value"}
    token = create_token(data)
    
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
    # Create a token that expires in 1 second
    data = {"sub": "user123"}
    token = create_token(data, expires_delta=timedelta(seconds=1))
    
    # Initially it should not be expired
    assert not is_token_expired(token)
    
    # Wait for expiration
    time.sleep(2)
    
    # Now it should be expired
    assert is_token_expired(token)


def test_get_token_expiration():
    """Test getting token expiration timestamp."""
    # Create a token with known expiration
    data = {"sub": "user123"}
    expiry = timedelta(minutes=5)
    expected_exp = (datetime.utcnow() + expiry).timestamp()
    
    token = create_token(data, expires_delta=expiry)
    
    # Get expiration
    exp = get_token_expiration(token)
    
    # Should be within 1 second of expected
    assert abs(exp - expected_exp) < 1


def test_decode_token_invalid():
    """Test decoding invalid tokens."""
    # Test completely invalid token
    with pytest.raises(jwt.PyJWTError):
        decode_token("invalid.token.string")
    
    # Test token with invalid signature
    valid_token = create_token({"sub": "user123"})
    parts = valid_token.rsplit('.', 1)
    invalid_sig_token = parts[0] + ".invalidsignature"
    
    with pytest.raises(jwt.PyJWTError):
        decode_token(invalid_sig_token)


def test_token_with_missing_claims():
    """Test token validation with missing required claims."""
    # Manually create a token without required claims
    payload = {
        "sub": "user123",
        # Missing "type" claim
        "iat": datetime.utcnow().timestamp(),
        "exp": (datetime.utcnow() + timedelta(minutes=5)).timestamp(),
        "jti": str(uuid.uuid4())
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # This should still decode as we don't validate the "type" claim in decode_token
    payload = decode_token(token)
    assert payload["sub"] == "user123"
    
    # But it would fail in decode_refresh_token
    with pytest.raises(jwt.PyJWTError):
        decode_refresh_token(token)


def test_expired_token_validation():
    """Test validation of expired tokens."""
    # Create an already expired token
    data = {"sub": "user123"}

    # Mock datetime.utcnow to create a token that appears to have been created in the past
    with patch('backend.utils.jwt.datetime') as mock_datetime:
        # Configure mock
        mock_now = datetime.utcnow()
        mock_datetime.utcnow.return_value = mock_now + timedelta(seconds=-30)  # 30 seconds in the past

        # Create token that will be expired
        token = create_token(data)
    
    # Token should be expired
    assert is_token_expired(token)
    
    # Decoding should fail with ExpiredSignatureError
    with pytest.raises(jwt.ExpiredSignatureError):
        decode_token(token)
    
    # But we can bypass expiration check
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
    header_b64, payload_b64, signature = token.split('.')
    
    # Tamper with the payload to escalate privileges (decode, modify, encode)
    import base64
    import json
    
    # Decode payload
    padded_payload = payload_b64 + '=' * (4 - len(payload_b64) % 4)
    payload_json = base64.urlsafe_b64decode(padded_payload).decode('utf-8')
    payload_data = json.loads(payload_json)
    
    # Modify payload
    payload_data["role"] = "admin"
    
    # Encode modified payload
    modified_payload_json = json.dumps(payload_data)
    modified_payload_b64 = base64.urlsafe_b64encode(modified_payload_json.encode('utf-8')).decode('utf-8').rstrip('=')
    
    # Construct tampered token
    tampered_token = f"{header_b64}.{modified_payload_b64}.{signature}"
    
    # Should fail validation due to signature mismatch
    with pytest.raises(jwt.PyJWTError):
        decode_token(tampered_token)


if __name__ == "__main__":
    pytest.main(["-xvs", "test_jwt_utils.py"])