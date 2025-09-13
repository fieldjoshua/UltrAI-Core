"""
Example test file demonstrating the test configuration system.

This file shows how to write tests that adapt to different test modes.
"""

import pytest
from httpx import AsyncClient
from tests.test_config import test_config, TestMode, skip_if_offline, skip_if_not_mode
from tests.mock_config import MockLLMResponses, create_mock_llm_adapter


class TestConfigurationExample:
    """Example tests showing configuration usage"""
    
    def test_mode_detection(self):
        """Test that mode is correctly detected"""
        assert test_config.mode in TestMode
        print(f"Running in {test_config.mode.value} mode")
    
    def test_endpoint_configuration(self):
        """Test that endpoints are configured correctly"""
        # Test mode-specific configuration
        
        if test_config.mode == TestMode.PRODUCTION:
            assert test_config.config.base_url.startswith("https://")
            assert "onrender.com" in test_config.config.base_url
        else:
            assert test_config.config.base_url.startswith("http://")
    
    @pytest.mark.asyncio
    async def test_mock_behavior(self, mock_llm_adapters):
        """Test that mocks are applied based on configuration"""
        if test_config.config.mock_llms:
            assert mock_llm_adapters is not None
            # In mock mode, adapters should be mocked
        else:
            assert mock_llm_adapters is None
            # In live mode, no mocks provided
    
    @skip_if_offline()
    @pytest.mark.asyncio
    async def test_requiring_external_services(self):
        """Test that requires external services (skipped in OFFLINE mode)"""
        # This test will only run in MOCK, INTEGRATION, LIVE, or PRODUCTION modes
        assert test_config.mode != TestMode.OFFLINE
    
    @skip_if_not_mode(TestMode.INTEGRATION)
    @pytest.mark.asyncio
    async def test_integration_only(self):
        """Test that only runs in INTEGRATION mode"""
        # This test will only run when TEST_MODE=INTEGRATION
        assert test_config.mode == TestMode.INTEGRATION
        assert test_config.config.use_real_db
        assert test_config.config.use_real_redis
    
    @pytest.mark.live
    @pytest.mark.asyncio
    async def test_live_api_call(self):
        """Test that makes real API calls (only in LIVE mode)"""
        if test_config.mode != TestMode.LIVE:
            pytest.skip("Test requires LIVE mode")
        
        # This would make a real API call
        # Only runs when TEST_MODE=LIVE
        assert test_config.config.require_api_keys
    
    @pytest.mark.production
    @pytest.mark.asyncio
    async def test_production_endpoint(self):
        """Test against production endpoints (only in PRODUCTION mode)"""
        if test_config.mode != TestMode.PRODUCTION:
            pytest.skip("Test requires PRODUCTION mode")
        
        # Test against real production endpoint
        async with AsyncClient() as client:
            response = await client.get(f"{test_config.config.base_url}/")
            assert response.status_code == 200


class TestMockConfiguration:
    """Tests demonstrating mock configuration"""
    
    def test_mock_responses_available(self):
        """Test that mock responses are configured"""
        response = MockLLMResponses.SIMPLE_RESPONSE
        assert "generated_text" in response
        assert response["provider"] == "mock"
    
    @pytest.mark.asyncio
    async def test_mock_adapter_creation(self):
        """Test creating mock adapters"""
        adapter = create_mock_llm_adapter("test-provider", "test-model")
        result = await adapter.generate("Test prompt")
        
        assert result["provider"] == "test-provider"
        assert result["model"] == "test-model"
        assert "Mock test-provider response" in result["generated_text"]
    
    def test_timeout_configuration(self):
        """Test that timeouts are configured based on mode"""
        api_timeout = test_config.config.api_timeout
        
        if test_config.mode == TestMode.LIVE:
            # Live mode should have longer timeouts
            assert api_timeout >= 60
        elif test_config.mode == TestMode.PRODUCTION:
            # Production mode should have even longer timeouts
            assert api_timeout >= 60
        else:
            # Other modes have standard timeouts
            assert api_timeout <= 30


# Conditional test based on environment
if test_config.mode == TestMode.OFFLINE:
    def test_offline_specific():
        """Test that only exists in OFFLINE mode"""
        assert test_config.mode == TestMode.OFFLINE
        assert test_config.config.use_mocks
        assert test_config.config.mock_llms