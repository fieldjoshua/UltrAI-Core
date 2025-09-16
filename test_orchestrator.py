#!/usr/bin/env python
"""Test script for the orchestrator endpoint"""
import os
import asyncio
import httpx
import json

# Disable authentication for testing
os.environ["ENABLE_AUTH"] = "false"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-for-mvp-audit-12345"

async def test_orchestrator():
    """Test the orchestrator analyze endpoint"""
    url = "http://localhost:8000/api/orchestrator/analyze"
    payload = {
        "query": "What is the meaning of life?",
        "num_models": 3
    }
    
    print(f"Testing {url} with payload: {json.dumps(payload, indent=2)}")
    print("-" * 80)
    
    async with httpx.AsyncClient(timeout=180.0) as client:
        try:
            response = await client.post(url, json=payload)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            print("-" * 80)
            
            if response.status_code == 200:
                data = response.json()
                print("Response:")
                print(json.dumps(data, indent=2))
            else:
                print(f"Error Response: {response.text}")
                
        except httpx.TimeoutException:
            print("Request timed out after 180 seconds")
        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    # Start the server first
    import subprocess
    import time
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    print("Starting server...")
    server_process = subprocess.Popen([
        "python", "-m", "uvicorn", "app.main:app", 
        "--host", "0.0.0.0", "--port", "8000"
    ])
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Run the test
        asyncio.run(test_orchestrator())
    finally:
        # Kill the server
        print("\nStopping server...")
        server_process.terminate()
        server_process.wait()