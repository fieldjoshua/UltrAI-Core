from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes.health_routes import router as health_router
from app.routes.user_routes import user_router
from app.config_cors import get_cors_config
from app.config import Config
from app.middleware.combined_auth_middleware import setup_combined_auth_middleware
from app.middleware.rate_limit_middleware import setup_rate_limit_middleware
from app.middleware.security_headers_middleware import setup_security_headers_middleware
from app.middleware.telemetry_middleware import setup_telemetry_middleware
from app.middleware.request_id_middleware import setup_request_id_middleware
from app.middleware.performance_middleware import setup_performance_middleware
from app.utils.logging import get_logger
from app.utils.structured_logging import (
    setup_structured_logging_middleware as setup_structured_logging,
    apply_structured_logging_middleware as apply_structured_logging,
)
from app.database.connection import init_db
from app.services.model_selection_service import SmartModelSelectionService

logger = get_logger("test_app_setup")


def create_app() -> FastAPI:
    """Create a minimal FastAPI application with health and user routes."""
    app = FastAPI()

    # Add CORS middleware with flexible configuration
    cors_config = get_cors_config()

    # In production, never use wildcard; rely on configured origins
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "production":
        allow_origins = cors_config["allow_origins"]
    else:
        allow_origins = ["*"] if os.getenv("RENDER") else cors_config["allow_origins"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
        expose_headers=cors_config["expose_headers"],
        max_age=cors_config["max_age"],
    )

    # Add security headers (CSP/HSTS/etc.)
    setup_security_headers_middleware(
        app,
        csp_directives={
            "default-src": "'self'",
            "script-src": "'self'",
            # Allow inline styles for initial loader and style attributes set by React
            "style-src": "'self' 'unsafe-inline' https://fonts.googleapis.com",
            "img-src": "'self' data:",
            "font-src": "'self' https://fonts.gstatic.com",
            "connect-src": "'self'",
            "frame-src": "'none'",
            "object-src": "'none'",
            "base-uri": "'self'",
            "form-action": "'self'",
        },
        exclude_paths=[
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/swagger-ui",
        ],
    )

    # Correlation IDs
    setup_request_id_middleware(app)
    
    # Performance optimizations (compression, caching headers)
    try:
        setup_performance_middleware(app)
        logger.info("Performance optimization middleware enabled")
    except Exception:
        logger.error("Failed to enable performance middleware", exc_info=True)

    # Initialize database session (uses fallback if DB is unavailable)
    try:
        init_db()
        logger.info("Database initialized (or fallback active)")
    except Exception:
        logger.error("Database initialization failed", exc_info=True)

    # Security headers already configured above; avoid duplicate middleware that can override CSP

    # Structured request logging (with sampling and correlation IDs)
    try:
        setup_structured_logging(app)
        apply_structured_logging(app)
        logger.info("Structured logging middleware enabled")
    except Exception:
        logger.error("Failed to enable structured logging middleware", exc_info=True)

    # Telemetry middleware (OpenTelemetry traces and metrics)
    try:
        setup_telemetry_middleware(app)
        logger.info("Telemetry middleware enabled")
    except Exception:
        logger.error("Failed to enable telemetry middleware", exc_info=True)

    # Add authentication middleware if enabled
    if Config.ENABLE_AUTH:
        # Define public paths (no authentication required)
        public_paths = [
            "/health",
            "/api/health",
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/refresh",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/analyze",  # Temporarily public for testing
            "/api/orchestrator",  # Temporarily public for testing
            "/api/available-models",  # Public for model discovery
            "/api/pricing",  # Public for pricing info
        ]

        # Protected paths that require authentication
        protected_paths = [
            "/api/admin",
            "/api/debug",
        ]

        # Setup combined authentication middleware
        setup_combined_auth_middleware(app, public_paths=public_paths, protected_paths=protected_paths)
        logger.info("Authentication middleware enabled (JWT + API Key support)")

    # Add rate limiting middleware if enabled
    if Config.ENABLE_RATE_LIMIT:
        # Exclude paths from rate limiting
        excluded_paths = [
            "/health",
            "/api/health",
            "/api/docs",
            "/api/redoc",
            "/api/openapi.json",
            "/api/metrics",
        ]

        # Setup rate limiting middleware
        setup_rate_limit_middleware(app, excluded_paths=excluded_paths)
        logger.info("Rate limiting middleware enabled")

    # Include initial routers (mounted under API prefix below)
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
    from app.routes.cache_routes import router as cache_router
    from app.routes.test_env_routes import router as test_env_router

    # Register API routers under /api prefix
    api_prefix = "/api"
    app.include_router(health_router, prefix=api_prefix)
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
    app.include_router(cache_router, prefix=api_prefix)
    app.include_router(test_env_router, prefix=api_prefix)

    # Enforce single /api prefix (no root mount for orchestrator)

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

    # Initialize shared services (e.g., smart model selection)
    try:
        if not hasattr(app.state, "services"):
            app.state.services = {}
        app.state.services["model_selector"] = SmartModelSelectionService()
        logger.info("SmartModelSelectionService initialized")
    except Exception:
        logger.error("Failed to initialize SmartModelSelectionService", exc_info=True)

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

        @app.get("/wizard_steps.json")
        async def serve_wizard_steps_json():
            """Serve wizard steps JSON from the built frontend directory."""
            json_file = os.path.join(frontend_dist, "wizard_steps.json")
            if os.path.exists(json_file):
                return FileResponse(json_file, media_type="application/json")
            return {"error": "wizard_steps.json not found"}

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

    # Correlate requests with X-Request-ID
    @app.middleware("http")
    async def request_id_middleware(request, call_next):
        try:
            import uuid
            request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
            # Process request
            response = await call_next(request)
            # Echo header
            try:
                response.headers["X-Request-ID"] = request_id
            except Exception:
                pass
            return response
        except Exception:
            # Ensure a response even if middleware fails
            from starlette.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "status": "error",
                    "message": "Unhandled error",
                    "code": "INTERNAL",
                },
                headers={"X-Request-ID": request.headers.get("X-Request-ID", "unknown")},
            )

    return app
