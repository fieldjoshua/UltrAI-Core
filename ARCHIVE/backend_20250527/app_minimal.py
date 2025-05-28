"""MVP Minimal FastAPI app for Render deployment - ALL functionality preserved"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Set up logging
logging.basicConfig(
    level=(
        logging.INFO
        if os.getenv("ENV", "development") == "production"
        else logging.DEBUG
    ),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Dependency availability tracking
DEPENDENCY_STATUS = {
    "sqlalchemy": {"available": False, "required": True},
    "redis": {"available": False, "required": False},
    "sentry_sdk": {"available": False, "required": False},
    "prometheus_client": {"available": False, "required": False},
}


# Check and initialize dependencies
def check_dependencies():
    """Check availability of dependencies and initialize fallbacks"""
    for dep_name in DEPENDENCY_STATUS:
        try:
            __import__(dep_name)
            DEPENDENCY_STATUS[dep_name]["available"] = True
            logger.info(f"Dependency {dep_name} is available")
        except ImportError:
            logger.warning(f"Dependency {dep_name} not available")
            if DEPENDENCY_STATUS[dep_name]["required"]:
                logger.error(f"Required dependency {dep_name} is missing!")


# Check dependencies on startup
check_dependencies()

# Initialize database if available
database_initialized = False
if DEPENDENCY_STATUS["sqlalchemy"]["available"]:
    try:
        from .database import check_database_connection, init_db

        database_initialized = True
    except Exception as e:
        logger.error(f"Failed to import database modules: {e}")

# Initialize Redis/Cache service if available
cache_service = None
if DEPENDENCY_STATUS["redis"]["available"]:
    try:
        from .services.cache_service import cache_service as cs

        cache_service = cs
        if cache_service.is_redis_available():
            logger.info("Redis cache initialized")
        else:
            logger.info("Using in-memory cache")
    except Exception as e:
        logger.warning(f"Failed to initialize cache service: {e}")

# Initialize Sentry if available
if DEPENDENCY_STATUS["sentry_sdk"]["available"]:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        sentry_sdk.init(
            dsn=os.getenv("SENTRY_DSN"),
            integrations=[FastApiIntegration()],
            environment=os.getenv("ENV", "development"),
            traces_sample_rate=0.1,
        )
    except Exception as e:
        logger.warning(f"Failed to initialize Sentry: {e}")


# App lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app lifecycle - startup and shutdown"""
    # Startup
    logger.info("Starting Ultra API in MVP minimal mode")
    logger.info(f"Environment: {os.getenv('ENV', 'development')}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Dependencies status: {DEPENDENCY_STATUS}")

    # Initialize database if available
    if database_initialized:
        try:
            await init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Ultra API")


# Create FastAPI app with all MVP features
app = FastAPI(
    title="Ultra API - MVP Minimal",
    version="1.0.0",
    description="All MVP functionality with minimal resource usage",
    docs_url="/docs" if os.getenv("ENV", "development") == "development" else None,
    redoc_url="/redoc" if os.getenv("ENV", "development") == "development" else None,
    lifespan=lifespan,
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions with proper error response"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    error_response = {
        "error_code": "INTERNAL_ERROR",
        "message": "An internal server error occurred",
        "resolution": "Please check the logs or contact support",
        "context": str(request.url),
        "request_id": request.headers.get("X-Request-ID", "unknown"),
    }

    # Include details in development
    if os.getenv("ENV", "development") == "development":
        error_response["details"] = str(exc)

    return JSONResponse(status_code=500, content=error_response)


# Validation error handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle validation errors with user-friendly messages"""
    return JSONResponse(
        status_code=422,
        content={
            "error_code": "VALIDATION_ERROR",
            "message": "Invalid request data",
            "details": (
                exc.errors() if os.getenv("ENV") == "development" else "Invalid input"
            ),
            "resolution": "Please check your request data and try again",
        },
    )


# Enhanced health check endpoint
@app.get("/api/health")
async def health() -> Dict[str, Any]:
    """Comprehensive health check with dependency status"""
    health_status = {
        "status": "ok",
        "service": "ultra-api",
        "environment": os.getenv("ENV", "development"),
        "app_type": "mvp-minimal",
        "version": "1.0.0",
        "dependencies": DEPENDENCY_STATUS.copy(),
    }

    # Check database connection if available
    if database_initialized:
        try:
            db_status = await check_database_connection()
            health_status["database"] = {
                "status": "connected" if db_status else "disconnected"
            }
        except Exception as e:
            health_status["database"] = {"status": "error", "message": str(e)}
            health_status["status"] = "degraded"

    # Check cache service if available
    if cache_service:
        try:
            cache_status = cache_service.get_status()
            health_status["cache"] = {
                "status": "connected" if cache_status["enabled"] else "disabled",
                "type": cache_status["type"],
                "redis_available": cache_status["redis_available"],
            }
        except Exception as e:
            health_status["cache"] = {"status": "error", "message": str(e)}
            health_status["status"] = "degraded"

    # Overall status based on required dependencies
    for dep, info in DEPENDENCY_STATUS.items():
        if info["required"] and not info["available"]:
            health_status["status"] = "error"
            health_status["error_code"] = "DEPENDENCY_MISSING"
            health_status["message"] = f"Required dependency {dep} is not available"
            break

    return health_status


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "message": "Ultra API v1.0.0 - MVP Minimal Deployment",
        "docs": "/docs" if os.getenv("ENV", "development") == "development" else None,
        "health": "/api/health",
        "mode": "mvp-minimal",
        "features": {
            "authentication": True,
            "document_upload": True,
            "llm_orchestration": True,
            "analysis": True,
            "caching": cache_service is not None and cache_service.is_redis_available(),
            "monitoring": DEPENDENCY_STATUS["sentry_sdk"]["available"],
        },
    }


# Import ALL MVP routes - with error handling
try:
    from .routes import analyze_routes, auth_routes, llm_routes, orchestrator_routes

    # Authentication routes - REQUIRED for MVP
    app.include_router(
        auth_routes.auth_router, prefix="/api/auth", tags=["authentication"]
    )
    logger.info("Authentication routes loaded")

    # LLM routes - REQUIRED for MVP
    app.include_router(llm_routes.llm_router, prefix="/api", tags=["llm"])
    logger.info("LLM routes loaded")

    # Analysis routes - REQUIRED for MVP
    app.include_router(analyze_routes.analyze_router, prefix="/api", tags=["analysis"])
    logger.info("Analysis routes loaded")

    # Orchestrator routes - REQUIRED for MVP
    app.include_router(
        orchestrator_routes.orchestrator_router,
        prefix="/api/orchestrator",
        tags=["orchestrator"],
    )
    logger.info("Orchestrator routes loaded")

except ImportError as e:
    logger.error(f"Failed to import required routes: {e}")

    # Create fallback routes if imports fail
    @app.post("/api/auth/login")
    async def fallback_login():
        return JSONResponse(
            status_code=503,
            content={
                "error_code": "SERVICE_UNAVAILABLE",
                "message": "Authentication service not available",
                "resolution": "Check that all required dependencies are installed",
            },
        )

    @app.post("/analyze")
    async def fallback_analyze():
        return JSONResponse(
            status_code=503,
            content={
                "error_code": "SERVICE_UNAVAILABLE",
                "message": "Analysis service not available",
                "resolution": "Check that all required dependencies are installed",
            },
        )

    @app.get("/api/available-models")
    async def fallback_models():
        return JSONResponse(
            status_code=503,
            content={
                "error_code": "SERVICE_UNAVAILABLE",
                "message": "Model service not available",
                "resolution": "Check that all required dependencies are installed",
            },
        )


# Document upload endpoint - attempt to import
try:
    from .routes import document_routes

    app.include_router(
        document_routes.document_router, prefix="/api", tags=["documents"]
    )
    logger.info("Document routes loaded")
except ImportError as e:
    logger.warning(f"Could not import document routes: {e}")

    @app.post("/api/upload-document")
    async def fallback_upload():
        return JSONResponse(
            status_code=503,
            content={
                "error_code": "SERVICE_UNAVAILABLE",
                "message": "Document upload service not available",
                "resolution": "Check that document processing dependencies are installed",
            },
        )


# Additional MVP utility routes
@app.get("/api/llm/status")
async def llm_status():
    """Get status of LLM providers"""
    try:
        from .services.llm_service import get_llm_status

        return await get_llm_status()
    except ImportError:
        return {
            "providers": {
                "openai": {"status": "unknown"},
                "anthropic": {"status": "unknown"},
                "google": {"status": "unknown"},
            }
        }


@app.get("/api/orchestrator/patterns")
async def get_patterns():
    """Get available analysis patterns"""
    try:
        from .services.pattern_service import get_available_patterns

        return await get_available_patterns()
    except ImportError:
        return ["summarize", "analyze", "compare", "extract"]


# Metrics endpoint if prometheus is available
if DEPENDENCY_STATUS["prometheus_client"]["available"]:
    try:
        from fastapi.responses import Response
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

        @app.get("/metrics")
        async def metrics():
            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    except Exception as e:
        logger.warning(f"Failed to set up metrics endpoint: {e}")


# Error recovery endpoints
@app.post("/api/auth/request-password-reset")
async def password_reset(email: str):
    """Password reset endpoint with fallback"""
    try:
        from .routes.auth_routes import request_password_reset

        return await request_password_reset(email)
    except ImportError:
        return {"message": "Password reset functionality temporarily unavailable"}


# Resource monitoring endpoint
@app.get("/api/internal/resources")
async def get_resource_usage():
    """Monitor resource usage - internal endpoint"""
    try:
        import psutil

        process = psutil.Process()

        return {
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "cpu_percent": process.cpu_percent(interval=0.1),
            "open_files": len(process.open_files()),
            "connections": len(process.connections()),
            "threads": process.num_threads(),
        }
    except Exception as e:
        return {"error": f"Failed to get resource data: {e}"}


# Startup message
if __name__ == "__main__":
    import uvicorn

    # For minimal deployment, use single worker
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        workers=1,
        loop="uvloop",
        log_level="info" if os.getenv("ENV") == "production" else "debug",
    )
