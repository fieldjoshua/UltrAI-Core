"""Compatibility shim for legacy imports.

Re-exports authentication helpers from combined_auth_middleware so tests
and older modules importing app.middleware.auth_middleware continue to work.
"""

from .combined_auth_middleware import require_auth, AuthUser  # noqa: F401

__all__ = ["require_auth", "AuthUser"]


