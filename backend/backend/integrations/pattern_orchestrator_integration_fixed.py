"""
Pattern Orchestrator Integration for Backend - FIXED VERSION
This provides a cleaner integration point for the sophisticated orchestrator
"""

import os
import sys
import logging

logger = logging.getLogger(__name__)

# Ensure src directory is in path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
src_dir = os.path.join(root_dir, "src")

for directory in [root_dir, src_dir]:
    if directory not in sys.path and os.path.exists(directory):
        sys.path.insert(0, directory)

# Now import the orchestrator
try:
    from src.core.ultra_pattern_orchestrator import PatternOrchestrator as OriginalPatternOrchestrator
    from src.patterns.ultra_analysis_patterns import get_pattern_mapping
    
    # Create a wrapper to fix the model name mapping issue
    class PatternOrchestrator(OriginalPatternOrchestrator):
        """Fixed PatternOrchestrator that properly maps model names"""
        
        def _initialize_clients(self):
            """Initialize API clients with proper model name mapping"""
            super()._initialize_clients()
            
            # Fix the available_models to use the names the code expects
            fixed_models = []
            model_mapping = {
                "anthropic": "claude",
                "openai": "chatgpt",
                "google": "gemini",
                "mistral": "mistral",
                "cohere": "cohere",
                "perplexity": "perplexity",
                "deepseek": "deepseek"
            }
            
            for model in self.available_models:
                mapped_name = model_mapping.get(model, model)
                if mapped_name not in fixed_models:
                    fixed_models.append(mapped_name)
            
            self.available_models = fixed_models
            logger.info(f"Fixed available models: {self.available_models}")
    
    ORCHESTRATOR_AVAILABLE = True
    logger.info("✅ Successfully imported and fixed PatternOrchestrator")
    
except ImportError as e:
    logger.error(f"Warning: Could not import PatternOrchestrator: {e}")
    # Provide fallback implementations
    class PatternOrchestrator:
        """Fallback PatternOrchestrator for when imports fail"""
        def __init__(self, api_keys, pattern="gut", output_format="plain"):
            self.api_keys = api_keys
            self.pattern = pattern
            self.output_format = output_format
            self.available_models = []
            
            # Map API keys to expected model names
            if api_keys.get("anthropic"):
                self.available_models.append("claude")
            if api_keys.get("openai"):
                self.available_models.append("chatgpt")
            if api_keys.get("google"):
                self.available_models.append("gemini")
            if api_keys.get("mistral"):
                self.available_models.append("mistral")
            if api_keys.get("cohere"):
                self.available_models.append("cohere")
            if api_keys.get("perplexity"):
                self.available_models.append("perplexity")
            if api_keys.get("deepseek"):
                self.available_models.append("deepseek")
        
        async def orchestrate_full_process(self, prompt):
            return {
                "initial_responses": {"mock": "PatternOrchestrator not available"},
                "meta_responses": {"mock": "Import failed in production"},
                "hyper_responses": {"mock": "Check logs for import errors"},
                "ultra_response": "PatternOrchestrator import failed. Check deployment configuration.",
                "processing_time": 0.0
            }
    
    def get_pattern_mapping():
        return {
            "gut": {"name": "gut", "description": "Relies on LLM intuition", "stages": ["initial", "meta", "hyper", "ultra"]},
            "confidence": {"name": "confidence", "description": "Analyzes with confidence scoring", "stages": ["initial", "meta", "hyper", "ultra"]},
            "critique": {"name": "critique", "description": "Structured critique process", "stages": ["initial", "meta", "hyper", "ultra"]},
            "fact_check": {"name": "fact_check", "description": "Rigorous fact-checking", "stages": ["initial", "meta", "hyper", "ultra"]},
            "perspective": {"name": "perspective", "description": "Different analytical perspectives", "stages": ["initial", "meta", "hyper", "ultra"]},
            "scenario": {"name": "scenario", "description": "Scenario-based analysis", "stages": ["initial", "meta", "hyper", "ultra"]},
            "stakeholder": {"name": "stakeholder", "description": "Multiple stakeholder perspectives", "stages": ["initial", "meta", "hyper", "ultra"]},
            "systems": {"name": "systems", "description": "System dynamics mapping", "stages": ["initial", "meta", "hyper", "ultra"]},
            "time": {"name": "time", "description": "Multi-timeframe analysis", "stages": ["initial", "meta", "hyper", "ultra"]},
            "innovation": {"name": "innovation", "description": "Cross-domain pattern discovery", "stages": ["initial", "meta", "hyper", "ultra"]}
        }
    
    ORCHESTRATOR_AVAILABLE = False

# Export the orchestrator components
__all__ = ["PatternOrchestrator", "get_pattern_mapping", "ORCHESTRATOR_AVAILABLE"]