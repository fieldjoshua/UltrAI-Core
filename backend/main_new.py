"""
UltraAI Backend API - Main Entry Point
This file provides backward compatibility with the original main.py
while using the new modular architecture.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import configuration
from backend.config import Config

# Import utility functions
from backend.utils.metrics import update_metrics_history

# Import routes
from backend.routes.health import health_router
from backend.routes.metrics import metrics_router
from backend.routes.document_routes import document_router
from backend.routes.analyze_routes import analyze_router

# Import error handling system
from error_handler import error_handling_middleware, register_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ultra_api")

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
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure more restrictively in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware
app.middleware("http")(error_handling_middleware)

# Include routers
app.include_router(health_router)
app.include_router(metrics_router)
app.include_router(document_router)
app.include_router(analyze_router)

# Register exception handlers
register_exception_handlers(app)


# Periodic metric updates
@app.middleware("http")
async def update_metrics_middleware(request, call_next):
    """Middleware to update metrics after each request"""
    response = await call_next(request)
    update_metrics_history()
    return response