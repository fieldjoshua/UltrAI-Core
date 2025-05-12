# Proposed Structure for Iterative Orchestrator

This document outlines the proposed directory structure and component organization for the Iterative Orchestrator implementation. It provides a clear map of the final structure and identifies components that should be archived.

## Directory Structure

```
src/
├── orchestration/
│   ├── __init__.py
│   ├── base.py                  # BaseOrchestrator implementation
│   ├── enhanced.py              # EnhancedOrchestrator implementation
│   ├── config.py                # Orchestrator configuration classes
│   ├── patterns/                # Analysis patterns
│   │   ├── __init__.py
│   │   ├── base.py              # Base pattern interface
│   │   ├── registry.py          # Pattern registry
│   │   ├── standard.py          # Standard patterns implementation
│   │   └── custom.py            # Custom patterns implementation
│   ├── progress/                # Progress tracking
│   │   ├── __init__.py
│   │   ├── tracker.py           # Progress tracking implementation
│   │   └── events.py            # Progress event definitions
│   ├── evaluation/              # Response evaluation
│   │   ├── __init__.py
│   │   ├── quality.py           # Quality evaluation implementation
│   │   └── metrics.py           # Metrics collection
│   └── utils/                   # Utility functions
│       ├── __init__.py
│       ├── retry.py             # Retry logic
│       ├── circuit_breaker.py   # Circuit breaker implementation
│       └── resource.py          # Resource optimization
│
├── adapters/                    # LLM service adapters
│   ├── __init__.py
│   ├── base.py                  # Base adapter interface
│   ├── openai.py                # OpenAI adapter implementation
│   ├── anthropic.py             # Anthropic adapter implementation
│   ├── gemini.py                # Google Gemini adapter implementation
│   ├── mistral.py               # Mistral adapter implementation
│   ├── factory.py               # Adapter factory functions
│   └── mock.py                  # Mock adapter implementation
│
├── services/                    # Service layer
│   ├── __init__.py
│   ├── orchestration_service.py # Service for orchestrator management
│   ├── config_service.py        # Configuration management service
│   ├── cache_service.py         # Caching service
│   └── mock_service.py          # Mock service for testing
│
└── cli/                         # Command-line interface
    ├── __init__.py
    ├── analyzer.py              # Simple analyzer CLI
    └── utils.py                 # CLI utilities

backend/
├── api/                         # API endpoints
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── analyze.py           # Analysis endpoints
│   │   └── models.py            # Model information endpoints
│   └── models/                  # API models
│       ├── __init__.py
│       ├── requests.py          # Request models
│       └── responses.py         # Response models
│
└── services/                    # Backend-specific services
    ├── __init__.py
    ├── orchestration.py         # Backend orchestration service
    └── document.py              # Document processing service

tests/
├── unit/
│   ├── orchestration/           # Orchestrator unit tests
│   └── adapters/                # Adapter unit tests
└── integration/
    ├── orchestration/           # Orchestrator integration tests
    └── api/                     # API integration tests

ARCHIVE/
├── legacy/                      # Archived legacy code
│   ├── ultra_hyper.py
│   ├── orchestrator.py
│   └── enhanced_orchestrator_old.py
└── duplicates/                  # Archived duplicate implementations
    ├── backend_models/
    └── src_models/
```

## Component Mapping

### 1. Core Orchestration Components

| New Component | Derived From | Description |
|---------------|--------------|-------------|
| `src/orchestration/base.py` | `SimpleAnalyzer`, `MultiLLMOrchestrator` | Core orchestration functionality |
| `src/orchestration/enhanced.py` | `EnhancedOrchestrator` | Advanced orchestration features |
| `src/orchestration/config.py` | `EnhancedOrchestrator`, `SimpleAnalyzer` | Configuration classes |

### 2. Adapter Components

| New Component | Derived From | Description |
|---------------|--------------|-------------|
| `src/adapters/base.py` | `llm_adapter.py` | Base adapter interface |
| `src/adapters/openai.py` | `OpenAIAdapter` | OpenAI-specific implementation |
| `src/adapters/anthropic.py` | `AnthropicAdapter` | Anthropic-specific implementation |
| `src/adapters/gemini.py` | `GeminiAdapter` | Google Gemini implementation |
| `src/adapters/factory.py` | `create_adapter()` | Adapter factory functions |
| `src/adapters/mock.py` | `mock_llm_service.py` | Mock adapter implementation |

### 3. Service Components

| New Component | Derived From | Description |
|---------------|--------------|-------------|
| `src/services/orchestration_service.py` | `PromptService` | Orchestrator management service |
| `src/services/config_service.py` | `LLMConfigService` | Configuration management |
| `src/services/cache_service.py` | Cache implementations | Unified caching service |

### 4. API Components

| New Component | Derived From | Description |
|---------------|--------------|-------------|
| `backend/api/routes/analyze.py` | `analyze_routes.py` | Analysis API endpoints |
| `backend/api/models/requests.py` | Current request models | API request models |
| `backend/api/models/responses.py` | Current response models | API response models |

### 5. CLI Components

| New Component | Derived From | Description |
|---------------|--------------|-------------|
| `src/cli/analyzer.py` | `SimpleAnalyzer` | Command-line interface |

## Files to Archive

The following files should be archived as they will be replaced by the new implementation:

| File to Archive | Archive Location | Reason |
|-----------------|-----------------|--------|
| `src/core/ultra_hyper.py` | `ARCHIVE/legacy/ultra_hyper.py` | Replaced by new orchestrator |
| `src/legacy/ultra_hyper.py` | `ARCHIVE/legacy/ultra_hyper.py` | Duplicate implementation |
| `src/orchestrator.py` | `ARCHIVE/legacy/orchestrator.py` | Replaced by new orchestrator |
| `src/models/enhanced_orchestrator.py` | `ARCHIVE/duplicates/src_models/enhanced_orchestrator.py` | Duplicate implementation |
| `backend/models/enhanced_orchestrator.py` | `ARCHIVE/duplicates/backend_models/enhanced_orchestrator.py` | Replaced by new orchestrator |
| `simple_analyzer.py` | (Keep in root for reference) | Will be replaced but keep for reference |
| `backend/mock_llm_service.py` | `ARCHIVE/duplicates/backend_mock_llm_service.py` | Replaced by unified mock service |
| `backend/services/mock_llm_service.py` | `ARCHIVE/duplicates/backend_services_mock_llm_service.py` | Replaced by unified mock service |

## Migration Strategy

The migration to the new structure will follow these steps:

1. **Create Core Components**
   - Implement `BaseOrchestrator` in `src/orchestration/base.py`
   - Implement adapter classes in `src/adapters/`
   - Implement configuration in `src/orchestration/config.py`

2. **Create CLI Interface**
   - Implement `src/cli/analyzer.py` as direct replacement for `simple_analyzer.py`
   - Test functionality to ensure it works the same as the original

3. **Implement Enhanced Features**
   - Add `EnhancedOrchestrator` in `src/orchestration/enhanced.py`
   - Implement patterns, progress tracking, and resource optimization
   - Test functionality against original implementation

4. **Update Service Layer**
   - Create new services in `src/services/`
   - Implement backward compatibility adapters

5. **Update API Layer**
   - Create new API routes in `backend/api/routes/`
   - Use service layer for orchestration
   - Implement feature parity with existing endpoints

6. **Perform Integration Testing**
   - Test end-to-end functionality
   - Verify compatibility with existing systems
   - Benchmark performance

7. **Archive Legacy Code**
   - Move replaced files to archive locations
   - Update imports and references
   - Document archived components

## Key Interface Changes

### BaseOrchestrator Interface

```python
class BaseOrchestrator:
    """Core orchestration system for managing LLM requests and responses."""
    
    def __init__(self, config=None):
        """Initialize the orchestrator with configuration."""
        
    async def check_availability(self):
        """Check which models are available and responsive."""
        
    async def process(self, prompt, models=None, primary_model=None):
        """Process a prompt using multiple LLMs and synthesize results."""
        
    async def _send_to_llm(self, model_name, prompt):
        """Send prompt to a specific LLM and handle errors."""
        
    async def _synthesize_responses(self, prompt, responses, primary_model):
        """Combine multiple LLM responses into a single result."""
```

### EnhancedOrchestrator Interface

```python
class EnhancedOrchestrator(BaseOrchestrator):
    """Enhanced orchestration system with advanced features."""
    
    def __init__(self, config=None):
        """Initialize the enhanced orchestrator with configuration."""
        
    async def process_with_pattern(self, prompt, pattern=None, models=None, primary_model=None):
        """Process a prompt using a specific analysis pattern."""
        
    async def process_with_document(self, prompt, document, pattern=None, models=None):
        """Process a prompt with an attached document."""
        
    async def stream_process(self, prompt, pattern=None, models=None):
        """Process a prompt with streaming responses."""
```

### Adapter Interface

```python
class LLMAdapter:
    """Base adapter for LLM integrations."""
    
    def __init__(self, provider, api_key=None, model=None):
        """Initialize the adapter with provider and API key."""
        
    async def generate(self, prompt, **options):
        """Generate a response from the LLM."""
        
    async def stream_generate(self, prompt, **options):
        """Generate a streaming response from the LLM."""
        
    def get_capabilities(self):
        """Get capabilities of this LLM."""
        
    async def check_availability(self):
        """Check if the LLM is available."""
```

### Service Interface

```python
class OrchestrationService:
    """Service for managing orchestrators and processing prompts."""
    
    def __init__(self, config_service):
        """Initialize the orchestration service."""
        
    async def analyze_prompt(self, prompt, models=None, primary_model=None, pattern=None, options=None):
        """Analyze a prompt using LLMs and return the results."""
        
    async def analyze_with_document(self, prompt, document, models=None, primary_model=None, pattern=None):
        """Analyze a prompt with an attached document."""
        
    async def stream_analyze(self, prompt, models=None, primary_model=None, pattern=None):
        """Analyze a prompt with streaming responses."""
```