from fastapi import APIRouter

from app.api.api_v1.endpoints.users import router as users_router
from app.api.api_v1.endpoints.auth import router as auth_router

api_router = APIRouter()

# Import and include other routers here
# Example:
# from app.api.api_v1.endpoints import users, auth, chat
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
# api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

# Include routers
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router)
