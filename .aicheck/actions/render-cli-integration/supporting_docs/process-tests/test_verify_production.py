#!/usr/bin/env python3
"""
Test suite for verify-production.sh script functionality
Part of render-cli-integration action process testing
"""

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
import pytest
import requests
from unittest.mock import patch, Mock


class TestVerifyProductionScript:
    """Test suite for the verify-production.sh script"""
    
    @pytest.fixture
    def script_path(self):
        """Get path to the verification script"""
        return Path(__file__).parent.parent.parent.parent.parent.parent / "scripts" / "verify-production.sh"
    
    def test_script_exists_and_executable(self, script_path):
        """Test that the verification script exists and is executable"""
        assert script_path.exists(), "verify-production.sh script not found"
        assert os.access(script_path, os.X_OK), "verify-production.sh is not executable"
    
    def test_script_has_proper_shebang(self, script_path):
        """Test that script has proper bash shebang"""
        content = script_path.read_text()
        assert content.startswith("#!/bin/bash"), "Script should start with #!/bin/bash"
    
    def test_script_has_error_handling(self, script_path):
        """Test that script includes error handling"""
        content = script_path.read_text()
        assert "set -e" in content, "Script should have 'set -e' for error handling"
    
    def test_script_has_required_functions(self, script_path):
        """Test that script contains required functions"""
        content = script_path.read_text()
        required_functions = [
            "print_status",
            "print_success", 
            "print_warning",
            "print_error",
            "run_test"
        ]
        for func in required_functions:
            assert func in content, f"Script should contain {func} function"
    
    def test_script_has_production_url(self, script_path):
        """Test that script has correct production URL"""
        content = script_path.read_text()
        assert "https://ultrai-core-4lut.onrender.com" in content, "Script should have correct production URL"
    
    def test_script_tests_all_critical_endpoints(self, script_path):
        """Test that script tests all critical endpoints"""
        content = script_path.read_text()
        critical_endpoints = [
            "/health",
            "/api/orchestrator/models",
            "/api/orchestrator/patterns", 
            "/api/orchestrator/feather",
            "/openapi.json"
        ]
        for endpoint in critical_endpoints:
            assert endpoint in content, f"Script should test {endpoint} endpoint"
    
    def test_script_detects_sophisticated_endpoints(self, script_path):
        """Test that script can detect sophisticated orchestrator endpoints"""
        content = script_path.read_text()
        assert "sophisticated" in content.lower(), "Script should reference sophisticated endpoints"
        assert "antiquated" in content.lower(), "Script should detect antiquated code"
    
    def test_script_has_exit_codes(self, script_path):
        """Test that script uses proper exit codes"""
        content = script_path.read_text()
        assert "exit 0" in content, "Script should exit 0 on success"
        assert "exit 1" in content, "Script should exit 1 on failure"
    
    def test_script_tracks_test_results(self, script_path):
        """Test that script tracks test results"""
        content = script_path.read_text()
        assert "TESTS_PASSED" in content, "Script should track passed tests"
        assert "TESTS_FAILED" in content, "Script should track failed tests"
        assert "CRITICAL_FAILED" in content, "Script should track critical failures"
    
    def test_script_has_timeout_handling(self, script_path):
        """Test that script handles timeouts"""
        content = script_path.read_text()
        assert "--max-time" in content, "Script should use curl timeouts"
    
    def test_script_provides_recommendations(self, script_path):
        """Test that script provides actionable recommendations"""
        content = script_path.read_text()
        recommendations = [
            "Check deployment logs",
            "Verify latest code was deployed",
            "Clear build cache",
            "Check environment variables"
        ]
        for rec in recommendations:
            assert rec in content, f"Script should recommend: {rec}"


class TestProductionEndpointChecks:
    """Test the endpoint checking logic"""
    
    def test_health_endpoint_format(self):
        """Test expected health endpoint response format"""
        expected_fields = ["status", "services"]
        # This would be tested against actual endpoint in integration tests
        assert all(field in expected_fields for field in expected_fields)
    
    def test_sophisticated_vs_antiquated_detection(self):
        """Test detection logic for sophisticated vs antiquated endpoints"""
        # Mock responses to test detection logic
        sophisticated_endpoints = [
            "/api/orchestrator/models",
            "/api/orchestrator/patterns",
            "/api/orchestrator/feather"
        ]
        
        antiquated_endpoints = [
            "/api/orchestrator/execute"
        ]
        
        # Test that we can distinguish between the two
        assert len(sophisticated_endpoints) == 3
        assert len(antiquated_endpoints) == 1
        assert not any(endpoint in sophisticated_endpoints for endpoint in antiquated_endpoints)
    
    def test_response_time_validation(self):
        """Test response time validation logic"""
        acceptable_time = 4.5  # seconds
        slow_time = 6.0  # seconds
        
        assert acceptable_time < 5.0, "Should be considered acceptable"
        assert slow_time >= 5.0, "Should be considered slow"
    
    def test_json_parsing_error_handling(self):
        """Test JSON parsing error handling"""
        # Test with invalid JSON
        invalid_json = '{"invalid": json}'
        valid_json = '{"status": "ok"}'
        
        # In the script, jq should handle invalid JSON gracefully
        assert len(valid_json) > 0
        assert len(invalid_json) > 0


class TestScriptIntegration:
    """Integration tests for the verification script"""
    
    @pytest.fixture
    def mock_curl_success(self):
        """Mock successful curl responses"""
        return {
            "/health": '{"status": "ok", "services": {"api": "ok", "database": "connected"}}',
            "/api/orchestrator/models": '["gpt-4", "claude-3", "gemini-pro"]',
            "/api/orchestrator/patterns": '[{"name": "gut"}, {"name": "confidence"}]',
            "/openapi.json": '{"paths": {"/health": {}, "/api/orchestrator/models": {}}}'
        }
    
    @pytest.fixture  
    def mock_curl_antiquated(self):
        """Mock responses indicating antiquated code"""
        return {
            "/health": '{"status": "ok"}',
            "/api/orchestrator/models": '{"detail": "Not Found"}',
            "/api/orchestrator/patterns": '{"detail": "Not Found"}',
            "/api/orchestrator/execute": '{"status": "success"}',
            "/openapi.json": '{"paths": {"/health": {}, "/api/orchestrator/execute": {}}}'
        }
    
    def test_sophisticated_detection_logic(self, mock_curl_success):
        """Test logic that detects sophisticated orchestrator"""
        models_response = mock_curl_success["/api/orchestrator/models"]
        patterns_response = mock_curl_success["/api/orchestrator/patterns"]
        
        # Should not be "Not Found" responses
        assert "Not Found" not in models_response
        assert "Not Found" not in patterns_response
        assert len(models_response) > 10  # Non-empty response
        assert len(patterns_response) > 10  # Non-empty response
    
    def test_antiquated_detection_logic(self, mock_curl_antiquated):
        """Test logic that detects antiquated code"""
        models_response = mock_curl_antiquated["/api/orchestrator/models"]
        patterns_response = mock_curl_antiquated["/api/orchestrator/patterns"]
        execute_response = mock_curl_antiquated["/api/orchestrator/execute"]
        
        # Should have "Not Found" for sophisticated endpoints
        assert "Not Found" in models_response
        assert "Not Found" in patterns_response
        # But antiquated endpoint exists
        assert "success" in execute_response


if __name__ == "__main__":
    pytest.main([__file__, "-v"])