#!/usr/bin/env python3
"""Check if HuggingFace is configured in production."""

import requests
import json
from datetime import datetime

def check_huggingface_status():
    """Check HuggingFace configuration status."""
    
    base_url = "https://ultrai-core.onrender.com"
    
    print(f"Checking HuggingFace status at {datetime.now()}")
    print("-" * 60)
    
    # Check API keys status
    try:
        response = requests.get(f"{base_url}/api/models/api-keys-status")
        if response.status_code == 200:
            data = response.json()
            hf_status = data.get("huggingface", {})
            print(f"HuggingFace configured: {hf_status.get('configured', False)}")
            if hf_status.get('configured'):
                print(f"Models available: {len(hf_status.get('models', []))}")
        else:
            print(f"API keys status error: {response.status_code}")
    except Exception as e:
        print(f"Error checking API keys: {e}")
    
    print()
    
    # Check available models
    try:
        response = requests.get(f"{base_url}/api/available-models")
        if response.status_code == 200:
            data = response.json()
            total = data.get("total_count", 0)
            print(f"Total models available: {total}")
            
            # Check for HuggingFace models
            models = data.get("models", [])
            hf_models = [m for m in models if m.get("provider") == "huggingface"]
            print(f"HuggingFace models: {len(hf_models)}")
            
            if hf_models:
                print("\nHuggingFace models found:")
                for model in hf_models[:3]:  # Show first 3
                    print(f"  - {model.get('id')}")
        else:
            print(f"Available models error: {response.status_code}")
    except Exception as e:
        print(f"Error checking models: {e}")

if __name__ == "__main__":
    check_huggingface_status()