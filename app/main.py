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
from app.services.model_selection import SmartModelSelector
from app.services.provider_health_manager import provider_health_manager

# from app.services.provider_health_manager import provider_health_manager
from app.utils.logging import get_logger
from app.config import Config
import os
import sys
import asyncio

logger = get_logger("main")

FAST_STARTUP = os.getenv("FAST_STARTUP", "false").lower() == "true"


async def log_startup_readiness():
    """Logs a summary of service readiness at startup."""
    logger.info("--- Startup Readiness Check ---")
    try:
        # Use asyncio.wait_for to prevent infinite blocking
        health_summary = await asyncio.wait_for(
            provider_health_manager.get_health_summary(),
            timeout=5.0
        )
        available_providers = health_summary.get("_system", {}).get("available_providers", [])
        required_providers = Config.REQUIRED_PROVIDERS
        missing_providers = [p for p in required_providers if p not in available_providers]

        big_3_status = {p: ("✅" if p in available_providers else "❌") for p in ["openai", "anthropic", "google"]}
        logger.info(
            "Provider Health (Big 3): OpenAI: %s, Anthropic: %s, Google: %s",
            big_3_status["openai"],
            big_3_status["anthropic"],
            big_3_status["google"],
        )

        if missing_providers:
            logger.warning(f"Missing required providers: {', '.join(missing_providers)}")
        else:
            logger.info("All required providers are present.")

        # Skip detailed model discovery at startup to prevent blocking
        logger.info("Skipping detailed model discovery at startup (will run in background)")

    except asyncio.TimeoutError:
        logger.warning("Startup readiness check timed out after 5s - continuing anyway")
    except Exception as e:
        logger.error(f"Failed to perform startup readiness check: {e}", exc_info=True)
    logger.info("---------------------------------")


def validate_production_requirements() -> bool:
    """
    Validate that production requirements are met.

    Returns:
        bool: True if requirements are met, False otherwise
    """
    if Config.ENVIRONMENT != "production":
        return True  # Skip validation for non-production environments

    # Check minimum models requirement
    if Config.MINIMUM_MODELS_REQUIRED < 2:
        logger.error(
            "⚠️ PRODUCTION CONFIG ERROR: MINIMUM_MODELS_REQUIRED must be at least 2 in production. "
            f"Current value: {Config.MINIMUM_MODELS_REQUIRED}"
        )
        return False

    # Check for required API keys (at least 2 providers must be configured)
    configured_providers = []

    if os.getenv("OPENAI_API_KEY"):
        configured_providers.append("OpenAI")
    if os.getenv("ANTHROPIC_API_KEY"):
        configured_providers.append("Anthropic")
    if os.getenv("GOOGLE_API_KEY"):
        configured_providers.append("Google")
    if os.getenv("HUGGINGFACE_API_KEY"):
        configured_providers.append("HuggingFace")

    if len(configured_providers) < 2:
        logger.error(
            "⚠️ PRODUCTION CONFIG ERROR: At least 2 LLM provider API keys must be configured. "
            f"Currently configured: {configured_providers}"
        )
        logger.error(
            "Please set at least 2 of the following environment variables: "
            "OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, HUGGINGFACE_API_KEY"
        )
        return False

    # Check single model fallback is disabled
    if Config.ENABLE_SINGLE_MODEL_FALLBACK:
        logger.warning(
            "⚠️ PRODUCTION WARNING: ENABLE_SINGLE_MODEL_FALLBACK is enabled. "
            "This should be disabled in production for proper multi-model orchestration."
        )

    logger.info(
        f"✅ Production validation passed: {len(configured_providers)} providers configured "
        f"({', '.join(configured_providers)}), minimum models: {Config.MINIMUM_MODELS_REQUIRED}"
    )

    return True


def initialize_services() -> Dict[str, Any]:
    """Initialize core services and return them in a dictionary."""
    # Initialize model registry
    model_registry = ModelRegistry()

    # Initialize quality evaluation service
    quality_evaluator = QualityEvaluationService()

    # Initialize rate limiter
    rate_limiter = RateLimiter()

    # Initialize model selector (shared across services)
    model_selector = SmartModelSelector()

    # Initialize cache service (singleton, will be reused)
    from app.services.cache_service import get_cache_service

    cache_service = get_cache_service()

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
        "model_selector": model_selector,
        "cache_service": cache_service,
    }


def configure_app(app: FastAPI, services: Dict[str, Any]) -> None:
    """Configure FastAPI app with initialized services."""
    # Store services in app state
    app.state.model_registry = services["model_registry"]
    app.state.prompt_service = services["prompt_service"]
    app.state.orchestration_service = services["orchestration_service"]
    app.state.services = services  # Store all services for route access

    @app.on_event("startup")
    async def startup_event():
        """On startup, run readiness check."""
        if not FAST_STARTUP:
            await log_startup_readiness()

    # Log startup message
    logger.info("✅ App loaded correctly")
    logger.info("Available orchestrator endpoints:")
    logger.info("  - POST /api/orchestrator/analyze")
    logger.info("  - POST /api/orchestrator/compare")
    logger.info("  - POST /api/orchestrator/evaluate")

    # Log Big 3 provider readiness
    from app.config import Config

    async def check_big3_readiness():
        try:
            orchestration_service = services["orchestration_service"]
            available_models = await orchestration_service._default_models_from_env()

            # Check which Big 3 providers are present
            providers_found = {"openai": False, "anthropic": False, "google": False}

            for model in available_models:
                if model.startswith("gpt") or model.startswith("o1"):
                    providers_found["openai"] = True
                elif model.startswith("claude"):
                    providers_found["anthropic"] = True
                elif model.startswith("gemini"):
                    providers_found["google"] = True

            # Log provider status
            logger.info("🚀 Big 3 Provider Status:")
            logger.info(
                f"  - OpenAI: {'✅ READY' if providers_found['openai'] else '❌ NOT AVAILABLE'}"
            )
            logger.info(
                f"  - Anthropic: {'✅ READY' if providers_found['anthropic'] else '❌ NOT AVAILABLE'}"
            )
            logger.info(
                f"  - Google: {'✅ READY' if providers_found['google'] else '❌ NOT AVAILABLE'}"
            )

            # Check if minimum requirements are met
            total_models = len(available_models)
            required_models = Config.MINIMUM_MODELS_REQUIRED
            required_providers = set(getattr(Config, "REQUIRED_PROVIDERS", []))

            providers_present = [p for p, found in providers_found.items() if found]
            all_required_present = (
                not required_providers
                or required_providers.issubset(set(providers_present))
            )

            if total_models >= required_models and all_required_present:
                logger.info(
                    f"✅ Service READY: {total_models} models available (minimum: {required_models})"
                )
            else:
                logger.warning(
                    f"⚠️ Service NOT READY: {total_models} models available (minimum: {required_models})"
                )
                if required_providers and not all_required_present:
                    missing = list(required_providers - set(providers_present))
                    logger.warning(f"⚠️ Missing required providers: {missing}")

        except Exception as e:
            logger.error(f"Failed to check Big 3 readiness: {e}")

    # Optionally skip heavy readiness checks for faster startup
    if not FAST_STARTUP:
        app.add_event_handler("startup", check_big3_readiness)


def create_production_app() -> FastAPI:
    """Create and configure the production FastAPI application."""
    # Validate production requirements
    if not validate_production_requirements():
        logger.error("🚨 PRODUCTION REQUIREMENTS NOT MET - SERVICE CANNOT START")
        if Config.ENVIRONMENT == "production":
            # In production, fail fast to prevent deploying a broken service
            sys.exit(1)

    # Create base app
    app = create_app()

    # Initialize services
    services = initialize_services()

    # Configure app with services
    configure_app(app, services)

    return app


# Create the production app
app = create_production_app()
