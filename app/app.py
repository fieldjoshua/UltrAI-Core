from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes.health_routes import router as health_router
from app.routes.user_routes import user_router
from app.config_cors import get_cors_config
from app.utils.logging import get_logger

logger = get_logger("test_app_setup")


def create_app() -> FastAPI:
    """Create a minimal FastAPI application with health and user routes."""
    app = FastAPI()

    # Add CORS middleware
    cors_config = get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
        expose_headers=cors_config["expose_headers"],
        max_age=cors_config["max_age"],
    )
    # Include initial routers
    app.include_router(health_router)
    app.include_router(user_router, prefix="/api")
    # Include all main application routers
    from app.routes.auth_routes import auth_router
    from app.routes.document_routes import document_router
    from app.routes.analyze_routes import analyze_router
    from app.routes.orchestrator_minimal import router as orchestrator_router
    from app.routes.llm_routes import llm_router
    from app.routes.document_analysis_routes import document_analysis_router
    from app.routes.docker_modelrunner_routes import router as docker_modelrunner_router
    from app.routes.available_models_routes import router as available_models_router
    from app.routes.pricing_routes import pricing_router
    from app.routes.oauth_routes import oauth_router
    from app.routes.recovery_routes import recovery_router
    from app.routes.debug_routes import router as debug_router
    from app.routes.debug_env_routes import router as debug_env_router
    from app.routes.metrics import metrics_router
    from app.routes.model_availability_routes import router as model_availability_router

    # Register API routers under /api prefix
    api_prefix = "/api"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(document_router, prefix=api_prefix)
    app.include_router(analyze_router, prefix=api_prefix)
    app.include_router(orchestrator_router, prefix=api_prefix)
    app.include_router(llm_router, prefix=api_prefix)
    app.include_router(document_analysis_router, prefix=api_prefix)
    app.include_router(docker_modelrunner_router, prefix=api_prefix)
    app.include_router(available_models_router, prefix=api_prefix)
    app.include_router(pricing_router, prefix=api_prefix)
    app.include_router(oauth_router, prefix=api_prefix)
    app.include_router(recovery_router, prefix=api_prefix)
    app.include_router(debug_router, prefix=api_prefix)
    app.include_router(debug_env_router, prefix=api_prefix)
    app.include_router(metrics_router, prefix=api_prefix)
    app.include_router(model_availability_router, prefix=api_prefix)

    # Expose orchestrator routes at root (no /api prefix) in addition to /api prefix
    # This allows frontend clients to call either path depending on deployment config.
    app.include_router(orchestrator_router)  # mounts at /orchestrator/*

    # In TESTING mode, ensure orchestrator service exists so routes work without full production init
    if os.getenv("TESTING") == "true" and not hasattr(
        app.state, "orchestration_service"
    ):
        try:
            from app.services.orchestration_service import OrchestrationService
            from app.services.rate_limiter import RateLimiter
            from unittest.mock import Mock

            app.state.orchestration_service = OrchestrationService(
                model_registry=Mock(), rate_limiter=RateLimiter()
            )
            logger.info(
                "🧪 TESTING mode – lightweight OrchestrationService attached to app.state"
            )
        except Exception as exc:
            logger.error(f"Failed to attach testing orchestration service: {exc}")

    # Serve frontend static files
    frontend_dist = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "frontend", "dist"
    )
    if os.path.exists(frontend_dist):
        # Mount static assets at root to serve JS/CSS files properly
        app.mount(
            "/assets",
            StaticFiles(directory=os.path.join(frontend_dist, "assets")),
            name="assets",
        )

        @app.get("/")
        async def serve_frontend():
            """Serve the React frontend"""
            index_file = os.path.join(frontend_dist, "index.html")
            if os.path.exists(index_file):
                return FileResponse(index_file)
            return {"message": "Frontend not built. Run 'cd frontend && npm run build'"}

        @app.get("/{path:path}")
        async def serve_frontend_routes(path: str):
            """Serve React app for all non-API routes (SPA routing)"""
            # Don't intercept API routes or assets
            if (
                path.startswith("api/")
                or path.startswith("docs")
                or path.startswith("health")
                or path.startswith("assets/")
            ):
                return {"error": "Route not found"}

            # Serve index.html for all other routes (React Router handles client-side routing)
            index_file = os.path.join(frontend_dist, "index.html")
            if os.path.exists(index_file):
                return FileResponse(index_file)
            return {"message": "Frontend not built"}

    return app
