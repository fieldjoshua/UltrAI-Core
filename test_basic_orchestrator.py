#!/usr/bin/env python3
"""
Simplest possible test of the BaseOrchestrator functionality.
This is the most basic iteration that tests if the core orchestrator works.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import the BaseOrchestrator and configurations
from src.orchestration.config import OrchestratorConfig, ModelConfig, RequestConfig, LLMProvider
from src.orchestration.base_orchestrator import BaseOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_basic_orchestrator():
    """Test the most basic orchestrator functionality with a single model."""
    
    logger.info("Setting up basic orchestrator test...")
    
    # Use mock mode for the simplest test
    logger.info("Using mock adapter for testing")
    os.environ["USE_MOCK"] = "true"
    
    # Create a simple configuration with just one mock model
    model_config = ModelConfig(
        provider=LLMProvider.MOCK,
        model_id="mock-model",
        api_key=None,  # Mock adapter doesn't need an API key
        is_primary=True,
        temperature=0.7,
        max_tokens=500
    )
    
    # Create the orchestrator configuration
    config = OrchestratorConfig(
        models=[model_config],
        cache_enabled=False,  # Disable cache for testing
        parallel_execution=True,
        log_level="INFO"
    )
    
    # Initialize the orchestrator
    logger.info("Initializing BaseOrchestrator...")
    orchestrator = BaseOrchestrator(config)
    
    # Create a simple request
    request = RequestConfig(
        prompt="Explain in 3 sentences what an LLM orchestrator does."
    )
    
    # Execute the request
    logger.info("Executing request...")
    response = await orchestrator.execute_request(request)
    
    # Log the results
    logger.info(f"Response received:")
    logger.info(f"Content: {response.content}")
    logger.info(f"Execution time: {response.metadata.get('execution_time', 'N/A')} seconds")
    logger.info(f"Models used: {response.metadata.get('models_used', [])}")
    logger.info(f"Successful models: {response.metadata.get('successful_models', [])}")
    
    return response

def main():
    """Main function to run the test."""
    logger.info("Starting basic orchestrator test...")
    
    try:
        # Run the async test
        response = asyncio.run(test_basic_orchestrator())
        logger.info("Test completed successfully!")
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()