"""Test the app_with_auth.py locally to verify it works"""
import subprocess
import time
import requests
import sys

def test_local_app():
    # Start the app locally
    print("Starting app locally...")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app_with_auth:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Give it time to start
    time.sleep(3)
    
    try:
        # Test root endpoint
        print("\nTesting root endpoint...")
        response = requests.get("http://localhost:8000/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test health endpoint
        print("\nTesting health endpoint...")
        response = requests.get("http://localhost:8000/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test database health
        print("\nTesting database health...")
        response = requests.get("http://localhost:8000/health/database")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Stop the process
        process.terminate()
        print("\nApp stopped")

if __name__ == "__main__":
    test_local_app()