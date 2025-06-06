"""
Production app entry point for deployment.
"""

from typing import Dict, Any

from fastapi import FastAPI
from app.app import create_app
from app.services.model_registry import ModelRegistry
from app.services.prompt_service import get_prompt_service
from app.services.orchestration_service import OrchestrationService
from app.services.quality_evaluation import QualityEvaluationService
from app.services.rate_limiter import RateLimiter
from app.utils.logging import get_logger

logger = get_logger("main")


def initialize_services() -> Dict[str, Any]:
    """Initialize core services and return them in a dictionary."""
    # Initialize model registry
    model_registry = ModelRegistry()

    # Initialize quality evaluation service
    quality_evaluator = QualityEvaluationService()

    # Initialize rate limiter
    rate_limiter = RateLimiter()

    # Initialize orchestration service with required dependencies
    orchestration_service = OrchestrationService(
        model_registry=model_registry,
        quality_evaluator=quality_evaluator,
        rate_limiter=rate_limiter,
    )

    # Initialize prompt service with dependency injection
    prompt_service = get_prompt_service(
        model_registry=model_registry, orchestration_service=orchestration_service
    )

    return {
        "model_registry": model_registry,
        "prompt_service": prompt_service,
        "orchestration_service": orchestration_service,
    }


def configure_app(app: FastAPI, services: Dict[str, Any]) -> None:
    """Configure FastAPI app with initialized services."""
    # Store services in app state
    app.state.model_registry = services["model_registry"]
    app.state.prompt_service = services["prompt_service"]
    app.state.orchestration_service = services["orchestration_service"]

    # Log startup message
    logger.info("✅ App loaded correctly")
    logger.info("Available orchestrator endpoints:")
    logger.info("  - POST /api/orchestrator/analyze")
    logger.info("  - POST /api/orchestrator/compare")
    logger.info("  - POST /api/orchestrator/evaluate")


def create_production_app() -> FastAPI:
    """Create and configure the production FastAPI application."""
    # Create base app
    app = create_app()

    # Initialize services
    services = initialize_services()

    # Configure app with services
    configure_app(app, services)

    return app


# Create the production app
app = create_production_app()
