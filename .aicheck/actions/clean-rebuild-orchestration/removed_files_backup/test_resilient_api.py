#!/usr/bin/env python3
"""Test script for resilient API endpoints."""

import asyncio
import json
from typing import Any, Dict

import aiohttp

API_BASE_URL = "http://localhost:8085/api"


async def test_resilient_analyze():
    """Test the resilient analyze endpoint."""
    payload = {
        "prompt": "What is the capital of France?",
        "models": ["openai-gpt4o", "anthropic-claude"],
        "lead_model": "openai-gpt4o",
        "analysis_type": "factual",
        "enable_fallback": True,
        "enable_cache": True,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{API_BASE_URL}/resilient/analyze", json=payload
        ) as response:
            result = await response.json()
            print(f"Analyze Response: {json.dumps(result, indent=2)}")
            return response.status == 200


async def test_provider_health():
    """Test the provider health endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/resilient/health") as response:
            result = await response.json()
            print(f"Health Response: {json.dumps(result, indent=2)}")
            return response.status == 200


async def test_statistics():
    """Test the statistics endpoint."""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/resilient/statistics") as response:
            result = await response.json()
            print(f"Statistics Response: {json.dumps(result, indent=2)}")
            return response.status == 200


async def test_all():
    """Run all tests."""
    print("Testing Resilient API Endpoints...")
    print("-" * 50)

    tests = [
        ("Resilient Analyze", test_resilient_analyze),
        ("Provider Health", test_provider_health),
        ("Statistics", test_statistics),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            success = await test_func()
            results.append((test_name, success))
            print(f"✓ {test_name}: {'PASSED' if success else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"✗ {test_name}: FAILED with error: {str(e)}")

    print("\n" + "=" * 50)
    print("Test Summary:")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Passed: {passed}/{total}")

    for test_name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {test_name}: {status}")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(test_all())
    exit(0 if success else 1)
