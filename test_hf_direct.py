#!/usr/bin/env python3
"""Test HuggingFace API directly to verify the key works."""

import requests
import os
from datetime import datetime

# Test if we can access HuggingFace API directly with your key
def test_huggingface_api_direct():
    """Test the HuggingFace API directly."""
    
    # Use the key provided by the user for testing
    api_key = "REDACTED_HF"
    
    model_id = "mistralai/Mistral-7B-Instruct-v0.1"
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "inputs": "<s>[INST] Say hello in one sentence. [/INST]",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.7
        }
    }
    
    print(f"Testing HuggingFace API at {datetime.now()}")
    print(f"Model: {model_id}")
    print(f"URL: {url}")
    print("-" * 60)
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Key is valid!")
            data = response.json()
            print(f"Response: {data}")
        elif response.status_code == 401:
            print("❌ API Key is invalid or not authorized")
        elif response.status_code == 503:
            print("⏳ Model is loading, this is normal for first request")
            print("Response:", response.json())
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_huggingface_api_direct()