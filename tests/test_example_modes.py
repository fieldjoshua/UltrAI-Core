"""
Example test file demonstrating the test mode configuration system.
"""

import pytest
from tests.test_config import test_config, TestMode, requires_mode, skip_in_modes


class TestModeExamples:
    """Examples of how test modes work."""
    
    def test_always_runs(self):
        """This test runs in all modes."""
        assert test_config.mode in TestMode
        print(f"Running in {test_config.mode.value} mode")
    
    @pytest.mark.live_online
    def test_live_only(self):
        """This test only runs in LIVE mode."""
        assert test_config.mode == TestMode.LIVE
        print("This test uses real LLM APIs")
    
    @pytest.mark.integration
    def test_integration_only(self):
        """This test needs local services."""
        assert test_config.mode == TestMode.INTEGRATION
        print("This test uses local Redis/Database")
    
    @requires_mode(TestMode.LIVE, TestMode.PRODUCTION)
    def test_live_or_production(self):
        """This test runs in LIVE or PRODUCTION modes."""
        assert test_config.mode in [TestMode.LIVE, TestMode.PRODUCTION]
        print(f"Running with real APIs in {test_config.mode.value} mode")
    
    @skip_in_modes(TestMode.OFFLINE)
    def test_needs_some_services(self):
        """This test is skipped in OFFLINE mode."""
        assert test_config.mode != TestMode.OFFLINE
        print("This test needs at least mock services")
    
    def test_check_configuration(self):
        """Check current test configuration."""
        config = test_config.config
        print(f"\nCurrent test configuration:")
        print(f"  Mode: {config.mode.value}")
        print(f"  Use mocks: {config.use_mocks}")
        print(f"  Mock LLMs: {config.mock_llms}")
        print(f"  Use real Redis: {config.use_real_redis}")
        print(f"  Use real DB: {config.use_real_db}")
        print(f"  Base URL: {config.base_url}")
        print(f"  Timeout: {config.api_timeout}s")
        
    def test_environment_variables(self):
        """Check that environment variables are set correctly."""
        import os
        
        # These should always be set in test mode
        assert os.getenv("TESTING") == "true"
        assert os.getenv("JWT_SECRET_KEY") is not None
        
        # Check mode-specific variables
        config = test_config.config
        if config.mode == TestMode.OFFLINE:
            assert os.getenv("USE_MOCK") == "true"
            assert os.getenv("ENABLE_AUTH") == "false"
        elif config.mode == TestMode.LIVE:
            assert os.getenv("USE_MOCK") == "false"
            assert os.getenv("ENABLE_AUTH") == "true"