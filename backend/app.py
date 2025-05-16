import argparse
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from backend.config import Config

# Import database
from backend.database import check_database_connection, init_db
from backend.middleware.api_key_middleware import setup_api_key_middleware

# Import security middleware
from backend.middleware.auth_middleware import setup_auth_middleware
from backend.middleware.csrf_middleware import setup_csrf_middleware
from backend.middleware.locale_middleware import setup_locale_middleware
from backend.middleware.security_headers_middleware import (
    setup_security_headers_middleware,
)
from backend.middleware.validation_middleware import setup_validation_middleware
from backend.routes.analyze_routes import analyze_router
from backend.routes.auth_routes import auth_router
from backend.routes.available_models_routes import router as available_models_router
from backend.routes.docker_modelrunner_routes import router as modelrunner_router
from backend.routes.document_analysis_routes import document_analysis_router
from backend.routes.document_routes import document_router

# Import routes
from backend.routes.health_routes import router as health_router
from backend.routes.llm_routes import llm_router
from backend.routes.metrics import metrics_router
from backend.routes.oauth_routes import oauth_router
from backend.routes.orchestrator_routes import orchestrator_router
from backend.routes.pricing_routes import pricing_router
from backend.routes.user_routes import user_router
from backend.utils.cookie_security_middleware import setup_cookie_security_middleware
from backend.utils.error_handler import (
    error_handling_middleware,
    register_exception_handlers,
)
from backend.utils.logging import get_logger
from backend.utils.metrics import setup_metrics
from backend.utils.middleware import setup_middleware
from backend.utils.monitoring import (
    log_startup_event,
    monitoring_system,
    setup_monitoring,
)

# Import rate limiting
from backend.utils.rate_limit_middleware import rate_limit_middleware

# Import utility functions
from backend.utils.server import find_available_port, is_port_available
from backend.utils.structured_logging import apply_structured_logging_middleware

# Get logger
logger = get_logger("ultra_api", "logs/api.log")

# Check if Sentry is available
try:
    import sentry_sdk

    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False


# Create a global mock service variable
mock_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application
    Handles startup and shutdown events
    """
    # Initialize monitoring system
    setup_monitoring(app)

    # Initialize metrics collection
    setup_metrics(app)

    # Startup: Create necessary directories
    Config.create_directories()

    # Validate configuration
    try:
        Config.validate_configuration()
        logger.info(f"Configuration validated for {Config.ENVIRONMENT} environment")
    except Exception as e:
        logger.error(f"Configuration validation error: {str(e)}")
        if Config.ENVIRONMENT == "production":
            logger.critical("Invalid configuration in production environment, exiting")
            sys.exit(1)
        else:
            logger.warning(
                "Continuing with invalid configuration in non-production environment"
            )

    # Initialize database
    try:
        init_db()
        if check_database_connection():
            logger.info("Database connection established successfully")
        else:
            logger.warning(
                "Database connection failed - some features may not work correctly"
            )
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        logger.warning(
            "Continuing without database connection - some features may not work correctly"
        )

    # Initialize Sentry if available and DSN is configured
    if SENTRY_AVAILABLE:
        # Get DSN from environment variable, with empty default
        sentry_dsn = os.environ.get("SENTRY_DSN", "")
        if sentry_dsn:
            sentry_sdk.init(
                dsn=sentry_dsn,
                send_default_pii=True,
                traces_sample_rate=1.0,
                environment=Config.ENVIRONMENT,
            )
            logger.info("Sentry initialized for error tracking")
        else:
            logger.info("No Sentry DSN configured, error tracking disabled")

    # Load mock service if configured
    global mock_service
    if Config.USE_MOCK or Config.MOCK_MODE:
        try:
            from backend.services.mock_llm_service import MockLLMService

            mock_service = MockLLMService()
            logger.info("🧪 Running in MOCK MODE - all responses will be simulated")
        except ImportError:
            logger.error(
                "⚠️ Mock service module not found. Please create mock_llm_service.py first."
            )
            sys.exit(1)
    else:
        # Log that we're running with real services
        logger.info(
            "🚀 Running with REAL SERVICES - API keys will be used for LLM providers"
        )
        # Check if we have at least one API key configured
        if not any(
            [Config.OPENAI_API_KEY, Config.ANTHROPIC_API_KEY, Config.GOOGLE_API_KEY]
        ):
            logger.warning(
                "⚠️ No API keys configured for LLM providers - some features may not work correctly"
            )

    # Log application startup
    log_startup_event(
        app_name="UltraAI Backend",
        version=app.version,
        config={
            "environment": Config.ENVIRONMENT,
            "debug": Config.DEBUG,
            "mock_mode": Config.MOCK_MODE,
            "enable_cache": Config.ENABLE_CACHE,
            "enable_auth": Config.ENABLE_AUTH,
            "enable_rate_limit": Config.ENABLE_RATE_LIMIT,
            "default_provider": Config.DEFAULT_PROVIDER,
            "default_model": Config.DEFAULT_MODEL,
        },
    )

    yield

    # Shutdown: Cleanup resources if needed
    logger.info("Shutting down application")


# Create FastAPI application with lifespan manager
app = FastAPI(
    title="Ultra API",
    description="UltraAI Backend API",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        *[f"http://localhost:{i}" for i in range(3000, 3020)],
        "https://ultrai.app",
        "https://api.ultrai.app",
        "http://frontend:3009",  # Docker container hostname
        "*",  # Allow all origins for testing
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Add error handling middleware
app.middleware("http")(error_handling_middleware)

# Set up security middleware
setup_security_headers_middleware(app)
setup_csrf_middleware(app)
setup_validation_middleware(app)
setup_auth_middleware(app)
setup_api_key_middleware(app)
setup_middleware(app)
setup_locale_middleware(app)

# Apply the structured logging middleware that was previously configured
apply_structured_logging_middleware(app)

# Set up rate limiting
app.middleware("http")(rate_limit_middleware)


# --- END ADDED ROUTE --- #

# Include routers
app.include_router(health_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(document_router, prefix="/api")
app.include_router(
    document_analysis_router
)  # Already has /api prefix in its route definitions
app.include_router(analyze_router)  # Already has /api prefix in its route definitions
app.include_router(pricing_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(oauth_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(llm_router, prefix="/api")
app.include_router(available_models_router, prefix="/api")  # New available models route
app.include_router(
    modelrunner_router
)  # Already has /api prefix in its route definitions
app.include_router(orchestrator_router, prefix="/api")  # New orchestrator routes


def run_server():
    """Run the server with command line arguments"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the UltraAI backend server")
    parser.add_argument(
        "--host", default=Config.API_HOST, help="Host to bind the server to"
    )
    parser.add_argument(
        "--port", type=int, default=Config.API_PORT, help="Port to bind the server to"
    )
    parser.add_argument(
        "--reload", action="store_true", help="Enable auto-reload on code changes"
    )
    parser.add_argument(
        "--find-port",
        action="store_true",
        help="Find an available port if specified port is in use",
    )
    parser.add_argument(
        "--mock", action="store_true", help="Run in mock mode with simulated responses"
    )
    args = parser.parse_args()

    # Set config from arguments if provided
    if args.mock:
        Config.USE_MOCK = True
        Config.MOCK_MODE = True

    port = args.port

    # If find-port is specified and the port is not available, find an available port
    if args.find_port and not is_port_available(port):
        original_port = port
        port = find_available_port(original_port)
        logger.info(f"Port {original_port} is in use, using port {port} instead")

    # Determine log level based on environment
    log_level = "debug" if Config.DEBUG else Config.LOG_LEVEL.lower()
    if log_level not in ["critical", "error", "warning", "info", "debug", "trace"]:
        log_level = "info"  # Default if invalid

    # Start the server
    logger.info(f"Starting UltraAI backend server in {Config.ENVIRONMENT} environment")
    logger.info(f"Server running at http://{args.host}:{port}")
    logger.info(f"API documentation available at http://{args.host}:{port}/api/docs")

    # Additional mode information
    if Config.USE_MOCK or Config.MOCK_MODE:
        logger.info("Running in MOCK MODE - real API keys will not be used")

    uvicorn.run(
        "app:app",
        host=args.host,
        port=port,
        reload=args.reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    run_server()
