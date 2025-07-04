#!/usr/bin/env python3
"""Comprehensive test of Ultra Synthesis optimization features"""

import asyncio
import json
from app.main import app, initialize_services
from app.routes.orchestrator_minimal import AnalysisRequest
from fastapi.testclient import TestClient

async def test_all_features():
    """Test all Ultra Synthesis optimization features"""
    
    # Initialize services
    services = initialize_services()
    
    # Create test client
    client = TestClient(app)
    
    print("🧪 ULTRA SYNTHESIS™ OPTIMIZATION TEST SUITE")
    print("=" * 60)
    print()
    
    # Test scenarios
    test_cases = [
        {
            "name": "1️⃣ Technical Query - Enhanced Synthesis",
            "query": "Explain the advantages of microservices architecture",
            "models": ["gpt-4o", "claude-3-5-sonnet-20241022", "gemini-1.5-pro"]
        },
        {
            "name": "2️⃣ Creative Query - Multiple Perspectives",
            "query": "Write a haiku about artificial intelligence",
            "models": ["gpt-4o-mini", "claude-3-5-haiku-20241022", "gemini-1.5-flash"]
        },
        {
            "name": "3️⃣ Analytical Query - Confidence Levels",
            "query": "Compare React vs Vue.js for enterprise applications",
            "models": ["gpt-4o", "claude-3-5-sonnet-20241022"]
        }
    ]
    
    for i, test in enumerate(test_cases):
        print(f"\n{'='*60}")
        print(f"{test['name']}")
        print(f"{'='*60}")
        print(f"Query: {test['query']}")
        print(f"Models: {', '.join(test['models'])}")
        print()
        
        # Test 1: Default (streamlined output)
        print("📊 Testing Default Output (Streamlined)...")
        response = client.post(
            "/api/orchestrator/analyze",
            json={
                "query": test['query'],
                "selected_models": test['models']
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                synthesis = result['results'].get('ultra_synthesis', '')
                
                # Extract quality metrics
                if "Synthesis Quality Metrics:" in synthesis:
                    print("✅ Quality Metrics Found!")
                    metrics_section = synthesis.split("Synthesis Quality Metrics:")[1].split("---")[0]
                    for line in metrics_section.split('\n'):
                        if line.strip().startswith('-'):
                            print(f"   {line.strip()}")
                
                # Check for confidence indicators
                confidence_count = synthesis.count('[High confidence]') + synthesis.count('[Moderate confidence]') + synthesis.count('[Low confidence]')
                print(f"✅ Confidence Indicators: {confidence_count} found")
                
                # Check synthesis length
                print(f"✅ Synthesis Length: {len(synthesis)} characters")
                
                # Save for inspection
                with open(f"/tmp/test_result_{i+1}_default.json", "w") as f:
                    json.dump(result, f, indent=2)
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
        
        # Test 2: With pipeline details
        print("\n📊 Testing Pipeline Details Output...")
        response = client.post(
            "/api/orchestrator/analyze",
            json={
                "query": test['query'],
                "selected_models": test['models'],
                "include_pipeline_details": True
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                results = result.get('results', {})
                
                # Check for all stages
                stages_found = []
                for stage in ['initial_response', 'peer_review_and_revision', 'ultra_synthesis']:
                    if stage in results:
                        stages_found.append(stage)
                        stage_data = results[stage]
                        if isinstance(stage_data, dict) and 'output' in stage_data:
                            output = stage_data['output']
                            if stage == 'initial_response' and isinstance(output, dict) and 'responses' in output:
                                print(f"   ✅ {stage}: {len(output['responses'])} models responded")
                            elif stage == 'peer_review_and_revision' and isinstance(output, dict):
                                if 'revised_responses' in output:
                                    print(f"   ✅ {stage}: {len(output['revised_responses'])} revisions")
                            elif stage == 'ultra_synthesis':
                                print(f"   ✅ {stage}: synthesis generated")
                
                print(f"✅ Pipeline Stages Found: {', '.join(stages_found)}")
                
                # Save for inspection
                with open(f"/tmp/test_result_{i+1}_pipeline.json", "w") as f:
                    json.dump(result, f, indent=2)
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
        
        await asyncio.sleep(2)  # Rate limiting
    
    # Test model availability endpoint
    print(f"\n{'='*60}")
    print("4️⃣ Model Availability Check")
    print(f"{'='*60}")
    
    response = client.get("/api/available-models")
    if response.status_code == 200:
        models_data = response.json()
        available = [m['name'] for m in models_data.get('models', []) if m.get('status') == 'available']
        print(f"✅ Available Models: {len(available)}")
        print(f"   Models: {', '.join(available[:5])}...")
    else:
        print(f"❌ Failed to get model availability")
    
    print("\n✅ Testing Complete!")
    print("\nTest results saved to:")
    for i in range(len(test_cases)):
        print(f"  - /tmp/test_result_{i+1}_default.json")
        print(f"  - /tmp/test_result_{i+1}_pipeline.json")

if __name__ == "__main__":
    asyncio.run(test_all_features())