"""
Tests for the data management component.
"""

import pytest
from backend.core.data import StoragePattern, PersistenceStrategy, DataFlow


def test_storage_pattern_initialization(mock_storage_pattern):
    """Test storage pattern initialization."""
    assert isinstance(mock_storage_pattern, StoragePattern)


@pytest.mark.asyncio
async def test_storage_pattern_operations(mock_storage_pattern):
    """Test storage pattern operations."""
    test_data = {"key": "value"}
    await mock_storage_pattern.store(test_data)
    retrieved = await mock_storage_pattern.retrieve("test")
    assert retrieved == {"id": "test", "data": "test"}
    await mock_storage_pattern.update("test", test_data)
    await mock_storage_pattern.delete("test")


def test_persistence_strategy_initialization(mock_persistence_strategy):
    """Test persistence strategy initialization."""
    assert isinstance(mock_persistence_strategy, PersistenceStrategy)


@pytest.mark.asyncio
async def test_persistence_strategy_operations(mock_persistence_strategy):
    """Test persistence strategy operations."""
    test_data = {"key": "value"}
    identifier = await mock_persistence_strategy.save(test_data)
    assert identifier == "test_id"
    loaded = await mock_persistence_strategy.load(identifier)
    assert loaded == {"id": identifier, "data": "test"}
    await mock_persistence_strategy.remove(identifier)


def test_data_flow_initialization(data_flow):
    """Test data flow initialization."""
    assert len(data_flow.patterns) == 1
    assert len(data_flow.strategies) == 1


def test_data_flow_register_pattern(mock_storage_pattern):
    """Test registering a pattern with data flow."""
    flow = DataFlow()
    flow.register_pattern("new_pattern", mock_storage_pattern)
    assert len(flow.patterns) == 1
    assert "new_pattern" in flow.patterns


def test_data_flow_register_strategy(mock_persistence_strategy):
    """Test registering a strategy with data flow."""
    flow = DataFlow()
    flow.register_strategy("new_strategy", mock_persistence_strategy)
    assert len(flow.strategies) == 1
    assert "new_strategy" in flow.strategies


def test_data_flow_get_pattern(mock_storage_pattern):
    """Test getting a pattern from data flow."""
    flow = DataFlow()
    flow.register_pattern("test_pattern", mock_storage_pattern)
    retrieved = flow.get_pattern("test_pattern")
    assert retrieved == mock_storage_pattern
    assert flow.get_pattern("nonexistent") is None


def test_data_flow_get_strategy(mock_persistence_strategy):
    """Test getting a strategy from data flow."""
    flow = DataFlow()
    flow.register_strategy("test_strategy", mock_persistence_strategy)
    retrieved = flow.get_strategy("test_strategy")
    assert retrieved == mock_persistence_strategy
    assert flow.get_strategy("nonexistent") is None


@pytest.mark.asyncio
async def test_data_flow_store_data(mock_storage_pattern):
    """Test storing data using data flow."""
    flow = DataFlow()
    flow.register_pattern("test_pattern", mock_storage_pattern)
    test_data = {"key": "value"}
    await flow.store_data("test_pattern", test_data)


@pytest.mark.asyncio
async def test_data_flow_store_data_nonexistent_pattern():
    """Test storing data with a nonexistent pattern."""
    flow = DataFlow()
    with pytest.raises(ValueError, match="Pattern 'nonexistent' not found"):
        await flow.store_data("nonexistent", {"key": "value"})


@pytest.mark.asyncio
async def test_data_flow_retrieve_data(mock_storage_pattern):
    """Test retrieving data using data flow."""
    flow = DataFlow()
    flow.register_pattern("test_pattern", mock_storage_pattern)
    retrieved = await flow.retrieve_data("test_pattern", "test")
    assert retrieved == {"id": "test", "data": "test"}


@pytest.mark.asyncio
async def test_data_flow_retrieve_data_nonexistent_pattern():
    """Test retrieving data with a nonexistent pattern."""
    flow = DataFlow()
    with pytest.raises(ValueError, match="Pattern 'nonexistent' not found"):
        await flow.retrieve_data("nonexistent", "test")


@pytest.mark.asyncio
async def test_data_flow_persist_data(mock_persistence_strategy):
    """Test persisting data using data flow."""
    flow = DataFlow()
    flow.register_strategy("test_strategy", mock_persistence_strategy)
    test_data = {"key": "value"}
    identifier = await flow.persist_data("test_strategy", test_data)
    assert identifier == "test_id"


@pytest.mark.asyncio
async def test_data_flow_persist_data_nonexistent_strategy():
    """Test persisting data with a nonexistent strategy."""
    flow = DataFlow()
    with pytest.raises(ValueError, match="Strategy 'nonexistent' not found"):
        await flow.persist_data("nonexistent", {"key": "value"})


@pytest.mark.asyncio
async def test_data_flow_load_data(mock_persistence_strategy):
    """Test loading data using data flow."""
    flow = DataFlow()
    flow.register_strategy("test_strategy", mock_persistence_strategy)
    loaded = await flow.load_data("test_strategy", "test_id")
    assert loaded == {"id": "test_id", "data": "test"}


@pytest.mark.asyncio
async def test_data_flow_load_data_nonexistent_strategy():
    """Test loading data with a nonexistent strategy."""
    flow = DataFlow()
    with pytest.raises(ValueError, match="Strategy 'nonexistent' not found"):
        await flow.load_data("nonexistent", "test_id")
