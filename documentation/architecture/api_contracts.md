# UltraAI API Contracts

## Overview

This document defines the API contracts for UltraAI's core components, including:

1. Request/response formats
2. Error handling patterns
3. API documentation
4. Versioning strategy

## API Versioning

### Version Format

```
v{major}.{minor}.{patch}
```

### Version Rules

1. Major: Breaking changes
2. Minor: New features, backward compatible
3. Patch: Bug fixes, backward compatible

## API Contracts

### 1. System Orchestrator API

#### Component Registration

```python
@dataclass
class RegisterComponentRequest:
    name: str
    component: Any
    metadata: Dict[str, Any]

@dataclass
class RegisterComponentResponse:
    success: bool
    component_id: str
    status: ComponentStatus
    error: Optional[str]

async def register_component(request: RegisterComponentRequest) -> RegisterComponentResponse:
    """Register a new component with the system."""
    pass
```

#### Component Status

```python
@dataclass
class GetComponentStatusRequest:
    component_id: str

@dataclass
class GetComponentStatusResponse:
    success: bool
    status: Optional[ComponentStatus]
    error: Optional[str]

async def get_component_status(request: GetComponentStatusRequest) -> GetComponentStatusResponse:
    """Get the status of a registered component."""
    pass
```

### 2. Configuration Manager API

#### Get Configuration

```python
@dataclass
class GetConfigRequest:
    key: str
    default: Optional[Any]

@dataclass
class GetConfigResponse:
    success: bool
    value: Any
    source: ConfigSource
    error: Optional[str]

async def get_config(request: GetConfigRequest) -> GetConfigResponse:
    """Get a configuration value."""
    pass
```

#### Set Configuration

```python
@dataclass
class SetConfigRequest:
    key: str
    value: Any
    source: ConfigSource
    metadata: Dict[str, Any]

@dataclass
class SetConfigResponse:
    success: bool
    version: int
    error: Optional[str]

async def set_config(request: SetConfigRequest) -> SetConfigResponse:
    """Set a configuration value."""
    pass
```

### 3. Event Bus API

#### Publish Event

```python
@dataclass
class PublishEventRequest:
    event: Event
    metadata: Dict[str, Any]

@dataclass
class PublishEventResponse:
    success: bool
    event_id: str
    error: Optional[str]

async def publish_event(request: PublishEventRequest) -> PublishEventResponse:
    """Publish an event to the bus."""
    pass
```

#### Subscribe to Event

```python
@dataclass
class SubscribeRequest:
    event_name: str
    handler: Callable
    priority: EventPriority
    metadata: Dict[str, Any]

@dataclass
class SubscribeResponse:
    success: bool
    subscription_id: str
    error: Optional[str]

async def subscribe(request: SubscribeRequest) -> SubscribeResponse:
    """Subscribe to an event."""
    pass
```

### 4. State Manager API

#### Get State

```python
@dataclass
class GetStateRequest:
    key: str
    default: Optional[Any]

@dataclass
class GetStateResponse:
    success: bool
    value: Any
    metadata: Dict[str, Any]
    error: Optional[str]

async def get_state(request: GetStateRequest) -> GetStateResponse:
    """Get a state value."""
    pass
```

#### Set State

```python
@dataclass
class SetStateRequest:
    key: str
    value: Any
    type: StateType
    metadata: Dict[str, Any]

@dataclass
class SetStateResponse:
    success: bool
    version: int
    error: Optional[str]

async def set_state(request: SetStateRequest) -> SetStateResponse:
    """Set a state value."""
    pass
```

## Error Handling

### Error Types

```python
class APIError(Exception):
    """Base class for API errors."""
    pass

class ValidationError(APIError):
    """Error raised when request validation fails."""
    pass

class NotFoundError(APIError):
    """Error raised when a resource is not found."""
    pass

class ConflictError(APIError):
    """Error raised when there is a conflict."""
    pass

class InternalError(APIError):
    """Error raised when an internal error occurs."""
    pass
```

### Error Response Format

```python
@dataclass
class ErrorResponse:
    code: str
    message: str
    details: Dict[str, Any]
    timestamp: float
```

## API Documentation

### OpenAPI/Swagger

```yaml
openapi: 3.0.0
info:
  title: UltraAI Core API
  version: 1.0.0
  description: API for UltraAI core components

paths:
  /components:
    post:
      summary: Register a new component
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RegisterComponentRequest'
      responses:
        '200':
          description: Component registered successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RegisterComponentResponse'
        '400':
          description: Invalid request
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ErrorResponse'
```

## API Success Criteria

The API contracts are successful when:

1. All endpoints are well-defined
2. Request/response formats are consistent
3. Error handling is comprehensive
4. Documentation is complete
5. Versioning is clear
6. APIs are testable

## Implementation Notes

1. Use type hints consistently
2. Implement comprehensive validation
3. Handle errors gracefully
4. Log all requests/responses
5. Monitor API usage
6. Optimize performance

## Next Steps

1. Implement API endpoints
2. Add API tests
3. Create API documentation
4. Set up monitoring
5. Optimize performance
