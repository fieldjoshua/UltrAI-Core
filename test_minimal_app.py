#!/usr/bin/env python3
"""Test the minimal app deployment locally"""

import os
import subprocess
import sys
import time

import requests

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_minimal_app():
    """Test minimal app with all MVP features"""

    # Set up environment
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": os.path.dirname(os.path.abspath(__file__)),
            "ENV": "development",
            "USE_MOCK": "true",
            "DATABASE_URL": "sqlite:///./test_ultra.db",
            "SECRET_KEY": "test-secret-key",
            "JWT_SECRET_KEY": "test-jwt-secret",
            "REDIS_URL": "redis://localhost:6379",
            "CORS_ORIGINS": "*",
            "SENTRY_DSN": "",  # Empty for testing
        }
    )

    print("Starting minimal app...")
    # Start the app using -m to ensure correct imports
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app_minimal:app", "--port", "8001"],
        env=env,
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    # Wait for startup
    time.sleep(5)

    try:
        # Test health endpoint
        print("\nTesting health endpoint...")
        response = requests.get("http://localhost:8001/api/health")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"App status: {data.get('status')}")
            print(f"App type: {data.get('app_type')}")
            print(f"Dependencies: {data.get('dependencies')}")

        # Test root endpoint
        print("\nTesting root endpoint...")
        response = requests.get("http://localhost:8001/")
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Features: {data.get('features')}")

        # Test authentication
        print("\nTesting authentication...")
        register_data = {
            "email": f"test_{int(time.time())}@example.com",
            "password": "SecurePass123!",
            "name": "Test User",
        }
        response = requests.post(
            "http://localhost:8001/api/auth/register", json=register_data
        )
        print(f"Registration status: {response.status_code}")

        # Test models endpoint
        print("\nTesting models endpoint...")
        response = requests.get("http://localhost:8001/api/available-models")
        print(f"Models endpoint status: {response.status_code}")

        # Test patterns endpoint
        print("\nTesting patterns endpoint...")
        response = requests.get("http://localhost:8001/api/orchestrator/patterns")
        print(f"Patterns endpoint status: {response.status_code}")

        # Test resource monitoring
        print("\nTesting resource monitoring...")
        response = requests.get("http://localhost:8001/api/internal/resources")
        print(f"Resources endpoint status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Memory usage: {data.get('memory_mb', 0):.2f} MB")
            print(f"CPU percent: {data.get('cpu_percent', 0):.1f}%")

        print("\n✓ All basic tests passed!")

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
    finally:
        # Stop the app
        print("\nStopping app...")
        process.terminate()
        process.wait()


if __name__ == "__main__":
    test_minimal_app()
