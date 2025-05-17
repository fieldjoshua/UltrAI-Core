#!/usr/bin/env python3
"""Simple test to validate MVP minimal deployment has all features"""

import json
import time

import requests


def test_backend_health():
    """Test that backend health check works"""
    try:
        response = requests.get("http://localhost:8085/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data}")
            return True
        else:
            print(f"✗ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_auth_login():
    """Test that auth/login endpoint exists"""
    try:
        response = requests.post(
            "http://localhost:8085/api/auth/login",
            json={"email": "test@example.com", "password": "test"},
            timeout=5,
        )
        print(f"✓ Auth login endpoint exists (status: {response.status_code})")
        return True
    except Exception as e:
        print(f"✗ Auth login failed: {e}")
        return False


def test_available_models():
    """Test that available models endpoint exists"""
    try:
        response = requests.get("http://localhost:8085/api/available-models", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Available models: {len(data)} models found")
            return True
        else:
            print(f"✗ Available models failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Available models failed: {e}")
        return False


def test_orchestrator_patterns():
    """Test that orchestrator patterns endpoint exists"""
    try:
        response = requests.get(
            "http://localhost:8085/api/orchestrator/patterns", timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Orchestrator patterns: {len(data)} patterns found")
            return True
        else:
            print(f"✗ Orchestrator patterns failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Orchestrator patterns failed: {e}")
        return False


def main():
    print("=== MVP Minimal Deployment Simple Test ===")
    print("Testing backend: http://localhost:8085")
    print()

    tests = [
        test_backend_health,
        test_auth_login,
        test_available_models,
        test_orchestrator_patterns,
    ]

    passed = 0
    failed = 0

    for test in tests:
        print(f"\nRunning: {test.__name__}")
        print("-" * 40)
        if test():
            passed += 1
        else:
            failed += 1
        time.sleep(1)

    print("\n" + "=" * 40)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(tests))*100:.1f}%")
    print("=" * 40)

    return failed == 0


if __name__ == "__main__":
    import sys

    sys.exit(0 if main() else 1)
