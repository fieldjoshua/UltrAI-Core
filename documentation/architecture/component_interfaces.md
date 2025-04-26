# UltraAI Core Component Interfaces

## Overview

This document defines the interfaces for UltraAI's core components:

1. System Orchestrator
2. Configuration Manager
3. Event Bus
4. State Manager

## Common Types

```python
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass

class SystemState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    SHUTTING_DOWN = "shutting_down"
    ERROR = "error"
    STOPPED = "stopped"

class EventPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class StateType(Enum):
    MEMORY = "memory"
    PERSISTENT = "persistent"
    CACHED = "cached"

class ConfigSource(Enum):
    FILE = "file"
    ENVIRONMENT = "environment"
    MEMORY = "memory"
    DEFAULT = "default"

@dataclass
class ComponentStatus:
    name: str
    state: SystemState
    health: float  # 0.0 to 1.0
    last_updated: float
    error_count: int
    warning_count: int

@dataclass
class Event:
    name: str
    data: Any
    timestamp: float
    priority: EventPriority = EventPriority.NORMAL
    source: str = "system"
    correlation_id: Optional[str] = None

@dataclass
class StateValue:
    value: Any
    type: StateType
    last_updated: float
    version: int = 1
    is_encrypted: bool = False

@dataclass
class ConfigValue:
    value: Any
    source: ConfigSource
    last_updated: float
    is_encrypted: bool = False
```

## System Orchestrator Interface

```python
class ISystemOrchestrator:
    """Interface for the System Orchestrator component."""

    async def initialize(self) -> None:
        """Initialize the system orchestrator."""
        pass

    async def register_component(self, name: str, component: Any) -> None:
        """Register a new component."""
        pass

    async def unregister_component(self, name: str) -> None:
        """Unregister a component."""
        pass

    async def get_component(self, name: str) -> Optional[Any]:
        """Get a component by name."""
        pass

    async def get_component_status(self, name: str) -> Optional[ComponentStatus]:
        """Get component status."""
        pass

    async def get_system_state(self) -> SystemState:
        """Get current system state."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the system orchestrator."""
        pass

    async def get_health(self) -> float:
        """Get system health score."""
        pass
```

## Configuration Manager Interface

```python
class IConfigurationManager:
    """Interface for the Configuration Manager component."""

    async def initialize(self) -> None:
        """Initialize the configuration manager."""
        pass

    async def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        pass

    async def set(self, key: str, value: Any, source: ConfigSource = ConfigSource.MEMORY) -> None:
        """Set configuration value."""
        pass

    async def delete(self, key: str) -> None:
        """Delete configuration value."""
        pass

    async def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        pass

    async def get_source(self, key: str) -> Optional[ConfigSource]:
        """Get configuration value source."""
        pass

    async def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration values."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the configuration manager."""
        pass

    async def get_health(self) -> float:
        """Get configuration manager health score."""
        pass
```

## Event Bus Interface

```python
class IEventBus:
    """Interface for the Event Bus component."""

    async def initialize(self) -> None:
        """Initialize the event bus."""
        pass

    async def publish(self, event: Event) -> None:
        """Publish an event."""
        pass

    async def subscribe(
        self,
        event_name: str,
        handler: Callable,
        priority: EventPriority = EventPriority.NORMAL,
    ) -> None:
        """Subscribe to an event."""
        pass

    async def unsubscribe(self, event_name: str, handler: Callable) -> None:
        """Unsubscribe from an event."""
        pass

    async def get_event_history(
        self, event_name: Optional[str] = None, limit: int = 100
    ) -> List[Event]:
        """Get event history."""
        pass

    async def clear_event_history(self) -> None:
        """Clear event history."""
        pass

    async def get_subscriber_count(self, event_name: str) -> int:
        """Get number of subscribers for an event."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the event bus."""
        pass

    async def get_health(self) -> float:
        """Get event bus health score."""
        pass
```

## State Manager Interface

```python
class IStateManager:
    """Interface for the State Manager component."""

    async def initialize(self) -> None:
        """Initialize the state manager."""
        pass

    async def get(self, key: str, default: Any = None) -> Any:
        """Get state value."""
        pass

    async def set(self, key: str, value: Any, state_type: StateType = StateType.MEMORY) -> None:
        """Set state value."""
        pass

    async def delete(self, key: str) -> None:
        """Delete state value."""
        pass

    async def observe(self, key: str, callback: Callable) -> None:
        """Observe state changes."""
        pass

    async def unobserve(self, key: str, callback: Callable) -> None:
        """Stop observing state changes."""
        pass

    async def get_all(self) -> Dict[str, Any]:
        """Get all state values."""
        pass

    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state value metadata."""
        pass

    async def clear(self) -> None:
        """Clear all state values."""
        pass

    async def shutdown(self) -> None:
        """Shutdown the state manager."""
        pass

    async def get_health(self) -> float:
        """Get state manager health score."""
        pass
```

## Interface Implementation Requirements

### Common Requirements

1. **Asynchronous Operations**
   - All interface methods are asynchronous
   - Use Python's `asyncio` for async/await support
   - Handle concurrent operations safely

2. **Error Handling**
   - Use appropriate exception types
   - Provide detailed error messages
   - Log errors with proper context
   - Handle cleanup in error cases

3. **Type Safety**
   - Use Python type hints
   - Validate input types
   - Handle type conversions safely

4. **Logging**
   - Log important operations
   - Include relevant context
   - Use appropriate log levels
   - Follow consistent format

5. **Health Checks**
   - Implement health check method
   - Return score between 0.0 and 1.0
   - Consider component-specific metrics

### Component-Specific Requirements

1. **System Orchestrator**
   - Handle component lifecycle
   - Maintain component registry
   - Monitor component health
   - Coordinate system operations

2. **Configuration Manager**
   - Support multiple config sources
   - Validate configuration values
   - Handle config persistence
   - Notify on config changes

3. **Event Bus**
   - Support event prioritization
   - Maintain event history
   - Handle event routing
   - Support subscription management

4. **State Manager**
   - Support different state types
   - Handle state persistence
   - Manage state observers
   - Implement caching

## Interface Usage Examples

### System Orchestrator

```python
# Initialize system
orchestrator = SystemOrchestrator()
await orchestrator.initialize()

# Register component
await orchestrator.register_component("my_component", component)

# Get component status
status = await orchestrator.get_component_status("my_component")
```

### Configuration Manager

```python
# Get configuration
value = await config_manager.get("api_key")

# Set configuration
await config_manager.set("timeout", 30, ConfigSource.FILE)

# Validate configuration
is_valid = await config_manager.validate_config({"timeout": 30})
```

### Event Bus

```python
# Subscribe to event
async def handle_event(event: Event):
    print(f"Handling event: {event.name}")

await event_bus.subscribe("user_login", handle_event)

# Publish event
event = Event(name="user_login", data={"user_id": 123})
await event_bus.publish(event)
```

### State Manager

```python
# Set state
await state_manager.set("user_session", {"id": 123}, StateType.CACHED)

# Observe state changes
async def state_changed(key: str, value: Any):
    print(f"State changed: {key} = {value}")

await state_manager.observe("user_session", state_changed)
```

## Success Criteria

The interface implementation is successful when:

1. All components implement their interfaces fully
2. Type safety is maintained
3. Error handling is comprehensive
4. Async operations work correctly
5. Health checks are meaningful
6. Components can interact effectively

## Next Steps

1. Implement interface tests
2. Add interface validation
3. Create interface documentation
4. Review interface design
5. Begin component implementation
