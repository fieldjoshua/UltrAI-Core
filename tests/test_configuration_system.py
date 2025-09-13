"""
Test the test configuration system itself.
This ensures our test infrastructure is working correctly.
"""

import os
import pytest
from tests.test_config import test_config, TestMode
from tests.mock_config import MockLLMResponses, create_mock_llm_adapter


class TestConfigurationSystem:
    """Verify the test configuration system works correctly"""
    
    def test_configuration_loads(self):
        """Test that configuration loads without errors"""
        assert test_config is not None
        assert test_config.mode in TestMode
        print(f"✓ Test mode: {test_config.mode.value}")
    
    def test_endpoints_configured(self):
        """Test that endpoints are properly configured"""
        config = test_config.config
        assert config.base_url is not None
        
        if test_config.mode in [TestMode.INTEGRATION, TestMode.LIVE]:
            assert config.use_real_db
            assert config.use_real_redis
        
        print(f"✓ API URL: {config.base_url}")
    
    def test_mock_configuration(self):
        """Test that mock settings are correct for mode"""
        config = test_config.config
        
        if test_config.mode == TestMode.OFFLINE:
            assert config.use_mocks, "Mocks should be enabled in OFFLINE mode"
            assert config.mock_llms, "LLM mocks should be enabled in OFFLINE mode"
        elif test_config.mode == TestMode.LIVE:
            assert not config.mock_llms, "LLMs should not be mocked in LIVE mode"
        
        print(f"✓ Mock LLMs: {config.mock_llms}, Use mocks: {config.use_mocks}")
    
    def test_timeout_configuration(self):
        """Test timeout values are set appropriately"""
        timeout = test_config.config.api_timeout
        
        assert timeout > 0
        assert isinstance(timeout, (int, float))
        
        print(f"✓ API Timeout: {timeout}s")
    
    @pytest.mark.asyncio
    async def test_mock_llm_adapter(self):
        """Test that mock LLM adapter works"""
        if test_config.config.mock_llms:
            adapter = create_mock_llm_adapter("test", "test-model")
            result = await adapter.generate("Test prompt")
            
            assert "generated_text" in result
            assert result["provider"] == "test"
            print(f"✓ Mock adapter working: {result['generated_text'][:50]}...")
        else:
            pytest.skip("Not in mocking mode")
    
    def test_skip_reasons(self):
        """Test that skip reasons are configured correctly"""
        skip_markers = test_config.config.skip_markers
        
        if test_config.mode == TestMode.OFFLINE:
            assert "live" in skip_markers
            assert "integration" in skip_markers
        
        print(f"✓ Skip markers: {skip_markers}")
    
    def test_environment_variables(self):
        """Test that required environment variables are set"""
        # JWT_SECRET_KEY should always be set
        assert os.getenv("JWT_SECRET_KEY") is not None, "JWT_SECRET_KEY must be set"
        
        # Check mode-specific requirements
        if test_config.mode == TestMode.LIVE:
            api_keys = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]
            available_keys = [k for k in api_keys if os.getenv(k)]
            print(f"✓ API keys available: {len(available_keys)}/{len(api_keys)}")
        
        print("✓ Environment variables configured")


def test_pytest_working():
    """Basic test to ensure pytest is working"""
    assert True
    print("✓ Pytest is working")