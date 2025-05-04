#!/usr/bin/env python3
"""
Run a specific prompt through the Simple Core Orchestrator.
"""

import asyncio
import json
import logging
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.simple_core.config import Config, ModelDefinition
from src.simple_core.factory import create_orchestrator, create_from_env

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("specific_prompt")

async def run_specific_prompt():
    """Run a specific prompt through the orchestrator."""
    # Initialize orchestrator
    orchestrator = create_from_env()
    if not orchestrator:
        logger.error("No API keys found in environment. Exiting.")
        return
    
    # The specific prompt
    prompt = """
    Provide a list of the top 10 angel investors who focus on peer-to-peer sales platforms 
    targeted at college campuses. Include their name, investment focus, notable investments, 
    and suggested ways to contact them (like LinkedIn profiles or email formats).
    """
    
    # Create request
    request = {
        "prompt": prompt,
        "options": {
            "max_tokens": 2000,
            "temperature": 0.7
        }
    }
    
    # Process request
    logger.info("Processing prompt about angel investors...")
    response = await orchestrator.process(request)
    
    # Print the primary response
    print("\n" + "=" * 80)
    print("ANGEL INVESTORS FOR COLLEGE CAMPUS P2P SALES")
    print("=" * 80)
    print(response["content"])
    print("-" * 80)
    print(f"Response from: {response['metadata']['primary_model']}")
    print("-" * 80)
    
    # Save detailed response to a file
    with open("angel_investors_response.json", "w") as f:
        json.dump(response, f, indent=2)
    
    logger.info(f"Full response saved to angel_investors_response.json")
    
    return response

def main():
    """Main function."""
    try:
        asyncio.run(run_specific_prompt())
    except Exception as e:
        logger.error(f"Error running prompt: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()