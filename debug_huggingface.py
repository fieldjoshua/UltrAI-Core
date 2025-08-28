#!/usr/bin/env python3
"""Debug HuggingFace integration to see actual errors."""

import requests
import json

url = "https://ultrai-core.onrender.com/api/orchestrator/analyze"

payload = {
    "query": "Hello, how are you?",
    "selected_models": ["mistralai/Mistral-7B-Instruct-v0.1"],
    "include_pipeline_details": True
}

print("Testing HuggingFace model directly...")
print(f"URL: {url}")
print(f"Model: {payload['selected_models'][0]}")
print("-" * 60)

try:
    response = requests.post(url, json=payload, timeout=60)
    
    if response.status_code == 200:
        data = response.json()
        
        # Save full response for analysis
        with open('huggingface_debug.json', 'w') as f:
            json.dump(data, f, indent=2)
            
        print("Response saved to huggingface_debug.json")
        
        # Extract the actual error
        if 'results' in data and 'initial_response' in data['results']:
            initial = data['results']['initial_response']
            if 'output' in initial and 'responses' in initial['output']:
                responses = initial['output']['responses']
                print(f"\nResponses: {json.dumps(responses, indent=2)}")
        
        # Check if it even tried to use the model
        if 'pipeline_info' in data:
            print(f"\nModels attempted: {data['pipeline_info'].get('models_used', [])}")
            
    else:
        print(f"HTTP {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")