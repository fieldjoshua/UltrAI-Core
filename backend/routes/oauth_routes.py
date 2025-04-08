"""
OAuth routes for the Ultra backend.

This module provides API routes for OAuth authentication with external providers.
"""

import logging
from typing import Union
from uuid import uuid4

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session

from backend.database.connection import get_db
from backend.database.repositories.user import UserRepository
from backend.models.oauth import (OAuthCodeRequest, OAuthError,
                                  OAuthURLResponse)
from backend.models.user import TokenResponse
from backend.services.auth_service import auth_service
from backend.services.oauth_service import oauth_service

# Create a router
oauth_router = APIRouter(tags=["OAuth"])

# Set up logging
logger = logging.getLogger("oauth_routes")

# Create repositories
user_repository = UserRepository()


@oauth_router.get("/api/auth/{provider}/login",
                   response_model=Union[OAuthURLResponse, OAuthError])
async def oauth_login(provider: str):
    """
    Generate OAuth login URL for the specified provider

    Args:
        provider: The OAuth provider ("google" or "github")

    Returns:
        OAuthURLResponse with authorization URL and state token
    """
    try:
        result = await oauth_service.generate_oauth_url(provider)

        if "error" in result:
            return JSONResponse(
                status_code=400,
                content={"error": result["error"]}
            )

        return {"url": result["url"], "state": result["state"]}

    except Exception as e:
        logger.error(f"Error generating OAuth URL: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error generating OAuth URL: {str(e)}"}
        )


@oauth_router.get("/api/auth/{provider}/callback")
async def oauth_callback(
    request: Request,
    provider: str,
    code: str = Query(None),
    state: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from provider

    Args:
        request: FastAPI request object
        provider: The OAuth provider ("google" or "github")
        code: The authorization code from the provider
        state: The state token for verification
        db: Database session

    Returns:
        Redirect to frontend with access token or error
    """
    try:
        # Validate required parameters
        if not code or not state:
            error_params = "error=Missing required parameters"
            return RedirectResponse(url=f"/auth/error?{error_params}")

        # Exchange code for token and user info
        result = await oauth_service.exchange_code_for_token(provider, code, state)

        if "error" in result:
            # Redirect to frontend with error
            error_params = f"error={result['error']}"
            return RedirectResponse(url=f"/auth/error?{error_params}")

        # Map provider user to our user format
        user_info = result["user_info"]

        # Check if user exists by OAuth ID
        db_user = user_repository.get_by_oauth(db, provider, user_info.get("sub") or str(user_info.get("id")))

        if not db_user:
            # Check if user exists by email
            email = user_info.get("email")
            if email:
                db_user = user_repository.get_by_email(db, email)

            if not db_user:
                # Create new user
                user_data = await oauth_service.map_provider_user_to_db_user(provider, user_info)

                # Generate random username if email exists
                if user_data.get("email"):
                    username = user_data["email"].split("@")[0] + str(uuid4())[:8]
                    user_data["username"] = username

                # Set default values for new user
                user_data["password_hash"] = "OAuth_USER_NO_PASSWORD_" + str(uuid4())
                user_data["is_active"] = True
                user_data["is_verified"] = True  # OAuth users are pre-verified

                # Create user in database
                db_user = user_repository.create(db, user_data)
            else:
                # Update existing user with OAuth info
                user_data = await oauth_service.map_provider_user_to_db_user(provider, user_info)
                user_repository.update(
                    db,
                    db_obj=db_user,
                    obj_in={
                        "oauth_provider": user_data["oauth_provider"],
                        "oauth_id": user_data["oauth_id"],
                    }
                )

        # Create access token
        token = auth_service.create_access_token(str(db_user.id))

        # Redirect to frontend with token
        token_params = f"access_token={token['access_token']}&token_type=bearer&expires_in={token['expires_in']}"
        return RedirectResponse(url=f"/auth/success?{token_params}")

    except Exception as e:
        logger.error(f"Error in OAuth callback: {str(e)}")
        # Redirect to frontend with error
        return RedirectResponse(url="/auth/error?error=Internal+server+error")


@oauth_router.post("/api/auth/{provider}/token", response_model=Union[TokenResponse, OAuthError])
async def oauth_token(
    provider: str,
    request: OAuthCodeRequest,
    db: Session = Depends(get_db)
):
    """
    Exchange OAuth code for access token (for native/mobile apps)

    Args:
        provider: The OAuth provider ("google" or "github")
        request: OAuth code request
        db: Database session

    Returns:
        TokenResponse with access token
    """
    try:
        # Exchange code for token and user info
        result = await oauth_service.exchange_code_for_token(provider, request.code, request.state)

        if "error" in result:
            return JSONResponse(
                status_code=400,
                content={"error": result["error"]}
            )

        # Map provider user to our user format
        user_info = result["user_info"]

        # Check if user exists by OAuth ID
        db_user = user_repository.get_by_oauth(db, provider, user_info.get("sub") or str(user_info.get("id")))

        if not db_user:
            # Check if user exists by email
            email = user_info.get("email")
            if email:
                db_user = user_repository.get_by_email(db, email)

            if not db_user:
                # Create new user
                user_data = await oauth_service.map_provider_user_to_db_user(provider, user_info)

                # Generate random username if email exists
                if user_data.get("email"):
                    username = user_data["email"].split("@")[0] + str(uuid4())[:8]
                    user_data["username"] = username

                # Set default values for new user
                user_data["password_hash"] = "OAuth_USER_NO_PASSWORD_" + str(uuid4())
                user_data["is_active"] = True
                user_data["is_verified"] = True  # OAuth users are pre-verified

                # Create user in database
                db_user = user_repository.create(db, user_data)
            else:
                # Update existing user with OAuth info
                user_data = await oauth_service.map_provider_user_to_db_user(provider, user_info)
                user_repository.update(
                    db,
                    db_obj=db_user,
                    obj_in={
                        "oauth_provider": user_data["oauth_provider"],
                        "oauth_id": user_data["oauth_id"],
                    }
                )

        # Create access token
        token = auth_service.create_access_token(str(db_user.id))

        # Return token response
        return token

    except Exception as e:
        logger.error(f"Error in OAuth token exchange: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error in OAuth token exchange: {str(e)}"}
        )