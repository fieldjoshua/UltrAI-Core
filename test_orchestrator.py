#!/usr/bin/env python3
"""
Test script for the basic orchestrator functionality.
"""

import asyncio
import os
import sys
import logging

# Add the project root to PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.orchestration.config import OrchestratorConfig, ModelConfig, RequestConfig, LLMProvider

# Use the BaseOrchestrator for simple testing
from src.orchestration.base_orchestrator import BaseOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_orchestrator():
    """Test the basic orchestrator functionality."""
    
    logger.info("Creating orchestrator configuration...")
    
    # Create mock model configuration
    mock_model = ModelConfig(
        provider=LLMProvider.MOCK,
        model_id="gpt-4",
        is_primary=True,
        temperature=0.7,
        max_tokens=1000
    )
    
    # Create orchestrator configuration
    config = OrchestratorConfig(
        models=[mock_model],
        cache_enabled=True,
        parallel_execution=True,
        log_level="INFO"
    )
    
    logger.info("Initializing orchestrator...")
    orchestrator = BaseOrchestrator(config)
    
    # Display available models
    available_models = orchestrator.get_available_models()
    logger.info(f"Available models: {available_models}")
    
    # Test with a simple prompt
    prompt = "What are the key considerations for building a reliable distributed system?"
    request = RequestConfig(prompt=prompt)
    
    logger.info(f"Sending prompt: {prompt}")
    response = await orchestrator.execute_request(request)
    
    # Display results
    logger.info("Response received:")
    logger.info(f"Primary content: {response.content}")
    logger.info(f"Execution time: {response.metadata.get('execution_time', 'N/A')} seconds")
    logger.info(f"Models used: {response.metadata.get('models_used', [])}")
    logger.info(f"Successful models: {response.metadata.get('successful_models', [])}")
    
    # Display model responses
    for model_key, model_response in response.model_responses.items():
        if "error" in model_response:
            logger.error(f"{model_key} error: {model_response['error']}")
        else:
            logger.info(f"{model_key} response: {model_response['content'][:100]}...")
    
    return response

def main():
    """Main function to run the test."""
    logger.info("Starting orchestrator test...")
    
    # Run the async test
    response = asyncio.run(test_orchestrator())
    
    logger.info("Test completed successfully!")
    
    # Return the response for further inspection
    return response

if __name__ == "__main__":
    main()