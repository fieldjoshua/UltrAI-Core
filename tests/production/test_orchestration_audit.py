#!/usr/bin/env python3
"""
Production Orchestration Test
Tests the actual deployed orchestration endpoint to verify it's working
"""

import asyncio
import json
import time
import httpx


async def test_orchestration():
    """Test the production orchestration endpoint"""
    
    base_url = "https://ultrai-core.onrender.com"
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        
        # Test 1: Health check
        print("1. Testing health endpoint...")
        try:
            response = await client.get(f"{base_url}/api/health")
            print(f"   Health: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
            
        # Test 2: Models endpoint
        print("\n2. Testing models endpoint...")
        try:
            response = await client.get(f"{base_url}/api/orchestrator/models")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Models: {data.get('models', [])}")
        except Exception as e:
            print(f"   Error: {e}")
            
        # Test 3: Patterns endpoint
        print("\n3. Testing patterns endpoint...")
        try:
            response = await client.get(f"{base_url}/api/orchestrator/patterns")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Patterns: {len(data.get('patterns', []))} available")
        except Exception as e:
            print(f"   Error: {e}")
            
        # Test 4: Simple orchestration request
        print("\n4. Testing orchestration with simple prompt...")
        try:
            start_time = time.time()
            response = await client.post(
                f"{base_url}/api/orchestrator/feather",
                json={
                    "prompt": "Say hello in 5 words",
                    "pattern": "gut"
                }
            )
            elapsed = time.time() - start_time
            print(f"   Status: {response.status_code} (took {elapsed:.2f}s)")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Models used: {data.get('models_used', [])}")
                print(f"   Processing time: {data.get('processing_time', 0):.2f}s")
                print(f"   Ultra response preview: {data.get('ultra_response', '')[:100]}...")
            else:
                print(f"   Error response: {response.text}")
                
        except httpx.TimeoutException:
            print(f"   TIMEOUT after {time.time() - start_time:.2f}s")
        except Exception as e:
            print(f"   Error: {type(e).__name__}: {e}")
            
        # Test 5: Check with timeout protection
        print("\n5. Testing timeout protection...")
        try:
            # This should timeout quickly if there's an issue
            response = await client.post(
                f"{base_url}/api/orchestrator/feather",
                json={
                    "prompt": "Test timeout",
                    "pattern": "gut"
                },
                timeout=30.0  # 30 second timeout
            )
            print(f"   Status: {response.status_code}")
            
        except httpx.TimeoutException:
            print("   Request timed out as expected if orchestration is hanging")
        except Exception as e:
            print(f"   Error: {e}")


if __name__ == "__main__":
    print("Testing UltraAI Orchestration in Production")
    print("=" * 50)
    asyncio.run(test_orchestration())
    print("\nTest complete!")