"""
Tests for the backend integration component.
"""

import pytest
from backend.core.integration import (
    Service,
    ServiceRegistry,
    IntegrationPattern,
    CommunicationProtocol,
)


def test_service_initialization(mock_service):
    """Test service initialization."""
    assert isinstance(mock_service, Service)


@pytest.mark.asyncio
async def test_service_lifecycle(mock_service):
    """Test service lifecycle methods."""
    await mock_service.initialize()
    await mock_service.shutdown()


def test_service_registry_initialization(service_registry):
    """Test service registry initialization."""
    assert len(service_registry.services) == 1
    assert "test_service" in service_registry.services


def test_service_registry_register_service(service_registry, mock_service):
    """Test registering a service with the registry."""
    service_registry.register_service("new_service", mock_service)
    assert len(service_registry.services) == 2
    assert "new_service" in service_registry.services


def test_service_registry_get_service(service_registry, mock_service):
    """Test getting a service from the registry."""
    retrieved = service_registry.get_service("test_service")
    assert retrieved == mock_service
    assert service_registry.get_service("nonexistent") is None


@pytest.mark.asyncio
async def test_service_registry_initialize_all(service_registry):
    """Test initializing all services in the registry."""
    await service_registry.initialize_all()


@pytest.mark.asyncio
async def test_service_registry_shutdown_all(service_registry):
    """Test shutting down all services in the registry."""
    await service_registry.shutdown_all()


def test_integration_pattern_initialization(mock_storage_pattern):
    """Test integration pattern initialization."""
    assert isinstance(mock_storage_pattern, IntegrationPattern)


@pytest.mark.asyncio
async def test_integration_pattern_lifecycle(mock_storage_pattern):
    """Test integration pattern lifecycle methods."""
    await mock_storage_pattern.connect()
    await mock_storage_pattern.disconnect()


@pytest.mark.asyncio
async def test_integration_pattern_data_flow(mock_storage_pattern):
    """Test integration pattern data flow methods."""
    test_data = {"key": "value"}
    await mock_storage_pattern.send(test_data)
    received = await mock_storage_pattern.receive()
    assert received == {"id": "test", "data": "test"}


def test_communication_protocol_initialization():
    """Test communication protocol initialization."""
    protocol = CommunicationProtocol()
    assert len(protocol.patterns) == 0


def test_communication_protocol_register_pattern(mock_storage_pattern):
    """Test registering a pattern with the protocol."""
    protocol = CommunicationProtocol()
    protocol.register_pattern("test_pattern", mock_storage_pattern)
    assert len(protocol.patterns) == 1
    assert "test_pattern" in protocol.patterns


def test_communication_protocol_get_pattern(mock_storage_pattern):
    """Test getting a pattern from the protocol."""
    protocol = CommunicationProtocol()
    protocol.register_pattern("test_pattern", mock_storage_pattern)
    retrieved = protocol.get_pattern("test_pattern")
    assert retrieved == mock_storage_pattern
    assert protocol.get_pattern("nonexistent") is None


@pytest.mark.asyncio
async def test_communication_protocol_establish_connection(mock_storage_pattern):
    """Test establishing a connection using the protocol."""
    protocol = CommunicationProtocol()
    protocol.register_pattern("test_pattern", mock_storage_pattern)
    await protocol.establish_connection("test_pattern")


@pytest.mark.asyncio
async def test_communication_protocol_establish_nonexistent_connection():
    """Test establishing a connection with a nonexistent pattern."""
    protocol = CommunicationProtocol()
    with pytest.raises(ValueError, match="Pattern 'nonexistent' not found"):
        await protocol.establish_connection("nonexistent")


@pytest.mark.asyncio
async def test_communication_protocol_close_connection(mock_storage_pattern):
    """Test closing a connection using the protocol."""
    protocol = CommunicationProtocol()
    protocol.register_pattern("test_pattern", mock_storage_pattern)
    await protocol.close_connection("test_pattern")


@pytest.mark.asyncio
async def test_communication_protocol_close_nonexistent_connection():
    """Test closing a connection with a nonexistent pattern."""
    protocol = CommunicationProtocol()
    with pytest.raises(ValueError, match="Pattern 'nonexistent' not found"):
        await protocol.close_connection("nonexistent")
