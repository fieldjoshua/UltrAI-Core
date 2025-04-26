"""
Tests for the frontend interface component.
"""

import pytest
from backend.core.frontend import (
    FrontendConfig,
    FrontendComponent,
    PromptInput,
    ResultDisplay,
)


def test_frontend_config_initialization(frontend_config):
    """Test frontend configuration initialization."""
    assert frontend_config.title == "Test App"
    assert frontend_config.description == "Test application"
    assert frontend_config.version == "1.0.0"
    assert frontend_config.theme["primary"] == "#000000"


def test_frontend_component_initialization(frontend_component, frontend_config):
    """Test frontend component initialization."""
    assert frontend_component.config == frontend_config
    assert len(frontend_component.components) == 0


def test_frontend_component_register_component(frontend_component):
    """Test registering a component with the frontend."""
    test_component = {"type": "input", "props": {"label": "Test"}}
    frontend_component.register_component("test_input", test_component)
    assert len(frontend_component.components) == 1
    assert frontend_component.get_component("test_input") == test_component


def test_frontend_component_get_component(frontend_component):
    """Test getting a component from the frontend."""
    test_component = {"type": "input", "props": {"label": "Test"}}
    frontend_component.register_component("test_input", test_component)
    retrieved = frontend_component.get_component("test_input")
    assert retrieved == test_component
    assert frontend_component.get_component("nonexistent") is None


def test_frontend_component_render(frontend_component, frontend_config):
    """Test rendering the frontend interface."""
    test_component = {"type": "input", "props": {"label": "Test"}}
    frontend_component.register_component("test_input", test_component)

    rendered = frontend_component.render()
    assert rendered["title"] == frontend_config.title
    assert rendered["description"] == frontend_config.description
    assert rendered["version"] == frontend_config.version
    assert rendered["theme"] == frontend_config.theme
    assert rendered["components"]["test_input"] == test_component


def test_prompt_input_initialization():
    """Test prompt input initialization."""
    prompt_input = PromptInput()
    assert len(prompt_input.templates) == 0


def test_prompt_input_add_template():
    """Test adding a template to prompt input."""
    prompt_input = PromptInput()
    prompt_input.add_template("test", "Test template: {input}")
    assert prompt_input.get_template("test") == "Test template: {input}"


def test_prompt_input_get_template():
    """Test getting a template from prompt input."""
    prompt_input = PromptInput()
    prompt_input.add_template("test", "Test template: {input}")
    template = prompt_input.get_template("test")
    assert template == "Test template: {input}"
    assert prompt_input.get_template("nonexistent") is None


def test_prompt_input_validate_input():
    """Test validating user input."""
    prompt_input = PromptInput()
    assert prompt_input.validate_input("valid input")
    assert not prompt_input.validate_input("")
    assert not prompt_input.validate_input("   ")


def test_result_display_initialization():
    """Test result display initialization."""
    result_display = ResultDisplay()
    assert len(result_display.formatters) == 0


def test_result_display_add_formatter():
    """Test adding a formatter to result display."""
    result_display = ResultDisplay()

    def test_formatter(result: str) -> str:
        return f"Formatted: {result}"

    result_display.add_formatter("test", test_formatter)
    assert len(result_display.formatters) == 1


def test_result_display_format_result():
    """Test formatting a result."""
    result_display = ResultDisplay()

    def test_formatter(result: str) -> str:
        return f"Formatted: {result}"

    result_display.add_formatter("test", test_formatter)
    formatted = result_display.format_result("test result", "test")
    assert formatted == "Formatted: test result"


def test_result_display_format_result_missing_formatter():
    """Test formatting a result with a missing formatter."""
    result_display = ResultDisplay()
    result = "test result"
    formatted = result_display.format_result(result, "nonexistent")
    assert formatted == result
