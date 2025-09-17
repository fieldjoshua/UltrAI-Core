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

    # Log startup message
    logger.info("✅ App loaded correctly")
    logger.info("Available orchestrator endpoints:")
    logger.info("  - POST /api/orchestrator/analyze")
    logger.info("  - POST /api/orchestrator/compare")
    logger.info("  - POST /api/orchestrator/evaluate")
    
    # Log Big 3 provider readiness
    import asyncio
    from app.config import Config
    
    async def check_big3_readiness():
        try:
            orchestration_service = services["orchestration_service"]
            available_models = await orchestration_service._default_models_from_env()
            
            # Check which Big 3 providers are present
            providers_found = {
                "openai": False,
                "anthropic": False, 
                "google": False
            }
            
            for model in available_models:
                if model.startswith("gpt") or model.startswith("o1"):
                    providers_found["openai"] = True
                elif model.startswith("claude"):
                    providers_found["anthropic"] = True
                elif model.startswith("gemini"):
                    providers_found["google"] = True
            
            # Log provider status
            logger.info("🚀 Big 3 Provider Status:")
            logger.info(f"  - OpenAI: {'✅ READY' if providers_found['openai'] else '❌ NOT AVAILABLE'}")
            logger.info(f"  - Anthropic: {'✅ READY' if providers_found['anthropic'] else '❌ NOT AVAILABLE'}")
            logger.info(f"  - Google: {'✅ READY' if providers_found['google'] else '❌ NOT AVAILABLE'}")
            
            # Check if minimum requirements are met
            total_models = len(available_models)
            required_models = Config.MINIMUM_MODELS_REQUIRED
            required_providers = set(getattr(Config, "REQUIRED_PROVIDERS", []))
            
            providers_present = [p for p, found in providers_found.items() if found]
            all_required_present = not required_providers or required_providers.issubset(set(providers_present))
            
            if total_models >= required_models and all_required_present:
                logger.info(f"✅ Service READY: {total_models} models available (minimum: {required_models})")
            else:
                logger.warning(f"⚠️ Service NOT READY: {total_models} models available (minimum: {required_models})")
                if required_providers and not all_required_present:
                    missing = list(required_providers - set(providers_present))
                    logger.warning(f"⚠️ Missing required providers: {missing}")
                    
        except Exception as e:
            logger.error(f"Failed to check Big 3 readiness: {e}")
    
    # Run the readiness check
    asyncio.create_task(check_big3_readiness())


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
