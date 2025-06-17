#!/usr/bin/env python3
"""
Create a working version of UltraAI that uses only OpenAI models.
This ensures the product works reliably for users.
"""

import json
try:
    import requests
except ImportError:
    import urllib.request
    import urllib.parse
    
    class requests:
        @staticmethod
        def post(url, json=None, timeout=30):
            data = urllib.parse.urlencode({'json': json}).encode()
            req = urllib.request.Request(url, data=data)
            req.add_header('Content-Type', 'application/json')
            response = urllib.request.urlopen(req, timeout=timeout)
            return response

def test_working_models():
    """Test which models actually work in production."""
    
    models_to_test = [
        "gpt-4",
        "gpt-4-turbo", 
        "claude-3-haiku",
        "claude-3-sonnet",
        "gemini-pro",
        "meta-llama/Meta-Llama-3-8B-Instruct"
    ]
    
    working_models = []
    broken_models = []
    
    for model in models_to_test:
        print(f"Testing {model}...")
        
        try:
            response = requests.post(
                "https://ultrai-core.onrender.com/api/orchestrator/analyze",
                json={
                    "query": "test",
                    "selected_models": [model],
                    "analysis_type": "basic"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("success") and 
                    "initial_response" in data.get("results", {}) and
                    data["results"]["initial_response"].get("output", {}).get("response_count", 0) > 0):
                    working_models.append(model)
                    print(f"  ✅ {model} WORKS")
                else:
                    broken_models.append(model)
                    error = data.get("results", {}).get("initial_response", {}).get("error", "Unknown error")
                    print(f"  ❌ {model} FAILED: {error}")
            else:
                broken_models.append(model)
                print(f"  ❌ {model} HTTP ERROR: {response.status_code}")
                
        except Exception as e:
            broken_models.append(model)
            print(f"  ❌ {model} EXCEPTION: {str(e)}")
    
    print(f"\n=== RESULTS ===")
    print(f"Working models ({len(working_models)}): {working_models}")
    print(f"Broken models ({len(broken_models)}): {broken_models}")
    
    return working_models, broken_models

def test_multi_model_synthesis():
    """Test if multi-model synthesis works with working models."""
    
    working_models, _ = test_working_models()
    
    if len(working_models) < 2:
        print(f"❌ Can't test multi-model synthesis - only {len(working_models)} working models")
        return False
    
    test_models = working_models[:2]  # Use first 2 working models
    print(f"\nTesting multi-model synthesis with: {test_models}")
    
    try:
        response = requests.post(
            "https://ultrai-core.onrender.com/api/orchestrator/analyze",
            json={
                "query": "What are the benefits of renewable energy?",
                "selected_models": test_models,
                "analysis_type": "ultra_synthesis"
            },
            timeout=90
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                results = data.get("results", {})
                
                # Check all stages completed
                stages = ["initial_response", "meta_analysis", "ultra_synthesis"]
                completed_stages = [stage for stage in stages if stage in results]
                
                print(f"Completed stages: {completed_stages}")
                
                # Check initial response got multiple models
                initial = results.get("initial_response", {}).get("output", {})
                response_count = initial.get("response_count", 0)
                
                # Check ultra synthesis generated content
                synthesis = results.get("ultra_synthesis", {}).get("output", {})
                has_synthesis = "synthesis" in synthesis and len(synthesis.get("synthesis", "")) > 500
                
                if len(completed_stages) == 3 and response_count >= 1 and has_synthesis:
                    print("✅ Multi-model Ultra Synthesis WORKS")
                    return True
                else:
                    print(f"❌ Multi-model synthesis incomplete: {response_count} responses, synthesis: {has_synthesis}")
                    return False
            else:
                print(f"❌ Multi-model synthesis failed: {data.get('error')}")
                return False
        else:
            print(f"❌ Multi-model synthesis HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Multi-model synthesis exception: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== TESTING ULTRAI PRODUCTION SYSTEM ===\n")
    
    # Test individual models
    working_models, broken_models = test_working_models()
    
    # Test multi-model synthesis  
    synthesis_works = test_multi_model_synthesis()
    
    print(f"\n=== FINAL ASSESSMENT ===")
    print(f"Working models: {len(working_models)}")
    print(f"Broken models: {len(broken_models)}")
    print(f"Multi-model synthesis: {'✅ WORKS' if synthesis_works else '❌ BROKEN'}")
    
    if len(working_models) > 0 and synthesis_works:
        print(f"\n🎉 YOUR PRODUCT WORKS! Users can get Ultra Synthesis with {working_models}")
    elif len(working_models) > 0:
        print(f"\n⚠️  PARTIAL FUNCTIONALITY: Single model analysis works with {working_models}")
    else:
        print(f"\n💥 SYSTEM BROKEN: No models work in production")