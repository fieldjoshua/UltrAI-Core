import os
import asyncio
from typing import Dict, Any, Optional, List
from ultra_base import UltraBase, PromptTemplate, RateLimits
from ultra_llm import UltraLLM
from ultra_data import UltraData
import pandas as pd

class UltraOrchestrator:
    def __init__(
        self,
        api_keys: Dict[str, str],
        prompt_templates: Optional[PromptTemplate] = None,
        rate_limits: Optional[RateLimits] = None,
        output_format: str = "plain",
        enabled_features: Optional[List[str]] = None,
        ultra_engine: str = "chatgpt"
    ):
        # Initialize components
        self.llm = UltraLLM(
            api_keys=api_keys,
            prompt_templates=prompt_templates,
            rate_limits=rate_limits,
            output_format=output_format,
            enabled_features=enabled_features,
            ultra_engine=ultra_engine
        )
        
        self.data = UltraData(
            api_keys=api_keys,
            prompt_templates=prompt_templates,
            rate_limits=rate_limits,
            output_format=output_format,
            enabled_features=enabled_features
        )
        
        # Store configuration
        self.api_keys = api_keys
        self.prompt_templates = prompt_templates or PromptTemplate()
        self.rate_limits = rate_limits or RateLimits()
        self.output_format = output_format
        self.enabled_features = enabled_features or []
        self.ultra_engine = ultra_engine
    
    async def process_with_llm(self, prompt: str) -> Dict[str, str]:
        """Process a prompt through all enabled LLMs."""
        responses = {}
        
        if "openai" in self.enabled_features:
            responses["chatgpt"] = await self.llm.call_chatgpt(prompt)
        if "gemini" in self.enabled_features:
            responses["gemini"] = await self.llm.call_gemini(prompt)
        if "llama" in self.enabled_features:
            responses["llama"] = await self.llm.call_llama(prompt)
        
        return responses
    
    async def process_with_data(
        self,
        data: Any,
        processing_params: Dict[str, Any],
        viz_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process data and optionally create visualizations."""
        results = {}
        
        # Process data
        if "pandas" in self.enabled_features:
            processed_data = await self.data.process_data(data, processing_params)
            results["processed_data"] = processed_data
            
            # Create visualization if requested
            if viz_params and "matplotlib" in self.enabled_features:
                viz_path = await self.data.visualize_data(processed_data, viz_params)
                results["visualization"] = viz_path
        
        return results
    
    async def test_all_features(self):
        """Test all enabled features."""
        print("Testing all enabled features...\n")
        
        # Test LLM features
        if any(feature in ["openai", "gemini", "llama"] for feature in self.enabled_features):
            print("Testing LLM features...")
            await self.llm.test_apis()
        
        # Test data processing features
        if "pandas" in self.enabled_features:
            print("\nTesting data processing features...")
            test_data = pd.DataFrame({
                "A": [1, 2, 3, 4, 5],
                "B": [10, 20, 30, 40, 50]
            })
            try:
                processed = await self.data.process_data(
                    test_data,
                    {"scale": {"method": "standard"}}
                )
                print("Data processing test successful!")
            except Exception as e:
                print(f"Data processing test failed: {e}")
        
        if "matplotlib" in self.enabled_features:
            print("\nTesting visualization features...")
            try:
                viz_path = await self.data.visualize_data(
                    test_data,
                    {
                        "type": "line",
                        "columns": ["A", "B"],
                        "title": "Test Visualization"
                    }
                )
                print(f"Visualization test successful! Saved to {viz_path}")
            except Exception as e:
                print(f"Visualization test failed: {e}")

async def main():
    # Load API keys from environment variables
    api_keys = {
        'openai': os.getenv("OPENAI_API_KEY"),
        'google': os.getenv("GOOGLE_API_KEY"),
        'llama': os.getenv("LLAMA_API_KEY"),
    }
    
    # Initialize orchestrator with all features enabled
    orchestrator = UltraOrchestrator(
        api_keys=api_keys,
        enabled_features=["openai", "gemini", "llama", "pandas", "matplotlib"]
    )
    
    # Test all features
    await orchestrator.test_all_features()
    
    # Example usage
    prompt = "Analyze the following data and provide insights: [Your data here]"
    responses = await orchestrator.process_with_llm(prompt)
    
    # Process data if needed
    data = pd.DataFrame({
        "A": [1, 2, 3, 4, 5],
        "B": [10, 20, 30, 40, 50]
    })
    results = await orchestrator.process_with_data(
        data,
        {"scale": {"method": "standard"}},
        {
            "type": "line",
            "columns": ["A", "B"],
            "title": "Data Analysis"
        }
    )

if __name__ == "__main__":
    asyncio.run(main()) 