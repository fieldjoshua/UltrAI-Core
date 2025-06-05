#!/usr/bin/env python3
"""
Debug production orchestration issue
"""

import requests
import time

# First, let's check if the models are being initialized
print("1. Checking available models...")
response = requests.get("https://ultrai-core.onrender.com/api/orchestrator/models")
print(f"Models: {response.json()}")

# Check if test endpoint works
print("\n2. Checking test endpoint...")
response = requests.get("https://ultrai-core.onrender.com/api/orchestrator/test")
print(f"Test: {response.json()}")

# Try the legacy process endpoint instead of feather
print("\n3. Trying legacy /process endpoint...")
start = time.time()
try:
    response = requests.post(
        "https://ultrai-core.onrender.com/api/orchestrator/process",
        json={"prompt": "Hi", "analysis_type": "comparative"},
        timeout=30
    )
    print(f"Response in {time.time() - start:.2f}s: {response.status_code}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)
except Exception as e:
    print(f"Error after {time.time() - start:.2f}s: {e}")

# Try with a very simple prompt on feather
print("\n4. Trying feather with minimal prompt...")
start = time.time()
try:
    response = requests.post(
        "https://ultrai-core.onrender.com/api/orchestrator/feather",
        json={"prompt": "Hi"},
        timeout=30
    )
    print(f"Response in {time.time() - start:.2f}s: {response.status_code}")
    if response.status_code == 200:
        print(response.json())
    else:
        print(response.text)
except Exception as e:
    print(f"Error after {time.time() - start:.2f}s: {e}")