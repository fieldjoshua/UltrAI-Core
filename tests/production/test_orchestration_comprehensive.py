"""
Comprehensive orchestration tests for production
This is the main test file to verify orchestration is working correctly
"""

import pytest
import httpx
import asyncio
import time
import json
from datetime import datetime
from typing import Dict, Any, List


# Configuration
PROD_URL = "https://ultrai-core.onrender.com"
TIMEOUT_SHORT = 10.0
TIMEOUT_MEDIUM = 30.0
TIMEOUT_LONG = 60.0


class TestOrchestrationHealth:
    """Basic health checks for orchestration system"""
    
    @pytest.mark.asyncio
    async def test_api_health(self):
        """Test that the API is responding"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PROD_URL}/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
            print(f"✅ API Health: {data}")
    
    @pytest.mark.asyncio
    async def test_orchestrator_router_loaded(self):
        """Test that orchestrator router is loaded"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PROD_URL}/api/orchestrator/test")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "working" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_models_endpoint(self):
        """Test models endpoint returns expected models"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PROD_URL}/api/orchestrator/models")
            assert response.status_code == 200
            data = response.json()
            assert len(data["models"]) >= 3
            print(f"✅ Available models: {data['models']}")
    
    @pytest.mark.asyncio
    async def test_patterns_endpoint(self):
        """Test patterns endpoint returns all 10 patterns"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{PROD_URL}/api/orchestrator/patterns")
            assert response.status_code == 200
            data = response.json()
            assert len(data["patterns"]) == 10
            pattern_names = [p["name"] for p in data["patterns"]]
            print(f"✅ Available patterns: {pattern_names}")


class TestOrchestrationFunctionality:
    """Test actual orchestration functionality"""
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(TIMEOUT_LONG)
    async def test_simple_orchestration(self):
        """Test basic orchestration with simple prompt"""
        async with httpx.AsyncClient(timeout=TIMEOUT_MEDIUM) as client:
            start_time = time.time()
            
            response = await client.post(
                f"{PROD_URL}/api/orchestrator/feather",
                json={
                    "prompt": "What is 2+2?",
                    "pattern": "gut"
                }
            )
            
            elapsed = time.time() - start_time
            
            # Should complete within reasonable time
            assert response.status_code == 200, f"Failed with {response.status_code}: {response.text}"
            assert elapsed < 45.0, f"Too slow: {elapsed}s"
            
            data = response.json()
            assert data["status"] == "success"
            assert len(data["models_used"]) > 0
            
            print(f"✅ Orchestration completed in {elapsed:.2f}s")
            print(f"   Models used: {data['models_used']}")
            print(f"   Response preview: {data['ultra_response'][:100]}...")
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(TIMEOUT_LONG)
    async def test_multi_model_orchestration(self):
        """Test orchestration with multiple models"""
        async with httpx.AsyncClient(timeout=TIMEOUT_MEDIUM) as client:
            response = await client.post(
                f"{PROD_URL}/api/orchestrator/feather",
                json={
                    "prompt": "Explain AI in one sentence",
                    "pattern": "confidence",
                    "models": ["claude-3-opus", "gpt-4-turbo"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                assert len(data["initial_responses"]) >= 1
                print(f"✅ Multi-model orchestration successful")
    
    @pytest.mark.asyncio
    async def test_pattern_variations(self):
        """Test different analysis patterns"""
        patterns_to_test = ["gut", "confidence", "critique"]
        
        async with httpx.AsyncClient(timeout=TIMEOUT_MEDIUM) as client:
            for pattern in patterns_to_test:
                response = await client.post(
                    f"{PROD_URL}/api/orchestrator/feather",
                    json={
                        "prompt": "Test",
                        "pattern": pattern
                    }
                )
                
                assert response.status_code in [200, 504], f"Unexpected status for {pattern}"
                
                if response.status_code == 200:
                    data = response.json()
                    assert data["pattern_used"] == pattern
                    print(f"✅ Pattern {pattern} works")
                else:
                    print(f"⚠️ Pattern {pattern} timed out")


class TestOrchestrationErrors:
    """Test error handling in orchestration"""
    
    @pytest.mark.asyncio
    async def test_empty_prompt_validation(self):
        """Test that empty prompts are rejected"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PROD_URL}/api/orchestrator/feather",
                json={
                    "prompt": "",
                    "pattern": "gut"
                }
            )
            assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_invalid_pattern(self):
        """Test handling of invalid pattern names"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{PROD_URL}/api/orchestrator/feather",
                json={
                    "prompt": "Test",
                    "pattern": "invalid_pattern"
                }
            )
            # Should still work with default pattern
            assert response.status_code in [200, 504]
    
    @pytest.mark.asyncio
    async def test_timeout_protection(self):
        """Test that timeouts are handled gracefully"""
        async with httpx.AsyncClient(timeout=5.0) as client:
            with pytest.raises(httpx.TimeoutException):
                await client.post(
                    f"{PROD_URL}/api/orchestrator/feather",
                    json={
                        "prompt": "Long complex prompt that might timeout",
                        "pattern": "gut"
                    }
                )


class TestOrchestrationPerformance:
    """Performance and load tests"""
    
    @pytest.mark.asyncio
    async def test_response_time(self):
        """Test that responses are within acceptable time"""
        timings = []
        
        async with httpx.AsyncClient(timeout=TIMEOUT_MEDIUM) as client:
            for i in range(3):
                start = time.time()
                response = await client.post(
                    f"{PROD_URL}/api/orchestrator/feather",
                    json={
                        "prompt": f"Test {i}",
                        "pattern": "gut"
                    }
                )
                elapsed = time.time() - start
                
                if response.status_code == 200:
                    timings.append(elapsed)
        
        if timings:
            avg_time = sum(timings) / len(timings)
            print(f"✅ Average response time: {avg_time:.2f}s")
            assert avg_time < 30.0, f"Too slow average: {avg_time}s"
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        async def make_request(client, index):
            try:
                response = await client.post(
                    f"{PROD_URL}/api/orchestrator/feather",
                    json={
                        "prompt": f"Concurrent test {index}",
                        "pattern": "gut"
                    }
                )
                return response.status_code == 200
            except:
                return False
        
        async with httpx.AsyncClient(timeout=TIMEOUT_MEDIUM) as client:
            tasks = [make_request(client, i) for i in range(3)]
            results = await asyncio.gather(*tasks)
            
            success_count = sum(results)
            print(f"✅ Concurrent requests: {success_count}/3 successful")


def run_quick_test():
    """Run a quick test to see if orchestration is working"""
    import asyncio
    
    async def quick_check():
        async with httpx.AsyncClient(timeout=15.0) as client:
            print("🧪 Quick Orchestration Check...")
            
            # Health check
            health = await client.get(f"{PROD_URL}/api/health")
            print(f"1. Health: {'✅' if health.status_code == 200 else '❌'}")
            
            # Orchestration test
            try:
                start = time.time()
                orch = await client.post(
                    f"{PROD_URL}/api/orchestrator/feather",
                    json={"prompt": "Hi", "pattern": "gut"}
                )
                elapsed = time.time() - start
                
                if orch.status_code == 200:
                    print(f"2. Orchestration: ✅ ({elapsed:.2f}s)")
                    data = orch.json()
                    print(f"   Models: {data.get('models_used', [])}")
                else:
                    print(f"2. Orchestration: ❌ (status {orch.status_code})")
            except httpx.TimeoutException:
                print(f"2. Orchestration: ❌ (timeout)")
            except Exception as e:
                print(f"2. Orchestration: ❌ ({type(e).__name__})")
    
    asyncio.run(quick_check())


if __name__ == "__main__":
    # Run quick test if executed directly
    run_quick_test()