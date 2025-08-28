#!/usr/bin/env python3
"""Test HuggingFace models in the orchestration pipeline."""

import requests
import json
import time
from datetime import datetime

def test_single_huggingface_model(model_name):
    """Test a single HuggingFace model."""
    
    url = "https://ultrai-core.onrender.com/api/orchestrator/analyze"
    
    payload = {
        "query": "Write a haiku about artificial intelligence",
        "selected_models": [model_name],
        "include_pipeline_details": True
    }
    
    print(f"\nTesting {model_name}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                # Check if model responded
                if 'results' in data and 'initial_response' in data['results']:
                    initial = data['results']['initial_response']
                    if 'output' in initial and 'responses' in initial['output']:
                        responses = initial['output']['responses']
                        if model_name in responses:
                            text = str(responses[model_name])
                            if "error" in text.lower():
                                print(f"❌ Error: {text[:200]}")
                            else:
                                print(f"✅ Success! Response preview:")
                                print(f"   {text[:150]}...")
                        else:
                            print(f"❌ Model didn't respond")
                            # Check which models did respond
                            if responses:
                                print(f"   Responses from: {list(responses.keys())}")
                else:
                    print(f"❌ No initial response in results")
            else:
                print(f"❌ Request failed: {data.get('error', 'Unknown error')}")
                
        else:
            print(f"❌ HTTP {response.status_code}: {response.text[:200]}")
            
    except requests.exceptions.Timeout:
        print(f"⏱️  Request timed out (60s)")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_huggingface_orchestration():
    """Test HuggingFace models with other models in orchestration."""
    
    url = "https://ultrai-core.onrender.com/api/orchestrator/analyze"
    
    payload = {
        "query": "What are the main differences between supervised and unsupervised learning?",
        "selected_models": [
            "gpt-3.5-turbo",
            "mistralai/Mistral-7B-Instruct-v0.1",
            "claude-3-5-haiku-20241022"
        ],
        "include_pipeline_details": True
    }
    
    print(f"\nTesting HuggingFace in Multi-Model Orchestration")
    print("=" * 80)
    print(f"Models: {payload['selected_models']}")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ Success: {data.get('success')}")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            
            if 'pipeline_info' in data:
                info = data['pipeline_info']
                print(f"\n📊 Pipeline Info:")
                print(f"   Stages: {info.get('stages_completed')}")
                print(f"   Models used: {info.get('models_used')}")
            
            # Check each model's response
            if 'results' in data and 'initial_response' in data['results']:
                initial = data['results']['initial_response']
                if 'output' in initial:
                    print(f"\n📝 Model Responses:")
                    responses = initial['output'].get('responses', {})
                    successful = initial['output'].get('successful_models', [])
                    
                    for model in payload['selected_models']:
                        if model in responses:
                            resp = str(responses[model])
                            if "error" in resp.lower():
                                print(f"   {model}: ❌ {resp[:100]}")
                            else:
                                print(f"   {model}: ✅ Responded successfully")
                        else:
                            print(f"   {model}: ⚠️  No response")
                    
                    print(f"\n   Successful models: {successful}")
                    
        else:
            print(f"❌ HTTP {response.status_code}")
            print(response.text[:500])
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print(f"Testing HuggingFace Integration at {datetime.now()}")
    print("=" * 80)
    
    # Test individual models
    hf_models = [
        "mistralai/Mistral-7B-Instruct-v0.1",  # Usually most reliable
        "microsoft/phi-2",                       # Small and fast
        "google/gemma-7b-it",                   # Google's open model
    ]
    
    print("\n1. Testing Individual HuggingFace Models:")
    for model in hf_models:
        test_single_huggingface_model(model)
        time.sleep(2)  # Be nice to the API
    
    print("\n\n2. Testing HuggingFace in Multi-Model Orchestration:")
    test_huggingface_orchestration()
    
    print("\n\nNote: If models show 'Model is loading', wait 30 seconds and try again.")
    print("First request to a HuggingFace model triggers loading on their servers.")