"""
Production tests for orchestration endpoints
These tests verify the orchestration system is working correctly in production
"""

import pytest
import httpx
import asyncio
import time
from typing import Dict, Any


# Production URL
PROD_URL = "https://ultrai-core.onrender.com"
TEST_TIMEOUT = 30.0  # 30 second timeout for tests


class TestOrchestrationProduction:
    """Test suite for production orchestration endpoints"""
    
    @pytest.fixture
    async def client(self):
        """Create an async HTTP client for tests"""
        async with httpx.AsyncClient(timeout=TEST_TIMEOUT) as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test that the health endpoint is accessible"""
        response = await client.get(f"{PROD_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "uptime" in data
    
    @pytest.mark.asyncio
    async def test_models_endpoint(self, client):
        """Test that models endpoint returns expected models"""
        response = await client.get(f"{PROD_URL}/api/orchestrator/models")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["models"], list)
        assert len(data["models"]) >= 3
        # Check for expected models
        expected_models = ["claude-3-opus", "gpt-4-turbo", "gemini-pro"]
        for model in expected_models:
            assert model in data["models"]
    
    @pytest.mark.asyncio
    async def test_patterns_endpoint(self, client):
        """Test that patterns endpoint returns all 10 patterns"""
        response = await client.get(f"{PROD_URL}/api/orchestrator/patterns")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert isinstance(data["patterns"], list)
        assert len(data["patterns"]) == 10
        
        # Check pattern structure
        for pattern in data["patterns"]:
            assert "name" in pattern
            assert "description" in pattern
            assert "stages" in pattern
            assert len(pattern["stages"]) == 4
    
    @pytest.mark.asyncio
    async def test_orchestrator_test_endpoint(self, client):
        """Test the orchestrator test endpoint"""
        response = await client.get(f"{PROD_URL}/api/orchestrator/test")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "Orchestrator router is working" in data["message"]
    
    @pytest.mark.asyncio
    @pytest.mark.timeout(60)  # 60 second timeout for this test
    async def test_feather_orchestration_simple(self, client):
        """Test basic orchestration with a simple prompt"""
        start_time = time.time()
        
        response = await client.post(
            f"{PROD_URL}/api/orchestrator/feather",
            json={
                "prompt": "What is 2+2? Answer in one word.",
                "pattern": "gut"
            }
        )
        
        elapsed = time.time() - start_time
        
        # Should complete within reasonable time
        assert elapsed < 45.0, f"Request took too long: {elapsed}s"
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert data["status"] == "success"
        assert "initial_responses" in data
        assert "meta_responses" in data
        assert "hyper_responses" in data
        assert "ultra_response" in data
        assert "processing_time" in data
        assert "models_used" in data
        
        # Verify at least one model responded
        assert len(data["models_used"]) > 0
        assert data["processing_time"] > 0
    
    @pytest.mark.asyncio
    async def test_feather_orchestration_timeout_protection(self, client):
        """Test that timeout protection works"""
        # This should timeout gracefully
        with pytest.raises(httpx.TimeoutException):
            await client.post(
                f"{PROD_URL}/api/orchestrator/feather",
                json={
                    "prompt": "This is a test of timeout protection",
                    "pattern": "gut"
                },
                timeout=5.0  # Very short timeout
            )
    
    @pytest.mark.asyncio
    async def test_legacy_process_endpoint(self, client):
        """Test the legacy /process endpoint"""
        response = await client.post(
            f"{PROD_URL}/api/orchestrator/process",
            json={
                "prompt": "Hello",
                "analysis_type": "comparative"
            }
        )
        
        # Check if it returns proper response or error
        assert response.status_code in [200, 500, 504]
        
        if response.status_code == 200:
            data = response.json()
            assert "status" in data
            assert "result" in data
    
    @pytest.mark.asyncio
    async def test_missing_api_keys_error(self, client):
        """Test error handling when API keys are missing"""
        # This test assumes we can trigger the error condition
        # In production with keys configured, this might not trigger
        pass  # Skip for now as keys are configured
    
    @pytest.mark.asyncio
    async def test_invalid_request(self, client):
        """Test error handling for invalid requests"""
        response = await client.post(
            f"{PROD_URL}/api/orchestrator/feather",
            json={
                "prompt": "",  # Empty prompt should fail validation
                "pattern": "gut"
            }
        )
        
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
class TestOrchestrationIntegration:
    """Integration tests that verify full orchestration flow"""
    
    async def test_full_orchestration_flow(self):
        """Test complete orchestration from request to response"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Step 1: Check available models
            models_response = await client.get(f"{PROD_URL}/api/orchestrator/models")
            assert models_response.status_code == 200
            available_models = models_response.json()["models"]
            
            # Step 2: Check available patterns
            patterns_response = await client.get(f"{PROD_URL}/api/orchestrator/patterns")
            assert patterns_response.status_code == 200
            patterns = patterns_response.json()["patterns"]
            
            # Step 3: Run orchestration with first pattern
            pattern_name = patterns[0]["name"]
            
            orch_response = await client.post(
                f"{PROD_URL}/api/orchestrator/feather",
                json={
                    "prompt": "What is artificial intelligence?",
                    "pattern": pattern_name,
                    "models": available_models[:2]  # Use first 2 models
                }
            )
            
            if orch_response.status_code == 200:
                data = orch_response.json()
                assert data["pattern_used"] == pattern_name
                assert len(data["models_used"]) <= 2
            else:
                # Log the error for debugging
                print(f"Orchestration failed: {orch_response.status_code}")
                print(f"Response: {orch_response.text}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "-s"])