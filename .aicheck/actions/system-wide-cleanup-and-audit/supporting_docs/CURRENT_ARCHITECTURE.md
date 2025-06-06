# Current System Architecture: The Ground Truth

## Core Application Structure

### Entry Points

- `app/main.py`: Production entry point with startup message
- `app/app.py`: Core FastAPI application with middleware and route registration

### Routes (`app/routes/`)

- `analyze_routes.py`: Analysis endpoints with pattern mappings
- `auth_routes.py`: Authentication endpoints (login, register, etc.)
- `document_analysis_routes.py`: Document processing endpoints
- `health_routes.py`: Health check endpoints
- `llm_routes.py`: LLM management endpoints
- `user_routes.py`: User management endpoints
- `debug_routes.py`: Debugging endpoints

### Services (`app/services/`)

- `auth_service.py`: Authentication and user management
- `cache_service.py`: Redis-based caching with memory fallback
- `document_analysis_service.py`: Document processing
- `health_service.py`: System health monitoring
- `llm_config_service.py`: LLM configuration management (to be removed)
- `llm_fallback_service.py`: Fallback handling for LLM services
- `oauth_service.py`: OAuth integration
- `prompt_service.py`: Prompt management
- `rate_limit_service.py`: Rate limiting implementation

### Models (`app/models/`)

- Various Pydantic models for request/response validation
- Database models for user and session management

### Utils (`app/utils/`)

- `circuit_breaker.py`: Circuit breaker pattern implementation
- `health_check.py`: Health check framework
- `rate_limit_middleware.py`: Rate limiting middleware
- `recovery_strategies.py`: Service recovery patterns

## Current Issues

1. **Service Architecture**

   - Multiple singleton service instances
   - Inconsistent dependency injection patterns
   - Overlapping responsibilities between services
   - Rogue `llm_config_service.py` still present
   - Missing proper model registry implementation
   - Incomplete multi-layered analysis pipeline

2. **Route Organization**

   - Inconsistent route registration patterns
   - Mixed use of dependency injection
   - Duplicate health check implementations
   - Missing proper error handling patterns

3. **Configuration**

   - Multiple configuration files
   - Runtime configuration validation
   - Inconsistent environment variable usage
   - Missing hardware acceleration detection

4. **Error Handling**

   - Inconsistent error response formats
   - Mixed use of custom exceptions
   - Incomplete error recovery strategies
   - Missing exponential backoff implementation

5. **Testing**

   - Incomplete test coverage
   - Missing integration tests
   - Inconsistent test organization
   - Missing performance metrics collection

6. **Patent Alignment Issues**
   - Missing proper multi-layered analysis pipeline
   - Incomplete model registry implementation
   - Missing hardware acceleration support
   - Incomplete prompt template system
   - Missing proper meta-analysis implementation
   - Incomplete ultra-synthesis stage
   - Missing hyper-level analysis
