"""
Debug script to test orchestrator model selection.
"""

import os
import asyncio
from app.services.orchestration_service import OrchestrationService
from app.services.model_registry import ModelRegistry
from app.services.quality_evaluation import QualityEvaluationService
from app.services.rate_limiter import RateLimiter

async def debug_orchestrator():
    print("=== Orchestrator Debug ===")
    
    # Check environment variables
    print("\n1. Environment Variables:")
    api_keys = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
        "HUGGINGFACE_API_KEY": os.getenv("HUGGINGFACE_API_KEY"),
    }
    
    for key, value in api_keys.items():
        if value:
            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            print(f"  {key}: {masked}")
        else:
            print(f"  {key}: NOT SET")
    
    # Initialize orchestration service
    print("\n2. Initializing Orchestration Service...")
    model_registry = ModelRegistry()
    quality_evaluator = QualityEvaluationService()
    rate_limiter = RateLimiter()
    
    orchestration_service = OrchestrationService(
        model_registry=model_registry,
        quality_evaluator=quality_evaluator,
        rate_limiter=rate_limiter,
    )
    
    # Check default models
    print("\n3. Checking Default Models...")
    default_models = await orchestration_service._default_models_from_env()
    print(f"  Default models from environment: {default_models}")
    
    # Test creating adapters
    print("\n4. Testing Adapter Creation...")
    test_models = ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
    
    for model in test_models:
        adapter, mapped_model = orchestration_service._create_adapter(model)
        if adapter:
            print(f"  ✓ {model} -> adapter created (mapped to {mapped_model})")
        else:
            print(f"  ✗ {model} -> failed to create adapter")
    
    # Test pipeline with a simple query
    print("\n5. Testing Pipeline...")
    test_query = "Hello, this is a test"
    
    try:
        # Try with no models specified (should use defaults)
        print("  Testing with default model selection...")
        results = await orchestration_service.run_pipeline(
            input_data=test_query,
            options={"enable_cache": False}
        )
        
        print(f"  Pipeline stages completed: {list(results.keys())}")
        
        # Check initial_response stage
        if "initial_response" in results:
            initial = results["initial_response"]
            if hasattr(initial, "output") and isinstance(initial.output, dict):
                responses = initial.output.get("responses", {})
                print(f"  Models that responded: {list(responses.keys())}")
                for model, response in responses.items():
                    if isinstance(response, dict) and "error" in response:
                        print(f"    - {model}: ERROR - {response['error']}")
                    else:
                        print(f"    - {model}: SUCCESS")
            else:
                print("  Initial response has unexpected format")
                
    except Exception as e:
        print(f"  Pipeline failed: {str(e)}")
    
    print("\n=== Debug Complete ===")

if __name__ == "__main__":
    asyncio.run(debug_orchestrator())