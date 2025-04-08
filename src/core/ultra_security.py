import base64
import hashlib
import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from ultra_config import UltraConfig


@dataclass
class SecurityConfig:
    """Security configuration settings."""

    key_rotation_days: int = 30
    min_key_length: int = 32
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60
    encryption_enabled: bool = True


class APIKeyManager:
    """Manages API keys securely."""

    def __init__(self, config: UltraConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._load_encryption_key()

    def _load_encryption_key(self):
        """Load or generate encryption key."""
        key_file = os.path.join(self.config.cache_dir, ".key")
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            os.makedirs(self.config.cache_dir, exist_ok=True)
            with open(key_file, "wb") as f:
                f.write(self.key)
        self.cipher_suite = Fernet(self.key)

    def encrypt_api_key(self, api_key: str) -> str:
        """Encrypt an API key."""
        try:
            return self.cipher_suite.encrypt(api_key.encode()).decode()
        except Exception as e:
            self.logger.error(f"Failed to encrypt API key: {e}")
            raise

    def decrypt_api_key(self, encrypted_key: str) -> str:
        """Decrypt an API key."""
        try:
            return self.cipher_suite.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            self.logger.error(f"Failed to decrypt API key: {e}")
            raise


class AccessControl:
    """Manages access control and authentication."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.failed_attempts = {}
        self.lockouts = {}
        self.sessions = {}

    def authenticate(self, credentials: Dict[str, str]) -> bool:
        """Authenticate a user or service."""
        user_id = credentials.get("user_id")

        # Check if user is locked out
        if self._is_locked_out(user_id):
            return False

        # Perform authentication
        if self._verify_credentials(credentials):
            self._clear_failed_attempts(user_id)
            self._create_session(user_id)
            return True

        self._record_failed_attempt(user_id)
        return False

    def _is_locked_out(self, user_id: str) -> bool:
        """Check if a user is locked out."""
        if user_id in self.lockouts:
            lockout_time = self.lockouts[user_id]
            if datetime.now() < lockout_time:
                return True
            del self.lockouts[user_id]
        return False

    def _record_failed_attempt(self, user_id: str):
        """Record a failed authentication attempt."""
        if user_id not in self.failed_attempts:
            self.failed_attempts[user_id] = 1
        else:
            self.failed_attempts[user_id] += 1

        if self.failed_attempts[user_id] >= self.config.max_failed_attempts:
            self.lockouts[user_id] = datetime.now() + timedelta(
                minutes=self.config.lockout_duration_minutes
            )

    def _verify_credentials(self, credentials: Dict[str, str]) -> bool:
        """Verify authentication credentials."""
        # Implement your credential verification logic here
        return True  # Placeholder

    def _create_session(self, user_id: str):
        """Create a new session for authenticated user."""
        session_id = base64.b64encode(os.urandom(32)).decode()
        self.sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now()
            + timedelta(minutes=self.config.session_timeout_minutes),
        }
        return session_id


class DataEncryption:
    """Handles data encryption and decryption."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize encryption components."""
        self.salt = os.urandom(16)
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )

    def encrypt_data(self, data: Any) -> bytes:
        """Encrypt data."""
        if not self.config.encryption_enabled:
            return data

        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            key = base64.urlsafe_b64encode(self.kdf.derive(os.urandom(32)))
            f = Fernet(key)
            return f.encrypt(str(data).encode())
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            raise

    def decrypt_data(self, encrypted_data: bytes) -> Any:
        """Decrypt data."""
        if not self.config.encryption_enabled:
            return encrypted_data

        try:
            key = base64.urlsafe_b64encode(self.kdf.derive(os.urandom(32)))
            f = Fernet(key)
            decrypted = f.decrypt(encrypted_data)
            try:
                return json.loads(decrypted)
            except json.JSONDecodeError:
                return decrypted.decode()
        except Exception as e:
            self.logger.error(f"Failed to decrypt data: {e}")
            raise


class AuditLogger:
    """Logs security-related events."""

    def __init__(self, config: UltraConfig):
        self.config = config
        self.logger = logging.getLogger("security_audit")
        self._setup_audit_logging()

    def _setup_audit_logging(self):
        """Setup audit logging configuration."""
        audit_log = os.path.join(self.config.log_file, "security_audit.log")
        handler = logging.FileHandler(audit_log)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log a security event."""
        self.logger.info(f"Security Event - Type: {event_type} - Details: {details}")

    def log_access_attempt(self, user_id: str, success: bool, ip_address: str):
        """Log an access attempt."""
        self.logger.info(
            f"Access Attempt - User: {user_id} - Success: {success} - IP: {ip_address}"
        )

    def log_api_access(self, api_name: str, user_id: str, status_code: int):
        """Log an API access."""
        self.logger.info(
            f"API Access - API: {api_name} - User: {user_id} - Status: {status_code}"
        )
