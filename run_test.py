#!/usr/bin/env python3
"""
Test script that starts the server, runs tests, and stops the server.
"""

import multiprocessing
import os
import subprocess
import sys
import time
import requests
import json

def start_server():
    """Start the backend server in a subprocess."""
    # Set the current directory in PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd()
    
    # Start the server with mock mode
    server_proc = subprocess.Popen(
        ["python3", "backend/app.py", "--mock"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    
    # Wait for the server to start
    print("Starting server...")
    time.sleep(5)  # Give the server time to start
    
    return server_proc

def test_available_models():
    """Test the /api/available-models endpoint."""
    print("\n===== Testing GET /api/available-models =====")
    
    try:
        response = requests.get("http://localhost:8085/api/available-models")
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Available models: {data.get('available_models', [])}")
            return data.get('available_models', [])
        else:
            print(f"Error response: {response.text}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_analyze(available_models):
    """Test the /api/analyze endpoint."""
    print("\n===== Testing POST /api/analyze =====")
    
    # Choose a model from available models or use a default
    if available_models:
        test_model = available_models[0]
    else:
        test_model = "gpt4o"  # Default model for testing
    
    # Prepare request payload
    payload = {
        "prompt": "What are the key considerations for building a successful AI product?",
        "selected_models": [test_model],
        "ultra_model": test_model,
        "pattern": "confidence",
        "options": {},
        "output_format": "markdown"
    }
    
    try:
        response = requests.post(
            "http://localhost:8085/api/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Analysis ID: {data.get('analysis_id')}")
            
            # Check for model responses
            results = data.get("results", {})
            model_responses = results.get("model_responses", {})
            ultra_response = results.get("ultra_response", "")
            
            if model_responses:
                print(f"Received responses from {len(model_responses)} models")
            else:
                print("No model responses received")
            
            if ultra_response:
                print(f"Ultra response length: {len(str(ultra_response))} characters")
                print(f"Ultra response preview: {str(ultra_response)[:100]}...")
            else:
                print("No ultra response received")
            
            # Verify we're not getting placeholder data
            if "Paris is the capital" in str(ultra_response):
                print("WARNING: Still getting placeholder data!")
            else:
                print("SUCCESS: Not getting placeholder data")
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main test function."""
    # Start the server
    server_proc = start_server()
    
    try:
        # Check if the server is running
        try:
            response = requests.get("http://localhost:8085/api/docs")
            if response.status_code == 200:
                print("Server is running. Running tests...")
            else:
                print(f"Server might not be running properly. Status code: {response.status_code}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return
        
        # Run tests
        available_models = test_available_models()
        test_analyze(available_models)
        
    finally:
        # Stop the server
        print("\nStopping server...")
        server_proc.terminate()
        server_proc.wait()
        
        # Print server logs
        print("\n===== Server Logs =====")
        output = server_proc.stdout.read().decode('utf-8')
        print(output)

if __name__ == "__main__":
    main()