"""
Test JWT secret environment variable aliasing.
"""

import os
import pytest
from unittest.mock import patch


def test_jwt_secret_key_precedence():
    """Test that JWT_SECRET_KEY takes precedence over JWT_SECRET"""
    # Clear any existing env vars
    env_backup = {}
    for key in ["JWT_SECRET_KEY", "JWT_SECRET", "JWT_REFRESH_SECRET_KEY", "JWT_REFRESH_SECRET"]:
        if key in os.environ:
            env_backup[key] = os.environ[key]
            del os.environ[key]
    
    try:
        # Test 1: Only JWT_SECRET_KEY set
        os.environ["JWT_SECRET_KEY"] = "key-version"
        os.environ["JWT_REFRESH_SECRET_KEY"] = "refresh-key-version"
        
        # Re-import to get fresh values
        import importlib
        import app.utils.jwt_utils
        importlib.reload(app.utils.jwt_utils)
        
        assert app.utils.jwt_utils.SECRET_KEY == "key-version"
        assert app.utils.jwt_utils.REFRESH_SECRET_KEY == "refresh-key-version"
        
        # Test 2: Both set - KEY should take precedence
        os.environ["JWT_SECRET"] = "secret-version"
        os.environ["JWT_REFRESH_SECRET"] = "refresh-secret-version"
        
        importlib.reload(app.utils.jwt_utils)
        
        assert app.utils.jwt_utils.SECRET_KEY == "key-version"
        assert app.utils.jwt_utils.REFRESH_SECRET_KEY == "refresh-key-version"
        
        # Test 3: Only JWT_SECRET set
        del os.environ["JWT_SECRET_KEY"]
        del os.environ["JWT_REFRESH_SECRET_KEY"]
        
        importlib.reload(app.utils.jwt_utils)
        
        assert app.utils.jwt_utils.SECRET_KEY == "secret-version"
        assert app.utils.jwt_utils.REFRESH_SECRET_KEY == "refresh-secret-version"
        
    finally:
        # Restore original env vars
        for key in ["JWT_SECRET_KEY", "JWT_SECRET", "JWT_REFRESH_SECRET_KEY", "JWT_REFRESH_SECRET"]:
            if key in os.environ:
                del os.environ[key]
        for key, value in env_backup.items():
            os.environ[key] = value


def test_jwt_refresh_secret_fallback():
    """Test that refresh secret falls back to main secret + _REFRESH if not provided"""
    with patch.dict('os.environ', {'JWT_SECRET_KEY': 'main-secret'}, clear=True):
        import importlib
        import app.utils.jwt_utils
        importlib.reload(app.utils.jwt_utils)
        
        assert app.utils.jwt_utils.SECRET_KEY == "main-secret"
        assert app.utils.jwt_utils.REFRESH_SECRET_KEY == "main-secret_REFRESH"


def test_jwt_missing_secret_raises_error():
    """Test that missing JWT secret raises ValueError"""
    with patch.dict('os.environ', {}, clear=True):
        import importlib
        import app.utils.jwt_utils
        
        with pytest.raises(ValueError, match="JWT_SECRET_KEY or JWT_SECRET"):
            importlib.reload(app.utils.jwt_utils)