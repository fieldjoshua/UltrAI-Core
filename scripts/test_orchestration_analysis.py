#!/usr/bin/env python3
"""
Test implementation for the /api/orchestrator/analyze endpoint.
This demonstrates the exact step-by-step flow of the orchestration analysis.
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")  # Set this if auth is required


class OrchestrationAnalysisDemo:
    """Demonstrates the orchestration analysis pipeline."""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json"
        }
        if AUTH_TOKEN:
            self.headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    def print_step(self, step: str, title: str, data: Any):
        """Pretty print a pipeline step."""
        print(f"\n{'='*80}")
        print(f"📍 STEP {step}: {title}")
        print(f"{'='*80}")
        if isinstance(data, dict):
            print(json.dumps(data, indent=2, default=str))
        else:
            print(data)
    
    async def test_orchestration_analyze(self, user_input: str, options: Optional[Dict] = None):
        """Test the /api/orchestrator/analyze endpoint with detailed step tracking."""
        
        # Step 1.1: Prepare the request
        request_data = {
            "query": user_input,
            "analysis_type": "general",
            "include_pipeline_details": True,  # Get full pipeline details
            "include_initial_responses": True,  # Include Stage 1 responses
            "save_outputs": False,
            "options": options or {}
        }
        
        self.print_step("1.1", "User Query Prepared", {
            "user_input": user_input,
            "endpoint": "/api/orchestrator/analyze",
            "request_body": request_data
        })
        
        async with aiohttp.ClientSession() as session:
            try:
                # Make the API call
                url = f"{self.base_url}/api/orchestrator/analyze"
                self.print_step("1.2", "Sending Request to Orchestration Service", {
                    "url": url,
                    "method": "POST",
                    "headers": {k: v for k, v in self.headers.items() if k != "Authorization"}
                })
                
                async with session.post(url, json=request_data, headers=self.headers) as response:
                    result = await response.json()
                    
                    if response.status != 200:
                        self.print_step("ERROR", "Request Failed", {
                            "status": response.status,
                            "error": result
                        })
                        return
                    
                    # Parse the response
                    self._parse_orchestration_response(result, user_input)
                    
            except aiohttp.ClientError as e:
                self.print_step("ERROR", "Connection Failed", {
                    "error": str(e),
                    "suggestion": "Make sure the API server is running"
                })
    
    def _parse_orchestration_response(self, response: Dict[str, Any], user_input: str):
        """Parse and display the orchestration response step by step."""
        
        # Check if we got pipeline details
        if not response.get("success"):
            self.print_step("ERROR", "Analysis Failed", {
                "error": response.get("error", "Unknown error")
            })
            return
        
        results = response.get("results", {})
        pipeline_info = response.get("pipeline_info", {})
        
        # Step 1.3-1.5: Initial Response Stage
        if "initial_response" in results:
            initial_stage = results["initial_response"]
            if isinstance(initial_stage, dict) and "output" in initial_stage:
                initial_data = initial_stage["output"]
                
                # Step 1.3: Show concurrent execution
                self.print_step("1.3", "Concurrent Model Execution", {
                    "models_attempted": initial_data.get("models_attempted", []),
                    "execution_type": "parallel",
                    "stage": "initial_response"
                })
                
                # Step 1.4: Show individual model responses
                responses = initial_data.get("responses", {})
                for i, (model, response_text) in enumerate(responses.items(), 1):
                    self.print_step(f"1.4.{i}", f"Model Response: {model}", {
                        "model": model,
                        "response_preview": response_text[:300] + "..." if len(response_text) > 300 else response_text,
                        "response_length": len(response_text)
                    })
                
                # Step 1.5: Response collection summary
                self.print_step("1.5", "Initial Response Collection Complete", {
                    "successful_models": initial_data.get("successful_models", []),
                    "response_count": initial_data.get("response_count", 0),
                    "original_query": initial_data.get("prompt", user_input)
                })
        
        # Stage 2: Peer Review (if available)
        if "peer_review_and_revision" in results:
            peer_stage = results["peer_review_and_revision"]
            if isinstance(peer_stage, dict) and "output" in peer_stage:
                peer_data = peer_stage["output"]
                
                if peer_data.get("skipped"):
                    self.print_step("2.0", "Peer Review Stage Skipped", {
                        "reason": peer_data.get("reason", "Unknown"),
                        "stage": "peer_review_and_revision"
                    })
                else:
                    # Show revised responses
                    revised = peer_data.get("revised_responses", {})
                    for i, (model, revised_text) in enumerate(revised.items(), 1):
                        self.print_step(f"2.{i}", f"Peer Review: {model}", {
                            "model": model,
                            "reviewed_peers": [m for m in revised.keys() if m != model],
                            "revision_preview": revised_text[:300] + "..." if len(revised_text) > 300 else revised_text
                        })
        
        # Stage 3: Ultra Synthesis
        if "ultra_synthesis" in results:
            synthesis = results["ultra_synthesis"]
            if isinstance(synthesis, str):
                synthesis_text = synthesis
            elif isinstance(synthesis, dict):
                synthesis_text = synthesis.get("synthesis", str(synthesis))
            else:
                synthesis_text = str(synthesis)
            
            self.print_step("3.1", "Ultra Synthesis™ Complete", {
                "synthesis_preview": synthesis_text[:500] + "..." if len(synthesis_text) > 500 else synthesis_text,
                "full_length": len(synthesis_text)
            })
            
            # Show full synthesis
            self.print_step("3.2", "Full Ultra Synthesis Result", synthesis_text)
        
        # Pipeline Summary
        self.print_step("FINAL", "Pipeline Execution Summary", {
            "processing_time": response.get("processing_time", "N/A"),
            "stages_completed": pipeline_info.get("stages_completed", []),
            "models_used": pipeline_info.get("models_used", []),
            "pipeline_type": pipeline_info.get("pipeline_type", "unknown")
        })


async def main():
    """Run the orchestration analysis demo."""
    demo = OrchestrationAnalysisDemo()
    
    # Test queries matching the template
    test_queries = [
        "What is 2+2?",
        "Explain quantum entanglement",
        "Write a Python function to sort a list",
        "What are the causes of climate change?",
        "How do I start a small business?"
    ]
    
    print("🚀 UltrAI Orchestration Analysis Demo")
    print("=====================================")
    print("\nThis demonstrates the /api/orchestrator/analyze endpoint")
    print("following the step-by-step process from the documentation.\n")
    
    print("Available test queries:")
    for i, query in enumerate(test_queries, 1):
        print(f"{i}. {query}")
    
    try:
        choice = input("\nSelect a query (1-5) or enter your own: ")
        if choice.isdigit() and 1 <= int(choice) <= len(test_queries):
            user_input = test_queries[int(choice) - 1]
        else:
            user_input = choice
    except KeyboardInterrupt:
        print("\nExiting...")
        return
    
    print(f"\n🔄 Running orchestration analysis with: '{user_input}'")
    
    # Run the test
    await demo.test_orchestration_analyze(user_input)


if __name__ == "__main__":
    # Check if API is reachable
    import requests
    try:
        health_check = requests.get(f"{API_BASE_URL}/api/health", timeout=2)
        if health_check.status_code != 200:
            print(f"⚠️  API health check failed: {health_check.status_code}")
            print("Make sure the API server is running")
    except requests.RequestException as e:
        print(f"❌ Cannot reach API at {API_BASE_URL}")
        print(f"Error: {e}")
        print("\nTo run the API server locally:")
        print("  make dev")
        print("\nOr set API_URL environment variable:")
        print("  export API_URL=https://ultrai-staging-api.onrender.com")
        exit(1)
    
    # Run the async main
    asyncio.run(main())