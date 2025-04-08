import argparse
import os
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from backend.config import Config

# Import utility functions
from backend.utils.server import is_port_available, find_available_port
from backend.utils.logging import get_logger
from backend.utils.error_handler import error_handling_middleware, register_exception_handlers
from backend.utils.middleware import setup_middleware
from backend.utils.rate_limit_middleware import setup_rate_limit_middleware

# Import database
from backend.database import init_db, check_database_connection

# Import routes
from backend.routes.health import health_router
from backend.routes.metrics import metrics_router
from backend.routes.document_routes import document_router
from backend.routes.analyze_routes import analyze_router
from backend.routes.pricing_routes import pricing_router
from backend.routes.user_routes import user_router
from backend.routes.oauth_routes import oauth_router

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
    # Startup: Create necessary directories
    Config.create_directories()

    # Initialize database
    try:
        init_db()
        if check_database_connection():
            logger.info("Database connection established successfully")
        else:
            logger.warning("Database connection failed - some features may not work correctly")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        logger.warning("Continuing without database connection - some features may not work correctly")

    # Initialize Sentry if available
    if SENTRY_AVAILABLE:
        sentry_sdk.init(
            dsn="https://860c945f86e625b606babebefb04c009@o4509109008531456.ingest.us.sentry.io/4509109123350528",
            send_default_pii=True,
            traces_sample_rate=1.0,
            environment=os.getenv("ENVIRONMENT", "development"),
        )
        logger.info("Sentry initialized for error tracking")

    # Load mock service if configured
    global mock_service
    if Config.use_mock:
        try:
            from backend.services.mock_llm_service import MockLLMService
            mock_service = MockLLMService()
            logger.info("🧪 Running in MOCK MODE - all responses will be simulated")
        except ImportError:
            logger.error("⚠️ Mock service module not found. Please create mock_llm_service.py first.")
            sys.exit(1)

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

# Add error handling middleware
app.middleware("http")(error_handling_middleware)

# Set up additional middleware (request validation, logging, performance)
setup_middleware(app)

# Set up rate limiting
setup_rate_limit_middleware(app)

# Include routers
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(document_router)
app.include_router(analyze_router)
app.include_router(pricing_router)
app.include_router(user_router)
app.include_router(oauth_router)

# Register exception handlers
register_exception_handlers(app)


def run_server():
    """Run the server with command line arguments"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run the UltraAI backend server")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server to")
    parser.add_argument(
        "--port", type=int, default=8085, help="Port to bind the server to"
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

    # Set config from arguments
    Config.use_mock = args.mock

    port = args.port

    # If find-port is specified and the port is not available, find an available port
    if args.find_port and not is_port_available(port):
        original_port = port
        port = find_available_port(original_port)
        logger.info(f"Port {original_port} is in use, using port {port} instead")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            f"http://localhost:{port}",
            *[f"http://localhost:{i}" for i in range(3000, 3020)],
            "https://ultrai.app",
            "https://api.ultrai.app",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Start the server
    env = os.getenv("ENVIRONMENT", "development")
    log_level = "debug" if env == "development" else "info"

    logger.info(f"Starting UltraAI backend server in {env} environment")
    logger.info(f"Server running at http://{args.host}:{port}")
    logger.info(f"API documentation available at http://{args.host}:{port}/api/docs")

    uvicorn.run(
        "app:app",
        host=args.host,
        port=port,
        reload=args.reload,
        log_level=log_level,
    )


if __name__ == "__main__":
    run_server()