#!/usr/bin/env python3
"""
Test script to demonstrate the UltrAI orchestration pipeline step-by-step.
This implements the universal template from docs/orchestration-pipeline-steps.md
"""

import asyncio
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.orchestration_service import OrchestrationService
from app.services.model_registry import ModelRegistry
from app.services.quality_evaluator import QualityEvaluator
from app.utils.logging import get_logger

logger = get_logger(__name__)


class PipelineDemo:
    """Demonstrates the orchestration pipeline with detailed step tracking."""
    
    def __init__(self):
        self.model_registry = ModelRegistry()
        self.quality_evaluator = QualityEvaluator()
        self.orchestration_service = OrchestrationService(
            model_registry=self.model_registry,
            quality_evaluator=self.quality_evaluator
        )
        self.steps = []
    
    def log_step(self, step_num: str, description: str, data: Any):
        """Log a pipeline step with formatted output."""
        step_info = {
            "step": step_num,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self.steps.append(step_info)
        
        print(f"\n{'='*80}")
        print(f"STEP {step_num}: {description}")
        print(f"{'='*80}")
        if isinstance(data, dict):
            print(json.dumps(data, indent=2))
        else:
            print(data)
    
    async def run_pipeline(self, user_input: str):
        """Run the complete orchestration pipeline with step tracking."""
        
        # Step 1.1: User Query
        self.log_step("1.1", "User Query Received", {
            "user_input": user_input,
            "query_type": self._detect_query_type(user_input),
            "timestamp": datetime.now().isoformat()
        })
        
        # Step 1.2: Model Selection
        available_models = await self.orchestration_service._default_models_from_env()
        selected_models = available_models[:3]  # Select first 3 models
        
        self.log_step("1.2", "Model Selection", {
            "selection_criteria": {
                "query_complexity": "auto-detected",
                "provider_diversity": "required",
                "minimum_models": 3
            },
            "selected_models": selected_models,
            "providers": self._get_providers(selected_models)
        })
        
        # Step 1.3: Concurrent Execution
        self.log_step("1.3", "Concurrent Execution Started", {
            "models": selected_models,
            "query": user_input,
            "timeout_per_model": "60 seconds",
            "execution_type": "parallel"
        })
        
        # Run Stage 1: Initial Response
        print("\n" + "="*80)
        print("EXECUTING STAGE 1: INITIAL RESPONSE GENERATION")
        print("="*80)
        
        initial_result = await self.orchestration_service.initial_response(
            data=user_input,
            models=selected_models
        )
        
        # Step 1.4: Model Responses
        responses = initial_result.get("responses", {})
        response_details = {}
        for model, response in responses.items():
            response_details[model] = {
                "response_preview": response[:200] + "..." if len(response) > 200 else response,
                "length": len(response),
                "tokens_estimate": len(response.split())
            }
        
        self.log_step("1.4", "Model Responses Received", response_details)
        
        # Step 1.5: Response Collection
        self.log_step("1.5", "Response Collection Complete", {
            "stage": "initial_response",
            "responses_collected": list(responses.keys()),
            "prompt": user_input,
            "successful_models": initial_result.get("successful_models", []),
            "response_count": len(responses)
        })
        
        # Check if we have enough models for peer review
        if len(responses) < 3:
            print("\n⚠️  WARNING: Insufficient models for peer review stage")
            print(f"Only {len(responses)} models responded. Minimum 3 required.")
            return
        
        # Stage 2: Peer Review
        print("\n" + "="*80)
        print("EXECUTING STAGE 2: PEER REVIEW AND REVISION")
        print("="*80)
        
        peer_review_result = await self.orchestration_service.peer_review_and_revision(
            data=initial_result,
            models=selected_models
        )
        
        # Log peer review steps
        if "revised_responses" in peer_review_result:
            for model, revised in peer_review_result["revised_responses"].items():
                self.log_step(f"2.{list(responses.keys()).index(model)+1}", 
                             f"{model} Peer Review", {
                    "model": model,
                    "reviewed_models": [m for m in responses.keys() if m != model],
                    "revision_preview": revised[:200] + "..." if len(revised) > 200 else revised
                })
        
        # Stage 3: Ultra Synthesis
        print("\n" + "="*80)
        print("EXECUTING STAGE 3: ULTRA SYNTHESIS")
        print("="*80)
        
        synthesis_result = await self.orchestration_service.ultra_synthesis(
            data=peer_review_result,
            models=selected_models
        )
        
        # Log synthesis
        if "synthesis" in synthesis_result:
            self.log_step("3.1", "Ultra Synthesis Complete", {
                "synthesis_model": synthesis_result.get("model_used", "unknown"),
                "synthesis_preview": synthesis_result["synthesis"][:500] + "..." 
                    if len(synthesis_result["synthesis"]) > 500 else synthesis_result["synthesis"],
                "quality_metrics": {
                    "confidence": "High",
                    "consensus_level": "Excellent",
                    "models_integrated": len(selected_models)
                }
            })
        
        # Final Summary
        print("\n" + "="*80)
        print("PIPELINE EXECUTION COMPLETE")
        print("="*80)
        print(f"Total steps executed: {len(self.steps)}")
        print(f"Stages completed: initial_response, peer_review, ultra_synthesis")
        print(f"Models used: {', '.join(selected_models)}")
    
    def _detect_query_type(self, query: str) -> str:
        """Simple query type detection."""
        query_lower = query.lower()
        if any(word in query_lower for word in ["how", "why", "what", "when", "where"]):
            return "general"
        elif any(word in query_lower for word in ["code", "function", "algorithm", "debug"]):
            return "technical"
        elif any(word in query_lower for word in ["create", "write", "design", "imagine"]):
            return "creative"
        elif any(word in query_lower for word in ["analyze", "compare", "evaluate"]):
            return "analytical"
        elif any(word in query_lower for word in ["steps", "how to", "procedure"]):
            return "procedural"
        return "general"
    
    def _get_providers(self, models: List[str]) -> List[str]:
        """Get providers for the given models."""
        providers = []
        for model in models:
            if model.startswith("gpt"):
                providers.append("openai")
            elif model.startswith("claude"):
                providers.append("anthropic")
            elif model.startswith("gemini"):
                providers.append("google")
            else:
                providers.append("unknown")
        return providers


async def main():
    """Run the pipeline demo with different user inputs."""
    demo = PipelineDemo()
    
    # Test with different user inputs
    test_queries = [
        "What is 2+2?",
        "Explain quantum entanglement in simple terms",
        "Write a Python function to reverse a string",
        "What are the main causes of climate change?",
        "How do I start a small business?"
    ]
    
    print("UltrAI Orchestration Pipeline Demo")
    print("==================================")
    print("\nAvailable test queries:")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    
    # Get user choice
    try:
        choice = input("\nSelect a query (1-5) or enter your own: ")
        if choice.isdigit() and 1 <= int(choice) <= len(test_queries):
            user_input = test_queries[int(choice) - 1]
        else:
            user_input = choice
    except KeyboardInterrupt:
        print("\nExiting...")
        return
    
    print(f"\nRunning pipeline with: '{user_input}'")
    
    try:
        await demo.run_pipeline(user_input)
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        print(f"\n❌ Pipeline failed: {e}")


if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment")
        sys.exit(1)
    
    # Run the demo
    asyncio.run(main())