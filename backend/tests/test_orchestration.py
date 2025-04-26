"""
Tests for the orchestration engine component.
"""

import pytest
from backend.core.orchestration import Pattern, OrchestrationEngine


def test_pattern_initialization(pattern):
    """Test pattern initialization."""
    assert pattern.name == "test_pattern"
    assert pattern.description == "Test pattern description"
    assert len(pattern.steps) == 1


def test_pattern_add_step(pattern):
    """Test adding a step to a pattern."""
    new_step = {"template": "new_template", "type": "analysis"}
    pattern.add_step(new_step)
    assert len(pattern.steps) == 2
    assert pattern.steps[1] == new_step


def test_orchestration_engine_initialization(orchestration_engine):
    """Test orchestration engine initialization."""
    assert orchestration_engine.llm_provider is not None
    assert orchestration_engine.prompt_manager is not None
    assert orchestration_engine.response_processor is not None
    assert len(orchestration_engine.patterns) == 0


def test_orchestration_engine_register_pattern(orchestration_engine, pattern):
    """Test registering a pattern with the orchestration engine."""
    orchestration_engine.register_pattern(pattern)
    assert len(orchestration_engine.patterns) == 1
    assert orchestration_engine.get_pattern("test_pattern") == pattern


def test_orchestration_engine_get_pattern(orchestration_engine, pattern):
    """Test getting a pattern from the orchestration engine."""
    orchestration_engine.register_pattern(pattern)
    retrieved = orchestration_engine.get_pattern("test_pattern")
    assert retrieved == pattern
    assert orchestration_engine.get_pattern("nonexistent") is None


def test_orchestration_engine_set_components(
    orchestration_engine, mock_llm_provider, prompt_manager, response_processor
):
    """Test setting components in the orchestration engine."""
    orchestration_engine.set_llm_provider(mock_llm_provider)
    orchestration_engine.set_prompt_manager(prompt_manager)
    orchestration_engine.set_response_processor(response_processor)

    assert orchestration_engine.llm_provider == mock_llm_provider
    assert orchestration_engine.prompt_manager == prompt_manager
    assert orchestration_engine.response_processor == response_processor


@pytest.mark.asyncio
async def test_orchestration_engine_execute_pattern(orchestration_engine, pattern):
    """Test executing a pattern with the orchestration engine."""
    orchestration_engine.register_pattern(pattern)
    result = await orchestration_engine.execute_pattern(
        "test_pattern", input="test input"
    )
    assert result == "Mock response for: Test template: test input"


@pytest.mark.asyncio
async def test_orchestration_engine_execute_nonexistent_pattern(orchestration_engine):
    """Test executing a nonexistent pattern."""
    with pytest.raises(ValueError, match="Pattern 'nonexistent' not found"):
        await orchestration_engine.execute_pattern("nonexistent")


@pytest.mark.asyncio
async def test_orchestration_engine_execute_pattern_missing_components():
    """Test executing a pattern with missing components."""
    engine = OrchestrationEngine()
    pattern = Pattern("test", "test")
    engine.register_pattern(pattern)

    with pytest.raises(ValueError, match="Missing required components"):
        await engine.execute_pattern("test")
