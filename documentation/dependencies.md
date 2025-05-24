# Dependency Management in Ultra

This document outlines the dependency management approach in the Ultra backend, including how to handle optional dependencies, fallback mechanisms, and configuration options.

## Overview

Ultra uses a graceful degradation approach for handling optional dependencies. This means that the application can run with reduced functionality when certain dependencies are not available, rather than failing completely.

The dependency management system is implemented in `backend/utils/dependency_manager.py` and provides:

- Automatic detection of available dependencies
- Fallback implementations for critical services
- Feature flags based on dependency availability
- Clear error messages and installation instructions

## Dependency Classification

Dependencies in Ultra are classified as either **required** or **optional**:

### Required Dependencies

These dependencies are essential for the core functionality of the application:

| Dependency    | Purpose                      | Affected Components                        |
| ------------- | ---------------------------- | ------------------------------------------ |
| fastapi       | Core API framework           | All API endpoints                          |
| uvicorn       | ASGI server                  | Application server                         |
| pydantic      | Data validation              | All models and request/response validation |
| SQLAlchemy    | Database ORM                 | All database operations (has fallback)     |
| python-dotenv | Environment variable loading | Configuration                              |

### Optional Dependencies

These dependencies enhance functionality but are not required for the core application to run:

| Dependency                             | Purpose                | Affected Features                       | Graceful Degradation Path          |
| -------------------------------------- | ---------------------- | --------------------------------------- | ---------------------------------- |
| PyJWT                                  | JWT token handling     | Authentication                          | Simplified JWT implementation      |
| passlib                                | Password hashing       | User authentication                     | Use simplified auth in development |
| redis                                  | Caching, rate limiting | Performance optimization, Rate limiting | In-memory cache and rate limiting  |
| sentry_sdk                             | Error tracking         | Production monitoring                   | Disable Sentry integration         |
| anthropic, openai, google-generativeai | LLM integrations       | Multi-model analysis                    | Use mock LLM service               |

### Sophisticated Orchestration Dependencies (Production)

These dependencies are required for the patent-protected UltraAI orchestration platform:

| Dependency                             | Version | Purpose                | Patent Component                        | Required For                       |
| -------------------------------------- | ------- | ---------------------- | --------------------------------------- | ---------------------------------- |
| beautifulsoup4                         | 4.12.2  | Document processing    | Context-aware prompt interpolation      | Feather analysis with documents    |
| cachetools                             | 5.3.2   | Performance caching    | Quality evaluation optimization         | Enhanced orchestrator performance  |
| backoff                                | 2.2.1   | Circuit breaker logic  | Fault tolerance patterns                | Resilient multi-LLM orchestration |
| PyPDF2                                 | 3.0.1   | PDF document processing| Document context integration            | 4-stage analysis with documents    |
| python-docx                            | 1.1.0   | Word document processing| Structured document analysis           | Business document Feather patterns|
| openpyxl                               | 3.1.2   | Excel processing       | Data analysis workflows                 | Spreadsheet-based analysis        |
| prometheus_client                      | 0.19.0  | Performance monitoring | Quality evaluation metrics              | Patent claim validation           |
| bleach                                 | 6.1.0   | Security sanitization  | Input security for document processing | Safe document context integration |

## UltraAI Patent-Protected Features

The sophisticated orchestration dependencies enable UltraAI's patent-protected competitive advantages:

### 4-Stage Feather Analysis Workflow
- **Initial Stage**: Base LLM responses to user prompts
- **Meta Stage**: Cross-model analysis and refinement using `cachetools` for performance
- **Hyper Stage**: Quality evaluation and synthesis with `prometheus_client` monitoring
- **Ultra Stage**: Final orchestrated response with circuit breakers (`backoff`)

### Document Context Integration
- **PDF Processing**: `PyPDF2` enables sophisticated document analysis workflows
- **Word Documents**: `python-docx` supports business document Feather patterns
- **Web Content**: `beautifulsoup4` provides HTML parsing for context-aware analysis
- **Security**: `bleach` ensures safe document processing without XSS vulnerabilities

### Patent Claims Implementation
These dependencies directly support filed patent claims:
- **Claim 1-5**: Dynamic model registry with runtime configuration
- **Claim 6-10**: Quality evaluation and synthesis engines
- **Claim 11-15**: Circuit breaker patterns for fault tolerance
- **Claim 16-20**: Context-aware prompt interpolation with documents
- **Claim 21-26**: Performance monitoring and optimization systems

**Note**: Removing these dependencies would compromise patent defensibility and competitive advantages.

## Configuration Options

### Environment Variables

The following environment variables control dependency behavior:

| Variable                | Purpose                                   | Default |
| ----------------------- | ----------------------------------------- | ------- |
| `ENABLE_DB_FALLBACK`    | Enable fallback for database              | `true`  |
| `DB_CONNECTION_TIMEOUT` | Timeout for database connection (seconds) | `5`     |
| `CACHE_ENABLED`         | Enable caching                            | `true`  |
| `ENABLE_REDIS_CACHE`    | Enable Redis for caching (vs in-memory)   | `true`  |
| `ENABLE_JWT_AUTH`       | Enable JWT authentication                 | `true`  |
| `USE_MOCK`              | Use mock LLM services                     | `false` |
| `SENTRY_DSN`            | Sentry DSN for error tracking             | (empty) |

### Runtime Status Check

You can check the status of dependencies at runtime by calling the health endpoints:

- GET `/api/dependencies` - Get detailed information about all dependencies
- GET `/api/system/health` - Get system health information including dependency status

## Fallback Implementations

### Database Fallback

When PostgreSQL is not available, the system falls back to an in-memory database:

- Implemented in `backend/database/memory_db.py`
- Provides basic CRUD operations
- Supports simple querying and filtering
- Data is lost on application restart

Configure with:

```
ENABLE_DB_FALLBACK=true
```

### Caching Fallback

When Redis is not available, the system falls back to an in-memory cache:

- Implemented in `backend/services/cache_service.py`
- Uses an LRU (Least Recently Used) strategy to manage memory usage
- Configurable maximum items to prevent memory leaks
- Thread-safe for concurrent access

Configure with:

```
ENABLE_REDIS_CACHE=true
CACHE_ENABLED=true
MAX_MEMORY_ITEMS=1000
```

### JWT Fallback

When PyJWT is not available, the system falls back to a simplified JWT implementation:

- Implemented in `backend/utils/jwt_wrapper.py`
- Supports basic token creation and validation
- Only supports HS256 algorithm
- Not as secure as PyJWT for production use

## Installation Groups

We recommend installing dependencies based on your deployment needs:

### Core Dependencies

```bash
pip install -r requirements-core.txt
```

### Development Environment (All Dependencies)

```bash
pip install -r requirements.txt
```

### Minimal Production (Core + Selected Optional)

```bash
pip install -r requirements-core.txt
pip install redis PyJWT sentry_sdk
```

## Adding New Dependencies

When adding new dependencies to the Ultra project:

1. Classify the dependency as required or optional
2. Add appropriate error handling and fallback for optional dependencies
3. Use the `OptionalDependency` class for clean import management
4. Document the dependency in this file

Example pattern for new optional dependencies:

```python
from backend.utils.dependency_manager import OptionalDependency

# Define the dependency
my_dependency = OptionalDependency(
    module_name="my_module",
    display_name="My Module",
    is_required=False,
    feature_name="my_feature",
    installation_cmd="pip install my_module",
    fallback_factory=lambda: MyFallbackImplementation()
)

# Use the dependency
if my_dependency.is_available():
    module = my_dependency.get_module()
    # Use the module
else:
    # Use fallback implementation
    fallback = my_dependency.get_implementation()
```

## Dependency Status Monitoring

In production, you should monitor the dependency status to ensure all required services are available. The system logs warnings when running with fallback implementations, which should be monitored and addressed.

For critical dependencies, configure alerts when the system is running in fallback mode for extended periods.
