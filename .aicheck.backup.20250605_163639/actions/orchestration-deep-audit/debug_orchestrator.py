"""
Debug version of the Pattern Orchestrator with extensive logging
This file adds detailed logging at every critical point to trace the execution flow
"""

import os
import sys
import logging
import json

# Setup logging with more detail
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)

# Add src to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
src_dir = os.path.join(root_dir, "src")
sys.path.insert(0, src_dir)

from src.core.ultra_pattern_orchestrator import PatternOrchestrator as OriginalPatternOrchestrator

class DebugPatternOrchestrator(OriginalPatternOrchestrator):
    """Pattern Orchestrator with extensive debug logging"""
    
    def __init__(self, api_keys, pattern="gut", output_format="plain"):
        self.logger = logging.getLogger("DEBUG_ORCHESTRATOR")
        self.logger.info("=" * 80)
        self.logger.info("INITIALIZING DEBUG PATTERN ORCHESTRATOR")
        self.logger.info(f"API Keys provided: {list(api_keys.keys())}")
        self.logger.info(f"Pattern: {pattern}")
        self.logger.info(f"Output format: {output_format}")
        self.logger.info("=" * 80)
        
        super().__init__(api_keys, pattern, output_format)
        
        self.logger.info("INITIALIZATION COMPLETE")
        self.logger.info(f"Available models after init: {self.available_models}")
        self.logger.info("=" * 80)
    
    def _initialize_clients(self):
        """Override to add detailed logging"""
        self.logger.info(">>> ENTERING _initialize_clients")
        self.logger.info(f"API Keys status:")
        self.logger.info(f"  - Anthropic: {'Present' if self.anthropic_key else 'Missing'}")
        self.logger.info(f"  - OpenAI: {'Present' if self.openai_key else 'Missing'}")
        self.logger.info(f"  - Google: {'Present' if self.google_key else 'Missing'}")
        self.logger.info(f"  - Mistral: {'Present' if self.mistral_key else 'Missing'}")
        self.logger.info(f"  - Cohere: {'Present' if self.cohere_key else 'Missing'}")
        self.logger.info(f"  - Perplexity: {'Present' if self.perplexity_key else 'Missing'}")
        self.logger.info(f"  - DeepSeek: {'Present' if self.deepseek_key else 'Missing'}")
        
        # Call parent implementation
        super()._initialize_clients()
        
        self.logger.info(f"<<< EXITING _initialize_clients")
        self.logger.info(f"Available models: {self.available_models}")
        self.logger.info(f"Clients initialized: {list(self.clients.keys())}")
    
    async def orchestrate_full_process(self, prompt):
        """Override to add detailed logging"""
        self.logger.info(">>> ENTERING orchestrate_full_process")
        self.logger.info(f"Prompt: {prompt[:100]}...")
        self.logger.info(f"Available models at start: {self.available_models}")
        
        result = await super().orchestrate_full_process(prompt)
        
        self.logger.info("<<< EXITING orchestrate_full_process")
        self.logger.info(f"Result keys: {list(result.keys())}")
        return result
    
    async def get_initial_responses(self, prompt):
        """Override to add detailed logging"""
        self.logger.info(">>> ENTERING get_initial_responses")
        self.logger.info(f"Available models: {self.available_models}")
        
        # Log the model selection process
        models_to_use = []
        self.logger.info("Model selection process:")
        
        if "anthropic" in self.available_models:
            self.logger.info("  - Found 'anthropic' in available_models, adding 'claude' to models_to_use")
            models_to_use.append("claude")
        else:
            self.logger.info("  - 'anthropic' NOT in available_models")
            
        if "openai" in self.available_models:
            self.logger.info("  - Found 'openai' in available_models, adding 'chatgpt' to models_to_use")
            models_to_use.append("chatgpt")
        else:
            self.logger.info("  - 'openai' NOT in available_models")
            
        if "google" in self.available_models:
            self.logger.info("  - Found 'google' in available_models, adding 'gemini' to models_to_use")
            models_to_use.append("gemini")
        else:
            self.logger.info("  - 'google' NOT in available_models")
        
        self.logger.info(f"Models to use: {models_to_use}")
        
        # Call parent implementation
        responses = await super().get_initial_responses(prompt)
        
        self.logger.info("<<< EXITING get_initial_responses")
        self.logger.info(f"Responses received from: {list(responses.keys())}")
        for model, response in responses.items():
            self.logger.info(f"  - {model}: {len(response)} chars")
        
        return responses
    
    async def get_claude_response(self, prompt):
        """Override to add detailed logging"""
        self.logger.info(">>> ENTERING get_claude_response")
        self.logger.info(f"Available models: {self.available_models}")
        self.logger.info(f"Checking if 'claude' in available_models: {'claude' in self.available_models}")
        
        response = await super().get_claude_response(prompt)
        
        self.logger.info("<<< EXITING get_claude_response")
        self.logger.info(f"Response length: {len(response)} chars")
        self.logger.info(f"Response preview: {response[:100]}..." if response else "EMPTY RESPONSE")
        
        return response
    
    async def get_chatgpt_response(self, prompt):
        """Override to add detailed logging"""
        self.logger.info(">>> ENTERING get_chatgpt_response")
        self.logger.info(f"Available models: {self.available_models}")
        self.logger.info(f"Checking if 'chatgpt' in available_models: {'chatgpt' in self.available_models}")
        
        response = await super().get_chatgpt_response(prompt)
        
        self.logger.info("<<< EXITING get_chatgpt_response")
        self.logger.info(f"Response length: {len(response)} chars")
        self.logger.info(f"Response preview: {response[:100]}..." if response else "EMPTY RESPONSE")
        
        return response


async def test_debug_orchestrator():
    """Test the debug orchestrator with a simple prompt"""
    import asyncio
    
    # Get API keys from environment
    api_keys = {
        "anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "openai": os.getenv("OPENAI_API_KEY"),
        "google": os.getenv("GOOGLE_API_KEY"),
    }
    
    # Remove None values
    api_keys = {k: v for k, v in api_keys.items() if v}
    
    print(f"Testing with API keys: {list(api_keys.keys())}")
    
    # Create debug orchestrator
    orchestrator = DebugPatternOrchestrator(api_keys, pattern="gut")
    
    # Test with a simple prompt
    test_prompt = "What is 2+2?"
    
    print(f"\nTesting with prompt: {test_prompt}")
    print("=" * 80)
    
    try:
        result = await orchestrator.orchestrate_full_process(test_prompt)
        print("\nSUCCESS! Result received:")
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"\nERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_debug_orchestrator())