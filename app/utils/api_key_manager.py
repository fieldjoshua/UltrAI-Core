"""
API key management utilities for the Ultra backend.

This module provides functions for generating, validating, and managing API keys.
It includes secure storage, rotation, and access control mechanisms.
"""

import base64
import hashlib
import hmac
import os
import secrets
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError:
    # Fallback stubs for cryptography when unavailable
    class DummyFernet:
        def __init__(self, key):
            pass

        def encrypt(self, data):
            return data

        def decrypt(self, token):
            return token

    Fernet = DummyFernet  # type: ignore

    class hashes:
        class SHA256:
            """Dummy SHA256 algorithm stub"""

            pass

    class PBKDF2HMAC:
        def __init__(self, algorithm=None, length=None, salt=None, iterations=None):
            pass

        def derive(self, data):
            return data


from app.utils.logging import get_logger, log_audit

# Set up logger
logger = get_logger("api_key_manager", "logs/security.log")

# Key for encrypting API keys in storage
# In production, this key should be loaded from a secure location (e.g., environment variables, secrets manager)
ENCRYPTION_KEY = os.getenv("API_KEY_ENCRYPTION_KEY", "default-dev-encryption-key")
# Generate a proper Fernet key from the encryption key
if not ENCRYPTION_KEY:
    # Generate a key if not provided
    salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    ENCRYPTION_KEY = base64.urlsafe_b64encode(kdf.derive(b"ultra-api-keys"))
    logger.warning(
        "Using generated API key encryption key. This should be set in environment variables for production."
    )
else:
    # Create a Fernet key from the encryption key
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"ultra-salt",  # Fixed salt for development
        iterations=100000,
    )
    ENCRYPTION_KEY = base64.urlsafe_b64encode(kdf.derive(ENCRYPTION_KEY.encode()))

# Initialize Fernet cipher for encryption/decryption
cipher = Fernet(ENCRYPTION_KEY)


class ApiKeyScope(str, Enum):
    """Enum for API key scopes"""

    READ_ONLY = "read"
    READ_WRITE = "write"
    ADMIN = "admin"


class ApiKey:
    """Class representing an API key"""

    def __init__(
        self,
        key_id: str,
        user_id: str,
        name: str,
        scope: ApiKeyScope,
        expires_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        last_used_at: Optional[datetime] = None,
        rate_limit: Optional[int] = None,
        allowed_paths: Optional[List[str]] = None,
        allowed_ips: Optional[List[str]] = None,
    ):
        """
        Initialize API key

        Args:
            key_id: Unique identifier for the key
            user_id: ID of the user who owns the key
            name: Human-readable name for the key
            scope: Scope of access for the key
            expires_at: Expiration date (None for no expiration)
            created_at: Creation date
            last_used_at: Last usage date
            rate_limit: Rate limit for the key (requests per minute)
            allowed_paths: List of paths the key is allowed to access (None for all)
            allowed_ips: List of IPs allowed to use the key (None for all)
        """
        self.key_id = key_id
        self.user_id = user_id
        self.name = name
        self.scope = scope
        self.expires_at = expires_at
        self.created_at = created_at or datetime.now()
        self.last_used_at = last_used_at
        self.rate_limit = rate_limit
        self.allowed_paths = allowed_paths
        self.allowed_ips = allowed_ips

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert API key to dictionary

        Returns:
            Dictionary representation of the API key
        """
        return {
            "key_id": self.key_id,
            "user_id": self.user_id,
            "name": self.name,
            "scope": self.scope,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "created_at": self.created_at.isoformat(),
            "last_used_at": (
                self.last_used_at.isoformat() if self.last_used_at else None
            ),
            "rate_limit": self.rate_limit,
            "allowed_paths": self.allowed_paths,
            "allowed_ips": self.allowed_ips,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ApiKey":
        """
        Create API key from dictionary

        Args:
            data: Dictionary representation of the API key

        Returns:
            API key object
        """
        # Parse datetime fields
        expires_at = (
            datetime.fromisoformat(data["expires_at"])
            if data.get("expires_at")
            else None
        )
        created_at = (
            datetime.fromisoformat(data["created_at"])
            if data.get("created_at")
            else None
        )
        last_used_at = (
            datetime.fromisoformat(data["last_used_at"])
            if data.get("last_used_at")
            else None
        )

        return cls(
            key_id=data["key_id"],
            user_id=data["user_id"],
            name=data["name"],
            scope=ApiKeyScope(data["scope"]),
            expires_at=expires_at,
            created_at=created_at,
            last_used_at=last_used_at,
            rate_limit=data.get("rate_limit"),
            allowed_paths=data.get("allowed_paths"),
            allowed_ips=data.get("allowed_ips"),
        )

    def is_expired(self) -> bool:
        """
        Check if the API key is expired

        Returns:
            True if expired, False otherwise
        """
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def can_access_path(self, path: str) -> bool:
        """
        Check if the API key can access a path

        Args:
            path: Path to check

        Returns:
            True if allowed, False otherwise
        """
        if not self.allowed_paths:
            return True
        return any(path.startswith(allowed_path) for allowed_path in self.allowed_paths)

    def can_access_from_ip(self, ip_address: str) -> bool:
        """
        Check if the API key can be used from an IP address

        Args:
            ip_address: IP address to check

        Returns:
            True if allowed, False otherwise
        """
        if not self.allowed_ips:
            return True
        return ip_address in self.allowed_ips


class ApiKeyManager:
    """Manager for API keys"""

    def __init__(self):
        """Initialize API key manager"""
        self.api_keys: Dict[str, ApiKey] = {}  # key_id -> ApiKey
        self.key_hashes: Dict[str, str] = {}  # hashed_key -> key_id
        self.prefix_map: Dict[str, str] = {}  # key_prefix -> key_id

    def generate_api_key(
        self,
        user_id: str,
        name: str,
        scope: ApiKeyScope = ApiKeyScope.READ_ONLY,
        expires_in_days: Optional[int] = None,
        rate_limit: Optional[int] = None,
        allowed_paths: Optional[List[str]] = None,
        allowed_ips: Optional[List[str]] = None,
    ) -> Tuple[str, ApiKey]:
        """
        Generate a new API key

        Args:
            user_id: ID of the user who owns the key
            name: Human-readable name for the key
            scope: Scope of access for the key
            expires_in_days: Number of days until expiration (None for no expiration)
            rate_limit: Rate limit for the key (requests per minute)
            allowed_paths: List of paths the key is allowed to access (None for all)
            allowed_ips: List of IPs allowed to use the key (None for all)

        Returns:
            Tuple of (api_key, api_key_object)
        """
        # Generate a random key
        key_bytes = secrets.token_bytes(32)

        # Create a key ID
        key_id = secrets.token_hex(8)

        # Create a prefix (first 8 chars) for key identification
        prefix = "uk_" + secrets.token_hex(4)

        # Create the full key: prefix.base64_encoded_key
        full_key = f"{prefix}.{base64.urlsafe_b64encode(key_bytes).decode('ascii').rstrip('=')}"

        # Hash the key for storage
        key_hash = self._hash_key(full_key)

        # Create expiration date if specified
        expires_at = None
        if expires_in_days is not None:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        # Create the API key object
        api_key = ApiKey(
            key_id=key_id,
            user_id=user_id,
            name=name,
            scope=scope,
            expires_at=expires_at,
            created_at=datetime.now(),
            rate_limit=rate_limit,
            allowed_paths=allowed_paths,
            allowed_ips=allowed_ips,
        )

        # Store the API key
        self.api_keys[key_id] = api_key
        self.key_hashes[key_hash] = key_id
        self.prefix_map[prefix] = key_id

        # Log the key generation
        log_audit(
            action="generate_api_key",
            user_id=user_id,
            resource=f"api_key:{key_id}",
            details={
                "name": name,
                "scope": scope,
                "expires_at": expires_at.isoformat() if expires_at else None,
            },
        )

        return full_key, api_key

    def validate_api_key(
        self, api_key: str, path: Optional[str] = None, ip_address: Optional[str] = None
    ) -> Optional[ApiKey]:
        """
        Validate an API key

        Args:
            api_key: API key to validate
            path: Path being accessed (for path-specific access control)
            ip_address: IP address making the request (for IP restrictions)

        Returns:
            API key object if valid, None otherwise
        """
        try:
            # Hash the key
            key_hash = self._hash_key(api_key)

            # Look up the key ID from the hash
            key_id = self.key_hashes.get(key_hash)
            if not key_id:
                # If key ID is not found by hash, try to find it by prefix
                prefix = api_key.split(".")[0]
                key_id = self.prefix_map.get(prefix)

                if not key_id:
                    logger.warning(f"API key not found: {prefix}...")
                    return None

                # If found by prefix but not by hash, the key is invalid
                logger.warning(f"Invalid API key for prefix: {prefix}...")
                return None

            # Get the API key object
            api_key_obj = self.api_keys.get(key_id)
            if not api_key_obj:
                logger.warning(f"API key object not found for ID: {key_id}")
                return None

            # Check if the key is expired
            if api_key_obj.is_expired():
                logger.warning(f"Expired API key: {key_id}")
                return None

            # Check path access if specified
            if path and not api_key_obj.can_access_path(path):
                logger.warning(f"API key {key_id} not authorized for path: {path}")
                return None

            # Check IP access if specified
            if ip_address and not api_key_obj.can_access_from_ip(ip_address):
                logger.warning(f"API key {key_id} not authorized from IP: {ip_address}")
                return None

            # Update last used timestamp
            api_key_obj.last_used_at = datetime.now()

            return api_key_obj

        except Exception as e:
            logger.error(f"Error validating API key: {str(e)}")
            return None

    def revoke_api_key(self, key_id: str, user_id: str) -> bool:
        """
        Revoke an API key

        Args:
            key_id: ID of the key to revoke
            user_id: ID of the user who owns the key

        Returns:
            True if successful, False otherwise
        """
        # Get the API key
        api_key = self.api_keys.get(key_id)
        if not api_key:
            logger.warning(f"API key not found for revocation: {key_id}")
            return False

        # Check if the user owns the key
        if api_key.user_id != user_id:
            logger.warning(f"User {user_id} does not own API key {key_id}")
            return False

        # Find the hash for this key
        hash_to_remove = None
        for key_hash, mapped_key_id in self.key_hashes.items():
            if mapped_key_id == key_id:
                hash_to_remove = key_hash
                break

        # Find the prefix for this key
        prefix_to_remove = None
        for prefix, mapped_key_id in self.prefix_map.items():
            if mapped_key_id == key_id:
                prefix_to_remove = prefix
                break

        # Remove the key
        if key_id in self.api_keys:
            del self.api_keys[key_id]

        if hash_to_remove and hash_to_remove in self.key_hashes:
            del self.key_hashes[hash_to_remove]

        if prefix_to_remove and prefix_to_remove in self.prefix_map:
            del self.prefix_map[prefix_to_remove]

        # Log the revocation
        log_audit(
            action="revoke_api_key",
            user_id=user_id,
            resource=f"api_key:{key_id}",
        )

        return True

    def get_user_api_keys(self, user_id: str) -> List[ApiKey]:
        """
        Get all API keys for a user

        Args:
            user_id: ID of the user

        Returns:
            List of API key objects
        """
        return [key for key in self.api_keys.values() if key.user_id == user_id]

    def _hash_key(self, api_key: str) -> str:
        """
        Hash an API key for secure storage

        Args:
            api_key: API key to hash

        Returns:
            Hashed API key
        """
        return hmac.new(
            ENCRYPTION_KEY, api_key.encode("utf-8"), hashlib.sha256
        ).hexdigest()

    def encrypt_api_key(self, api_key: str) -> str:
        """
        Encrypt an API key for secure storage

        Args:
            api_key: API key to encrypt

        Returns:
            Encrypted API key
        """
        return cipher.encrypt(api_key.encode("utf-8")).decode("utf-8")

    def decrypt_api_key(self, encrypted_api_key: str) -> str:
        """
        Decrypt an encrypted API key

        Args:
            encrypted_api_key: Encrypted API key

        Returns:
            Decrypted API key
        """
        return cipher.decrypt(encrypted_api_key.encode("utf-8")).decode("utf-8")


# Create global instance
api_key_manager = ApiKeyManager()
