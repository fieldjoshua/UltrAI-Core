"""
JWT token utilities wrapper.

This module provides functions for creating, validating, and working with JWT tokens
for authentication and authorization. It handles graceful degradation when PyJWT
is not available by using a simple fallback implementation.
"""

import os
import time
import uuid
import hmac
import json
import base64
import hashlib
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta

from backend.utils.logging import get_logger
from backend.utils.dependency_manager import jwt_dependency

# Get logger
logger = get_logger("jwt_wrapper", "logs/jwt.log")

# Get secret keys from environment variables or use secure defaults
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or "3ed3fb79ec2d6f0a7d7a00a97a7dbd07aa09fb0dedf7b6ac7eec4260456d0d06"
REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY") or "27e55f29f1d0e3dc1bb5e2d7ea12596b4b39edddd8c06ad9d55f0e9bbce3c75c"

# Token settings
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
ALGORITHM = "HS256"
TOKEN_TYPE = "bearer"

# Flag to determine if we're using PyJWT or fallback
_using_pyjwt = jwt_dependency.is_available()


class JWTError(Exception):
    """Exception for JWT errors"""
    pass


class ExpiredSignatureError(JWTError):
    """Exception for expired JWT tokens"""
    pass


class InvalidTokenError(JWTError):
    """Exception for invalid JWT tokens"""
    pass


# Simple fallback JWT implementation for development
class FallbackJWT:
    """Fallback JWT implementation"""
    
    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        """Base64url encode bytes"""
        return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')
    
    @staticmethod
    def _base64url_decode(data: str) -> bytes:
        """Base64url decode string"""
        padding = b'=' * (4 - len(data) % 4)
        return base64.urlsafe_b64decode(data.encode('ascii') + padding)
    
    @staticmethod
    def encode(payload: Dict[str, Any], key: str, algorithm: str = "HS256") -> str:
        """
        Create a JWT token
        
        Args:
            payload: Payload data
            key: Secret key
            algorithm: Signing algorithm (only HS256 supported)
            
        Returns:
            JWT token string
        """
        if algorithm != "HS256":
            raise ValueError("Only HS256 algorithm is supported in fallback mode")
        
        # Create header
        header = {"alg": algorithm, "typ": "JWT"}
        
        # Encode header and payload
        header_encoded = FallbackJWT._base64url_encode(json.dumps(header).encode())
        payload_encoded = FallbackJWT._base64url_encode(json.dumps(payload).encode())
        
        # Create signature
        message = f"{header_encoded}.{payload_encoded}"
        signature = hmac.new(
            key.encode() if isinstance(key, str) else key,
            message.encode(),
            hashlib.sha256
        ).digest()
        signature_encoded = FallbackJWT._base64url_encode(signature)
        
        # Combine parts
        token = f"{header_encoded}.{payload_encoded}.{signature_encoded}"
        return token
    
    @staticmethod
    def decode(token: str, key: str, algorithms: List[str] = None, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Decode and validate a JWT token
        
        Args:
            token: JWT token
            key: Secret key
            algorithms: List of allowed algorithms (only HS256 supported)
            options: Options for validation
            
        Returns:
            Decoded payload
            
        Raises:
            JWTError: If token is invalid
            ExpiredSignatureError: If token is expired
        """
        # Set defaults
        if algorithms is None:
            algorithms = ["HS256"]
        if "HS256" not in algorithms:
            raise ValueError("Only HS256 algorithm is supported in fallback mode")
        
        if options is None:
            options = {"verify_exp": True}
        
        # Split token
        try:
            header_encoded, payload_encoded, signature_encoded = token.split(".")
        except ValueError:
            raise InvalidTokenError("Invalid token format")
        
        # Verify signature
        message = f"{header_encoded}.{payload_encoded}"
        expected_signature = hmac.new(
            key.encode() if isinstance(key, str) else key,
            message.encode(),
            hashlib.sha256
        ).digest()
        expected_signature_encoded = FallbackJWT._base64url_encode(expected_signature)
        
        if signature_encoded != expected_signature_encoded:
            raise InvalidTokenError("Invalid signature")
        
        # Decode payload
        try:
            payload = json.loads(FallbackJWT._base64url_decode(payload_encoded))
        except Exception as e:
            raise InvalidTokenError(f"Invalid payload: {str(e)}")
        
        # Check expiration
        if options.get("verify_exp", True) and "exp" in payload:
            exp_timestamp = payload["exp"]
            current_timestamp = time.time()
            
            if current_timestamp > exp_timestamp:
                raise ExpiredSignatureError("Token expired")
        
        return payload


def create_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token payload
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT token string
    """
    to_encode = data.copy()
    
    # Add standard claims
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
    to_encode.update({
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "jti": str(uuid.uuid4()),
        "type": "access"
    })
    
    # Create token
    if _using_pyjwt:
        # Use PyJWT
        jwt_module = jwt_dependency.get_module()
        encoded_jwt = jwt_module.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    else:
        # Use fallback
        return FallbackJWT.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: The data to encode in the token payload
        expires_delta: Optional custom expiration time
        
    Returns:
        JWT refresh token string
    """
    to_encode = data.copy()
    
    # Add standard claims
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
    to_encode.update({
        "exp": expire.timestamp(),
        "iat": datetime.utcnow().timestamp(),
        "jti": str(uuid.uuid4()),
        "type": "refresh"
    })
    
    # Create token with refresh secret
    if _using_pyjwt:
        # Use PyJWT
        jwt_module = jwt_dependency.get_module()
        encoded_jwt = jwt_module.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    else:
        # Use fallback
        return FallbackJWT.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, verify_exp: bool = True) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token to decode
        verify_exp: Whether to verify token expiration
        
    Returns:
        Decoded token payload as a dictionary
        
    Raises:
        JWTError: If token validation fails
    """
    options = {"verify_exp": verify_exp}
    
    # Try first with access token secret
    try:
        if _using_pyjwt:
            # Use PyJWT
            jwt_module = jwt_dependency.get_module()
            payload = jwt_module.decode(
                token, 
                SECRET_KEY, 
                algorithms=[ALGORITHM],
                options=options
            )
        else:
            # Use fallback
            payload = FallbackJWT.decode(
                token, 
                SECRET_KEY, 
                algorithms=[ALGORITHM],
                options=options
            )
        return payload
    except (JWTError, ExpiredSignatureError):
        # If that fails, try with refresh token secret
        try:
            if _using_pyjwt:
                # Use PyJWT
                jwt_module = jwt_dependency.get_module()
                payload = jwt_module.decode(
                    token, 
                    REFRESH_SECRET_KEY, 
                    algorithms=[ALGORITHM],
                    options=options
                )
            else:
                # Use fallback
                payload = FallbackJWT.decode(
                    token, 
                    REFRESH_SECRET_KEY, 
                    algorithms=[ALGORITHM],
                    options=options
                )
            return payload
        except Exception as e:
            # Re-raise the exception
            if _using_pyjwt:
                jwt_module = jwt_dependency.get_module()
                if isinstance(e, jwt_module.ExpiredSignatureError):
                    raise ExpiredSignatureError("Token expired")
                else:
                    raise InvalidTokenError(str(e))
            else:
                raise


def decode_refresh_token(token: str, verify_exp: bool = True) -> Dict[str, Any]:
    """
    Decode and validate a JWT refresh token.
    
    Args:
        token: The JWT refresh token to decode
        verify_exp: Whether to verify token expiration
        
    Returns:
        Decoded token payload as a dictionary
        
    Raises:
        JWTError: If token validation fails
    """
    options = {"verify_exp": verify_exp}
    
    try:
        if _using_pyjwt:
            # Use PyJWT
            jwt_module = jwt_dependency.get_module()
            payload = jwt_module.decode(
                token, 
                REFRESH_SECRET_KEY, 
                algorithms=[ALGORITHM],
                options=options
            )
        else:
            # Use fallback
            payload = FallbackJWT.decode(
                token, 
                REFRESH_SECRET_KEY, 
                algorithms=[ALGORITHM],
                options=options
            )
    except Exception as e:
        # Re-raise the exception
        if _using_pyjwt:
            jwt_module = jwt_dependency.get_module()
            if isinstance(e, jwt_module.ExpiredSignatureError):
                raise ExpiredSignatureError("Token expired")
            else:
                raise InvalidTokenError(str(e))
        else:
            raise
    
    # Verify it's a refresh token
    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid token type")
        
    return payload


def is_token_expired(token: str) -> bool:
    """
    Check if a token is expired.
    
    Args:
        token: The JWT token to check
        
    Returns:
        True if the token is expired, False otherwise
    """
    try:
        decode_token(token)
        return False
    except ExpiredSignatureError:
        return True
    except JWTError:
        # For other errors, consider the token invalid (therefore "expired")
        return True


def get_token_expiration(token: str) -> Optional[float]:
    """
    Get the expiration timestamp from a token.
    
    Args:
        token: The JWT token
        
    Returns:
        Expiration timestamp as a float, or None if unable to decode
    """
    try:
        # Decode without verifying expiration
        payload = decode_token(token, verify_exp=False)
        return payload.get("exp")
    except JWTError:
        return None


def is_using_pyjwt() -> bool:
    """
    Check if we're using PyJWT or fallback.
    
    Returns:
        True if using PyJWT, False if using fallback implementation
    """
    return _using_pyjwt


def get_jwt_status() -> Dict[str, Any]:
    """
    Get JWT implementation status.
    
    Returns:
        Dictionary with status information
    """
    return {
        "using_pyjwt": _using_pyjwt,
        "pyjwt_available": jwt_dependency.is_available(),
        "algorithm": ALGORITHM,
        "access_token_expire_minutes": ACCESS_TOKEN_EXPIRE_MINUTES,
        "refresh_token_expire_days": REFRESH_TOKEN_EXPIRE_DAYS,
    }