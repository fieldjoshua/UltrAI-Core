"""
Test the enhanced orchestrator with a specific prompt

This script runs a sample prompt through the enhanced orchestrator
to demonstrate the multi-stage processing workflow.
"""

import asyncio
import logging
import json
from typing import Dict, Any

from src.simple_core.factory import create_from_env
from src.simple_core.config import Config, ModelDefinition

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

TEST_PROMPT = "What are the most important skills for a startup founder?"

async def run_enhanced_test():
    print("\n" + "="*80)
    print("Enhanced Orchestrator Test")
    print("="*80)
    
    # Create the enhanced orchestrator from environment variables
    orchestrator = create_from_env(enhanced=True)
    
    if not orchestrator:
        print("Failed to create orchestrator. Please check API keys in environment.")
        print("Required environment variables (at least one needed):")
        print("  - OPENAI_API_KEY (for OpenAI models)")
        print("  - ANTHROPIC_API_KEY (for Anthropic models)")
        print("  - GOOGLE_API_KEY (for Google/Gemini models)")
        return
    
    print(f"\nProcessing prompt: {TEST_PROMPT}")
    print("\nThis will generate:")
    print("1. Initial responses from all configured models")
    print("2. Meta-analyses of those responses (comparing them)")
    print("3. A synthesized final response")
    print("\nWorking...\n")
    
    # Process the prompt
    result = await orchestrator.process({"prompt": TEST_PROMPT})
    
    # Display initial responses
    print("\n--- Initial Responses ---")
    for i, response in enumerate(result.get('initial_responses', []), 1):
        model = response.get('model', 'Unknown')
        provider = response.get('provider', 'Unknown')
        response_text = response.get('response', '')
        time = response.get('response_time', 0)
        quality = response.get('quality_score', None)
        
        quality_str = f", Quality Score: {quality:.2f}" if quality is not None else ""
        print(f"\n[{i}] {model} ({provider}, {time:.2f}s{quality_str}):")
        print("-" * 40)
        print(response_text)
    
    # Display meta-analyses
    if result.get('meta_analyses'):
        print("\n\n" + "="*80)
        print("--- Meta-Analyses ---")
        for i, analysis in enumerate(result.get('meta_analyses', []), 1):
            model = analysis.get('model', 'Unknown')
            provider = analysis.get('provider', 'Unknown')
            analysis_text = analysis.get('analysis', '')
            
            print(f"\n[{i}] Analysis by {model} ({provider}):")
            print("-" * 40)
            print(analysis_text)
    
    # Display synthesis
    if result.get('synthesis'):
        print("\n\n" + "="*80)
        print("--- Synthesized Response ---")
        synthesis = result.get('synthesis', {})
        model = synthesis.get('model', 'Unknown')
        provider = synthesis.get('provider', 'Unknown')
        response_text = synthesis.get('response', '')
        
        print(f"Synthesized by {model} ({provider}):")
        print("-" * 40)
        print(response_text)
    
    # Display selected best response
    if result.get('selected_response'):
        print("\n\n" + "="*80)
        print("--- Selected Best Response ---")
        selected = result.get('selected_response', {})
        model = selected.get('model', 'Unknown')
        provider = selected.get('provider', 'Unknown')
        quality = selected.get('quality_score', None)
        
        quality_str = f", Quality Score: {quality:.2f}" if quality is not None else ""
        print(f"Selected response: {model} ({provider}{quality_str})")
    
    print("\n" + "="*80)
    print("Test completed!")
    print("="*80 + "\n")

if __name__ == "__main__":
    asyncio.run(run_enhanced_test())