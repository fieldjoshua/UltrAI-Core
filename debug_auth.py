#!/usr/bin/env python3
"""Debug auth endpoints"""

import requests

# Test register endpoint
print("Testing /api/auth/register")
try:
    response = requests.post(
        "http://localhost:8085/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test123!@#",
            "name": "Test User"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    
print("\nChecking server health")
try:
    response = requests.get("http://localhost:8085/api/v1/health")
    print(f"Health status: {response.status_code}")
    print(f"Health response: {response.text}")
except Exception as e:
    print(f"Error: {e}")