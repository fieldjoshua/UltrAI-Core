# Migration Guide

This document outlines the strategy for migrating from the current orchestration system to the new Iterative Orchestrator.

## Migration Strategy

The migration will follow a phased approach to minimize disruption:

1. **Parallel Implementation**: The new orchestrator will be implemented alongside the existing system
2. **Adapter Layer**: An adapter will allow existing code to use the new orchestrator
3. **Gradual Transition**: Components will transition incrementally to direct use of the new orchestrator
4. **Validation**: Each transition will be validated to ensure equivalent functionality
5. **Deprecation**: Once all components have migrated, the legacy system will be deprecated

## Migration Steps

### Step 1: Implement BaseOrchestrator

The BaseOrchestrator will implement core functionality to support:

- Sending prompts to multiple LLMs in parallel
- Error handling and retries
- Basic response synthesis
- Mock mode support

This can be used independently of the existing system for new code.

### Step 2: Create Adapter for Existing Code

The adapter will:

- Translate between legacy request formats and new orchestrator formats
- Ensure consistent responses between old and new systems
- Allow gradual adoption without breaking changes

Example adapter usage:

```python
# Current code
result = await legacy_orchestrator.process(prompt, models)

# With adapter
adapter = OrchestratorAdapter(new_orchestrator)
legacy_request = {"prompt": prompt, "models": models}
adapted_request = await adapter.adapt_request(legacy_request)
result = await new_orchestrator.process(**adapted_request)
result = await adapter.adapt_response(result)
```

### Step 3: Implement EnhancedOrchestrator

The EnhancedOrchestrator will add advanced features:

- Document processing
- Analysis pattern selection
- Caching
- Detailed metrics

This component will support all existing functionality with improved architecture.

### Step 4: Update API Endpoints

API endpoints will be updated to use the new orchestrator directly:

```python
# Before
@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = await legacy_orchestrator.process(request.prompt, request.models)
    return result

# After
@router.post("/analyze")
async def analyze(request: AnalyzeRequest):
    result = await new_orchestrator.process(request.prompt, selected_models=request.models)
    return result
```

### Step 5: Refactor Dependent Services

Services that depend on orchestration will be updated to use the new system:

```python
# Before
class AnalysisService:
    def __init__(self):
        self.orchestrator = legacy_orchestrator
        
    async def analyze(self, data):
        # Use legacy orchestrator
        
# After
class AnalysisService:
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator or new_orchestrator
        
    async def analyze(self, data):
        # Use new orchestrator
```

### Step 6: Deprecate Legacy Components

Once all components have migrated:

1. Mark legacy components as deprecated
2. Update documentation to reference new system
3. Plan for eventual removal in future release

## Configuration Migration

### Legacy Configuration Format

```python
# Legacy format
{
    "gpt4": {
        "provider": "openai",
        "api_key": "sk-...",
        "parameters": {
            "temperature": 0.7,
            "max_tokens": 2000
        }
    },
    "claude3": {
        "provider": "anthropic",
        "api_key": "sk-ant-...",
        "parameters": {
            "temperature": 0.5,
            "max_tokens": 4000
        }
    }
}
```

### New Configuration Format

```python
# New format
{
    "models": {
        "gpt4": {
            "provider": "openai",
            "api_key": "sk-...",
            "parameters": {
                "temperature": 0.7,
                "max_tokens": 2000
            }
        },
        "claude3": {
            "provider": "anthropic",
            "api_key": "sk-ant-...",
            "parameters": {
                "temperature": 0.5,
                "max_tokens": 4000
            }
        }
    },
    "default_ultra_model": "gpt4",
    "default_models": ["gpt4", "claude3"],
    "caching": {
        "enabled": true,
        "ttl": 3600
    }
}
```

## Testing During Migration

During migration, tests will ensure functionality is preserved:

1. **Equivalent Response Tests**: Verify that new system produces equivalent results
2. **Performance Tests**: Ensure no performance regression
3. **Error Handling Tests**: Validate consistent error handling
4. **Integration Tests**: Verify correct interaction with other components

## Timeline

The migration is expected to follow this timeline:

1. BaseOrchestrator Implementation: 2 days
2. Adapter Layer Creation: 1 day
3. EnhancedOrchestrator Implementation: 2 days
4. API Endpoint Updates: 1 day
5. Dependent Service Refactoring: 1 day
6. Testing and Validation: Ongoing throughout

## Rollback Plan

If significant issues are encountered:

1. Revert API endpoints to use legacy system
2. Document specific issues encountered
3. Address issues in new orchestrator
4. Resume migration with additional testing