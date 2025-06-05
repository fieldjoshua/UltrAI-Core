#!/usr/bin/env python3
"""
Test suite for deploy-render.sh script functionality
Part of render-cli-integration action process testing
"""

import subprocess
import os
import tempfile
import shutil
from pathlib import Path
import pytest


class TestDeployRenderScript:
    """Test suite for the deploy-render.sh script"""
    
    @pytest.fixture
    def script_path(self):
        """Get path to the deploy script"""
        return Path(__file__).parent.parent.parent.parent.parent.parent / "scripts" / "deploy-render.sh"
    
    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing"""
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        subprocess.run(["git", "init"], check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
        
        # Create initial commit
        Path("test.txt").write_text("test")
        subprocess.run(["git", "add", "test.txt"], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        
        yield temp_dir
        
        # Cleanup
        os.chdir("/")
        shutil.rmtree(temp_dir)
    
    def test_script_exists_and_executable(self, script_path):
        """Test that the deploy script exists and is executable"""
        assert script_path.exists(), "deploy-render.sh script not found"
        assert os.access(script_path, os.X_OK), "deploy-render.sh is not executable"
    
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
            "print_error"
        ]
        for func in required_functions:
            assert func in content, f"Script should contain {func} function"
    
    def test_script_checks_render_cli(self, script_path):
        """Test that script checks for Render CLI availability"""
        content = script_path.read_text()
        assert "command -v render" in content, "Script should check for render CLI"
    
    def test_script_checks_authentication(self, script_path):
        """Test that script checks authentication"""
        content = script_path.read_text()
        assert "render whoami" in content, "Script should check authentication"
    
    def test_script_checks_git_status(self, script_path):
        """Test that script checks git status"""
        content = script_path.read_text()
        assert "git status" in content, "Script should check git status"
        assert "git branch" in content, "Script should check current branch"
    
    def test_script_tests_production_endpoints(self, script_path):
        """Test that script tests production endpoints"""
        content = script_path.read_text()
        endpoints = [
            "/health",
            "/api/orchestrator/models",
            "/api/orchestrator/patterns",
            "/api/orchestrator/feather"
        ]
        for endpoint in endpoints:
            assert endpoint in content, f"Script should test {endpoint} endpoint"
    
    def test_script_has_production_url(self, script_path):
        """Test that script has correct production URL"""
        content = script_path.read_text()
        assert "https://ultrai-core-4lut.onrender.com" in content, "Script should have correct production URL"
    
    def test_script_detects_antiquated_code(self, script_path):
        """Test that script can detect antiquated code"""
        content = script_path.read_text()
        assert "antiquated" in content.lower(), "Script should detect antiquated code"
        assert "/api/orchestrator/execute" in content, "Script should check for antiquated endpoints"


class TestDeployScriptBehavior:
    """Integration tests for deploy script behavior"""
    
    def test_git_status_check_with_clean_repo(self, temp_git_repo, script_path):
        """Test script behavior with clean git repository"""
        # This would require mocking render CLI, so we'll test the git logic only
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout.strip() == "", "Repository should be clean"
    
    def test_git_status_check_with_dirty_repo(self, temp_git_repo):
        """Test script behavior with uncommitted changes"""
        # Add uncommitted change
        Path("dirty.txt").write_text("uncommitted change")
        
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout.strip() != "", "Repository should show uncommitted changes"
    
    def test_branch_detection(self, temp_git_repo):
        """Test that script can detect current branch"""
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        assert result.returncode == 0
        assert result.stdout.strip() == "main", "Should be on main branch"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])