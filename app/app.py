from fastapi import FastAPI
from app.routes.health_routes import router as health_router
from app.routes.user_routes import user_router


def create_app() -> FastAPI:
    """Create a minimal FastAPI application with health and user routes."""
    app = FastAPI()
    app.include_router(health_router)
    app.include_router(user_router, prefix="/api")
    return app
