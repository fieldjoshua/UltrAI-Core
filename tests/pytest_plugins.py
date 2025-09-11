"""
Pytest plugins for Ultra test configuration.

This module is automatically loaded by pytest and configures
test collection and execution based on TEST_MODE.
"""

import os
import pytest
from tests.test_config import TestConfig, TestMode


def pytest_configure(config):
    """Configure pytest based on test mode"""
    # Register custom markers
    config.addinivalue_line("markers", "offline: tests that run without external dependencies")
    config.addinivalue_line("markers", "mock: tests that use sophisticated mocks")
    config.addinivalue_line("markers", "integration: tests that require local services")
    config.addinivalue_line("markers", "live: tests that use real LLM providers")
    config.addinivalue_line("markers", "production: tests that run against production")
    
    # Log current test mode
    from _pytest.terminal import TerminalReporter
    terminal = config.pluginmanager.get_plugin("terminalreporter")
    if terminal and isinstance(terminal, TerminalReporter):
        terminal.write_line(f"\n🔧 Test Mode: {TestConfig.mode.value}", bold=True, yellow=True)
        terminal.write_line(f"📍 API Endpoint: {TestConfig.endpoints.api_base_url}", bold=True)
        if TestConfig.should_mock["llm_responses"]:
            terminal.write_line("🎭 LLM Mocking: ENABLED", bold=True, green=True)
        else:
            terminal.write_line("🌐 LLM Mocking: DISABLED (using real providers)", bold=True, red=True)


def pytest_collection_modifyitems(session, config, items):
    """Modify test collection based on test mode"""
    skip_reasons = TestConfig.skip_reasons
    
    for item in items:
        # Skip tests based on markers and current mode
        for marker_name, skip_reason in skip_reasons.items():
            if marker_name in item.keywords:
                item.add_marker(pytest.mark.skip(reason=skip_reason))
        
        # Add mode-specific markers
        if TestConfig.mode == TestMode.OFFLINE:
            if "unit" in item.keywords or not any(m in item.keywords for m in ["integration", "live", "production", "e2e"]):
                item.add_marker(pytest.mark.offline)
        
        # Adjust timeouts based on test type and mode
        if "slow" in item.keywords:
            timeout = TestConfig.get_timeout("orchestration")
        elif "live" in item.keywords or "live_online" in item.keywords:
            timeout = TestConfig.get_timeout("llm_request")
        else:
            timeout = TestConfig.get_timeout("default")
        
        # Apply timeout if not already set
        if "timeout" not in item.keywords:
            item.add_marker(pytest.mark.timeout(timeout))


def pytest_runtest_setup(item):
    """Setup for each test based on configuration"""
    # Log test execution in verbose mode
    if item.config.getoption("verbose") >= 2:
        print(f"\n[{TestConfig.mode.value}] Running: {item.nodeid}")


def pytest_runtest_teardown(item):
    """Teardown after each test"""
    # Clean up any test-specific resources
    pass


@pytest.fixture(autouse=True)
def test_mode_info(request):
    """Automatically inject test mode info into all tests"""
    # Make test mode information available to all tests
    request.cls.test_mode = TestConfig.mode if hasattr(request, "cls") else None
    request.module.TEST_MODE = TestConfig.mode
    yield
    # Cleanup if needed


@pytest.fixture
def test_endpoints():
    """Provide test endpoints based on configuration"""
    return TestConfig.endpoints


@pytest.fixture
def test_timeouts():
    """Provide timeout configuration"""
    return TestConfig.timeouts