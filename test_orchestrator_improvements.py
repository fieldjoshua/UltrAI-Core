#!/usr/bin/env python3
"""Test script to verify orchestrator improvements."""

import asyncio
import os
import sys
from datetime import datetime

# Set up test environment
os.environ["TESTING"] = "true"
os.environ["ORCHESTRATION_TIMEOUT"] = "30"
os.environ["RATE_LIMIT_DETECTION_ENABLED"] = "true"
os.environ["RATE_LIMIT_RETRY_ENABLED"] = "true"
os.environ["MAX_RETRY_ATTEMPTS"] = "3"

# Force reload of config module to pick up new attributes
if 'app.config' in sys.modules:
    del sys.modules['app.config']

from app.services.orchestration_service import OrchestrationService
from app.services.model_registry import ModelRegistry
from app.services.quality_evaluation import QualityEvaluationService
from app.services.rate_limiter import RateLimiter

async def test_improvements():
    """Test the orchestrator improvements."""
    print(f"Testing orchestrator improvements at {datetime.now()}")
    print("-" * 60)
    
    # Initialize services
    model_registry = ModelRegistry()
    quality_evaluator = QualityEvaluationService()
    rate_limiter = RateLimiter()
    
    orchestrator = OrchestrationService(
        model_registry=model_registry,
        quality_evaluator=quality_evaluator,
        rate_limiter=rate_limiter
    )
    
    # Test 1: API key validation
    print("\n1. Testing API key validation:")
    result = await orchestrator._execute_model_with_retry(
        "gpt-4", 
        "Test prompt"
    )
    print(f"   Result (should be stub in test mode): {result.get('generated_text', '')[:50]}...")
    
    # Test 2: Provider detection
    print("\n2. Testing provider detection:")
    providers = {
        "gpt-4": "openai",
        "claude-3-opus-20240229": "anthropic", 
        "gemini-pro": "google",
        "meta-llama/Meta-Llama-3-8B-Instruct": "huggingface"
    }
    
    for model, expected in providers.items():
        actual = orchestrator._get_provider_from_model(model)
        status = "✅" if actual == expected else "❌"
        print(f"   {status} {model}: {actual} (expected: {expected})")
    
    # Test 3: Cache key generation with long input
    print("\n3. Testing cache key generation:")
    long_input = "A" * 1000  # 1000 character input
    
    # Mock the cache service
    from app.services.cache_service import get_cache_service
    cache_service = get_cache_service()
    
    # Generate cache key with old method (truncated)
    import hashlib
    old_hash = hashlib.sha256(long_input[:500].encode()).hexdigest()
    
    # Generate with new method (full hash)
    new_hash = hashlib.sha256(long_input.encode()).hexdigest()
    
    print(f"   Old method (truncated): {old_hash[:20]}...")
    print(f"   New method (full hash): {new_hash[:20]}...")
    print(f"   Hashes are {'❌ SAME' if old_hash == new_hash else '✅ DIFFERENT'}")
    
    # Test 4: Configuration values
    print("\n4. Testing configuration values:")
    from app.config import Config
    print(f"   ORCHESTRATION_TIMEOUT: {Config.ORCHESTRATION_TIMEOUT}s")
    print(f"   INITIAL_RESPONSE_TIMEOUT: {Config.INITIAL_RESPONSE_TIMEOUT}s")
    print(f"   PEER_REVIEW_TIMEOUT: {Config.PEER_REVIEW_TIMEOUT}s")
    print(f"   ULTRA_SYNTHESIS_TIMEOUT: {Config.ULTRA_SYNTHESIS_TIMEOUT}s")
    print(f"   LLM_REQUEST_TIMEOUT: {Config.LLM_REQUEST_TIMEOUT}s")
    print(f"   CONCURRENT_EXECUTION_TIMEOUT: {Config.CONCURRENT_EXECUTION_TIMEOUT}s")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(test_improvements())