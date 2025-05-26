"""
Pattern Orchestrator Integration for Backend
This provides a cleaner integration point for the sophisticated orchestrator
"""

import os
import sys

# Ensure src directory is in path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root_dir = os.path.dirname(backend_dir)
src_dir = os.path.join(root_dir, "src")

for directory in [root_dir, src_dir]:
    if directory not in sys.path and os.path.exists(directory):
        sys.path.insert(0, directory)

# Now import the orchestrator
try:
    from src.core.ultra_pattern_orchestrator import PatternOrchestrator
    from src.patterns.ultra_analysis_patterns import get_pattern_mapping
    ORCHESTRATOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import PatternOrchestrator: {e}")
    # Provide fallback implementations
    class PatternOrchestrator:
        """Fallback PatternOrchestrator for when imports fail"""
        def __init__(self, api_keys, pattern="gut", output_format="plain"):
            self.api_keys = api_keys
            self.pattern = pattern
            self.output_format = output_format
            self.available_models = list(api_keys.keys()) if api_keys else []
        
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
            "gut": None,
            "confidence": None,
            "critique": None,
            "fact_check": None,
            "perspective": None,
            "scenario": None
        }
    
    ORCHESTRATOR_AVAILABLE = False

# Export the orchestrator components
__all__ = ["PatternOrchestrator", "get_pattern_mapping", "ORCHESTRATOR_AVAILABLE"]
