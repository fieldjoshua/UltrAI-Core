"""
OAuth service for the Ultra backend.

This module provides OAuth integration for authentication with external providers
such as Google and GitHub.
"""

import os
import secrets
from typing import Any, Dict
from urllib.parse import urlencode

import httpx

from backend.utils.logging import get_logger

# Set up logger
logger = get_logger("oauth_service", "logs/oauth.log")

# OAuth provider configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:8000/api/auth/google/callback"
)

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
GITHUB_REDIRECT_URI = os.getenv(
    "GITHUB_REDIRECT_URI", "http://localhost:8000/api/auth/github/callback"
)

# OAuth state token storage
# In production, this should be stored in Redis or another distributed cache
oauth_states = {}


class OAuthService:
    """Service for OAuth authentication with external providers"""

    async def generate_oauth_url(self, provider: str) -> Dict[str, Any]:
        """
        Generate the OAuth URL for the specified provider

        Args:
            provider: The OAuth provider ("google" or "github")

        Returns:
            Dict containing the authorization URL and state token
        """
        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)

        if provider == "google":
            if not GOOGLE_CLIENT_ID:
                return {"error": "Google OAuth is not configured"}

            # Store state token
            oauth_states[state] = {"provider": "google"}

            # Build Google OAuth URL
            params = {
                "client_id": GOOGLE_CLIENT_ID,
                "redirect_uri": GOOGLE_REDIRECT_URI,
                "response_type": "code",
                "scope": "openid email profile",
                "state": state,
                "access_type": "offline",
                "prompt": "consent",
            }
            auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(params)}"
            return {"url": auth_url, "state": state}

        elif provider == "github":
            if not GITHUB_CLIENT_ID:
                return {"error": "GitHub OAuth is not configured"}

            # Store state token
            oauth_states[state] = {"provider": "github"}

            # Build GitHub OAuth URL
            params = {
                "client_id": GITHUB_CLIENT_ID,
                "redirect_uri": GITHUB_REDIRECT_URI,
                "scope": "user:email",
                "state": state,
            }
            auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
            return {"url": auth_url, "state": state}

        else:
            return {"error": f"Unsupported OAuth provider: {provider}"}

    async def validate_oauth_state(self, state: str) -> bool:
        """
        Validate the OAuth state token

        Args:
            state: The state token to validate

        Returns:
            True if the state token is valid, False otherwise
        """
        return state in oauth_states

    async def exchange_code_for_token(
        self, provider: str, code: str, state: str
    ) -> Dict[str, Any]:
        """
        Exchange the authorization code for an access token

        Args:
            provider: The OAuth provider ("google" or "github")
            code: The authorization code from the OAuth provider
            state: The state token for verification

        Returns:
            Dict containing the access token and user information
        """
        # Verify state token
        if not await self.validate_oauth_state(state):
            return {"error": "Invalid state token"}

        # Get stored state info and remove it
        state_info = oauth_states.pop(state, None)
        if not state_info or state_info.get("provider") != provider:
            return {"error": "Invalid OAuth flow"}

        try:
            # Exchange code for token based on provider
            if provider == "google":
                token_data = await self._exchange_google_code(code)
                if "error" in token_data:
                    return token_data

                # Get user info from Google
                user_info = await self._get_google_user_info(token_data["access_token"])
                return {
                    "token": token_data,
                    "user_info": user_info,
                    "provider": "google",
                }

            elif provider == "github":
                token_data = await self._exchange_github_code(code)
                if "error" in token_data:
                    return token_data

                # Get user info from GitHub
                user_info = await self._get_github_user_info(token_data["access_token"])
                return {
                    "token": token_data,
                    "user_info": user_info,
                    "provider": "github",
                }

            else:
                return {"error": f"Unsupported OAuth provider: {provider}"}

        except Exception as e:
            logger.error(f"Error exchanging OAuth code: {str(e)}")
            return {"error": f"Error exchanging OAuth code: {str(e)}"}

    async def _exchange_google_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange Google authorization code for access token

        Args:
            code: The authorization code from Google

        Returns:
            Dict containing the access token
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": GOOGLE_CLIENT_ID,
                        "client_secret": GOOGLE_CLIENT_SECRET,
                        "code": code,
                        "redirect_uri": GOOGLE_REDIRECT_URI,
                        "grant_type": "authorization_code",
                    },
                    headers={"Accept": "application/json"},
                )

                if response.status_code != 200:
                    logger.error(f"Google OAuth error: {response.text}")
                    return {"error": f"Google OAuth error: {response.status_code}"}

                return response.json()

            except Exception as e:
                logger.error(f"Error exchanging Google code: {str(e)}")
                return {"error": f"Error exchanging Google code: {str(e)}"}

    async def _get_google_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from Google using the access token

        Args:
            access_token: The OAuth access token

        Returns:
            Dict containing user information
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"},
                )

                if response.status_code != 200:
                    logger.error(f"Google user info error: {response.text}")
                    return {"error": f"Google user info error: {response.status_code}"}

                return response.json()

            except Exception as e:
                logger.error(f"Error getting Google user info: {str(e)}")
                return {"error": f"Error getting Google user info: {str(e)}"}

    async def _exchange_github_code(self, code: str) -> Dict[str, Any]:
        """
        Exchange GitHub authorization code for access token

        Args:
            code: The authorization code from GitHub

        Returns:
            Dict containing the access token
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://github.com/login/oauth/access_token",
                    data={
                        "client_id": GITHUB_CLIENT_ID,
                        "client_secret": GITHUB_CLIENT_SECRET,
                        "code": code,
                        "redirect_uri": GITHUB_REDIRECT_URI,
                    },
                    headers={"Accept": "application/json"},
                )

                if response.status_code != 200:
                    logger.error(f"GitHub OAuth error: {response.text}")
                    return {"error": f"GitHub OAuth error: {response.status_code}"}

                return response.json()

            except Exception as e:
                logger.error(f"Error exchanging GitHub code: {str(e)}")
                return {"error": f"Error exchanging GitHub code: {str(e)}"}

    async def _get_github_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user information from GitHub using the access token

        Args:
            access_token: The OAuth access token

        Returns:
            Dict containing user information
        """
        async with httpx.AsyncClient() as client:
            try:
                # Get user profile
                profile_response = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                    },
                )

                if profile_response.status_code != 200:
                    logger.error(f"GitHub user info error: {profile_response.text}")
                    return {
                        "error": f"GitHub user info error: {profile_response.status_code}"
                    }

                profile = profile_response.json()

                # Get user email (might be private)
                email_response = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Accept": "application/vnd.github.v3+json",
                    },
                )

                if email_response.status_code == 200:
                    emails = email_response.json()
                    primary_email = next((e for e in emails if e.get("primary")), None)
                    if primary_email:
                        profile["email"] = primary_email["email"]

                return profile

            except Exception as e:
                logger.error(f"Error getting GitHub user info: {str(e)}")
                return {"error": f"Error getting GitHub user info: {str(e)}"}

    async def map_provider_user_to_db_user(
        self, provider: str, user_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Map OAuth provider user information to database user format

        Args:
            provider: The OAuth provider ("google" or "github")
            user_info: The user information from the OAuth provider

        Returns:
            Dict containing mapped user data
        """
        if provider == "google":
            return {
                "email": user_info.get("email"),
                "name": user_info.get("name"),
                "oauth_provider": "google",
                "oauth_id": user_info.get("sub"),
                "picture": user_info.get("picture"),
            }

        elif provider == "github":
            return {
                "email": user_info.get("email"),
                "name": user_info.get("name") or user_info.get("login"),
                "oauth_provider": "github",
                "oauth_id": str(user_info.get("id")),
                "picture": user_info.get("avatar_url"),
            }

        else:
            logger.error(f"Unsupported OAuth provider: {provider}")
            return {}


# Create a global instance
oauth_service = OAuthService()
