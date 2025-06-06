"""
OAuth models for the Ultra backend.

This module defines Pydantic models for OAuth authentication requests and responses.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel


class OAuthURLResponse(BaseModel):
    """Response model for OAuth URL generation"""

    url: str
    state: str


class OAuthError(BaseModel):
    """Error response model for OAuth operations"""

    error: str
    details: Optional[Dict[str, Any]] = None


class OAuthCodeRequest(BaseModel):
    """Request model for OAuth code exchange"""

    code: str
    state: str


class OAuthUserInfo(BaseModel):
    """User information from OAuth provider"""

    provider: str
    email: str
    name: Optional[str] = None
    oauth_id: str
    picture: Optional[str] = None


class OAuthAccessToken(BaseModel):
    """OAuth access token information"""

    access_token: str
    token_type: str
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class OAuthResponse(BaseModel):
    """Response model for successful OAuth authentication"""

    user_info: OAuthUserInfo
    access_token: str
    token_type: str = "bearer"
    expires_in: int
