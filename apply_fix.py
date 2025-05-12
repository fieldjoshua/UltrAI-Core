#!/usr/bin/env python3
# Analysis fix script
import asyncio
import os
import sys

sys.path.insert(0, os.getcwd())


async def apply_fix():
    # Import modules
    from src.simple_core.analysis.modules.comparative import ComparativeAnalysis
    from src.simple_core.analysis.modules.factual import FactualAnalysis
    from src.simple_core.factory import create_from_env

    # The original analyze methods
    original_comparative = ComparativeAnalysis.analyze
    original_factual = FactualAnalysis.analyze

    # Create patched method
    async def fixed_analyze(self, prompt, responses, options=None):
        options = options or {}

        # Ensure analysis model is set for mock implementation
        if not options.get("analysis_model"):
            # Let the mock method run
            options["_bypass_analysis_model_check"] = True

        return await original_comparative(self, prompt, responses, options)

    async def fixed_factual_analyze(self, prompt, responses, options=None):
        options = options or {}

        # Ensure analysis model is set for mock implementation
        if not options.get("analysis_model"):
            # Let the mock method run
            options["_bypass_analysis_model_check"] = True

        return await original_factual(self, prompt, responses, options)

    # Patch the analyze methods
    ComparativeAnalysis.analyze = fixed_analyze
    FactualAnalysis.analyze = fixed_factual_analyze

    print("Analysis fix applied successfully")


# Run the fix
asyncio.run(apply_fix())
