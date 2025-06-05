#!/usr/bin/env python3
"""
Simple standalone test for orchestration
No dependencies on app context - just tests the production endpoint
"""

import asyncio
import httpx
import time


async def test_orchestration():
    """Simple test of production orchestration"""
    
    base_url = "https://ultrai-core.onrender.com"
    
    print("🧪 Testing UltraAI Orchestration")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Basic health
        print("\n1️⃣ Health Check:")
        try:
            response = await client.get(f"{base_url}/api/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ API is healthy")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return
            
        # Test 2: Orchestration endpoint
        print("\n2️⃣ Orchestration Test:")
        print("   Sending simple prompt...")
        
        try:
            start = time.time()
            response = await client.post(
                f"{base_url}/api/orchestrator/feather",
                json={
                    "prompt": "Say 'Hello AI' in exactly 2 words",
                    "pattern": "gut"
                }
            )
            elapsed = time.time() - start
            
            print(f"   Status: {response.status_code}")
            print(f"   Time: {elapsed:.2f}s")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Orchestration successful!")
                print(f"   Models used: {data.get('models_used', [])}")
                print(f"   Response preview: {data.get('ultra_response', '')[:100]}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except httpx.TimeoutException:
            print(f"   ❌ Request timed out after {time.time() - start:.2f}s")
            print("   The orchestration is still hanging!")
        except Exception as e:
            print(f"   ❌ Error: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(test_orchestration())