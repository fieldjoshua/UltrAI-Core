# ACTION: fix-core-functionality

**Version**: 1.0  
**Created**: 2025-06-07  
**Status**: Active  
**Priority**: Critical  

## Purpose

Fix critical missing functionality in UltraAI Core system to make it fully operational. The system has excellent architecture but empty route handlers, causing core endpoints to return 404 errors. This ACTION will implement the missing API endpoints to connect the well-designed service layer to actual HTTP endpoints.

## Requirements

- **Core Orchestrator Endpoint**: `POST /api/orchestrator/analyze` for main analysis functionality
- **Model Management**: `GET /api/available-models` for model listing and status  
- **Direct Analysis**: `POST /api/analyze` for simplified analysis requests
- **LLM Service Health**: Fix degraded LLM service status to "healthy"
- **Production Verification**: All endpoints tested and working on production URL

## Dependencies

### Internal Dependencies
- **OrchestrationService**: Main analysis workflow engine (app.state.orchestration_service)
- **ModelRegistry**: Model configuration and lifecycle (app.state.model_registry)  
- **LLM Adapters**: OpenAI, Anthropic, Google integrations (existing in services/)
- **Quality Evaluation**: Response assessment service (existing)

### External Dependencies  
- **API Keys**: OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY in production
- **Database**: PostgreSQL connection for persistent data
- **Redis**: Caching layer for performance
- **Render**: Production deployment platform

## Implementation Approach

### Phase 1: Core Orchestrator Implementation
**File**: `app/routes/orchestrator_minimal.py`
- Implement `POST /orchestrator/analyze` endpoint
- Connect to existing `OrchestrationService`
- Create `AnalysisRequest` and `AnalysisResponse` Pydantic models
- Add comprehensive error handling and logging

### Phase 2: Model Management Endpoints
**File**: `app/routes/available_models_routes.py`  
- Implement `GET /available-models` endpoint
- Connect to existing `ModelRegistry` service
- Return model configurations, status, and health
- Add caching for performance

### Phase 3: Analysis Routes
**File**: `app/routes/analyze_routes.py`
- Implement `POST /analyze` endpoint for direct analysis
- Add streaming response support for real-time results
- Connect to quality evaluation service
- Implement rate limiting integration

### Phase 4: LLM Service Diagnostics & Fix
**Files**: Health checks, LLM adapters
- Investigate why LLM service shows "degraded" status
- Verify API key configuration in Render production environment
- Test each LLM adapter (OpenAI, Anthropic, Google) individually
- Update health checks to properly report LLM service status
- Add fallback handling for missing/invalid API keys

### Phase 5: Testing & Production Deployment
- Unit tests for each new endpoint
- Integration tests with service layer
- Local testing with `make test` and `make prod`
- Deploy to production via `make deploy`
- **MANDATORY**: Test actual production URLs with evidence
- Document verification results in `supporting_docs/deployment-verification.md`

## Success Criteria

1. **Functional API Endpoints**:
   - `POST /api/orchestrator/analyze` returns valid analysis results
   - `GET /api/available-models` returns model list and status
   - `POST /api/analyze` provides direct analysis functionality
   - All endpoints handle errors gracefully with proper HTTP status codes

2. **LLM Service Health**:  
   - Health endpoint shows LLM service as "healthy" instead of "degraded"
   - Each LLM adapter (OpenAI, Anthropic, Google) functional or gracefully degraded
   - Clear error messages for missing/invalid API keys

3. **Production Verification** (per RULES.md requirements):
   - All endpoints tested on actual production URL: `https://ultrai-core.onrender.com`
   - End-to-end analysis workflow tested and documented
   - Response times acceptable (< 30 seconds for analysis)
   - Error handling verified in production environment

4. **Code Quality**:
   - All tests passing (154+ tests)
   - New code follows existing patterns and conventions
   - Proper logging and monitoring integration
   - API documentation updated in OpenAPI/Swagger

## Estimated Timeline

- **Phase 1 (Orchestrator)**: 4 hours - Critical path implementation
- **Phase 2 (Models)**: 2 hours - Model endpoint implementation  
- **Phase 3 (Analysis)**: 3 hours - Analysis routes and streaming
- **Phase 4 (LLM Fix)**: 3 hours - Diagnostics and API key verification
- **Phase 5 (Testing)**: 4 hours - Local testing, deployment, production verification
- **Total**: 16 hours (2 working days)

## Risk Assessment

### High Risk Items
- **LLM API Key Issues**: Production may have missing/invalid API keys
- **Service Integration**: Connecting routes to dependency-injected services
- **Production Deployment**: Ensuring changes deploy correctly on Render

### Mitigation Strategies
- Test each phase locally before proceeding
- Use existing service patterns and dependency injection
- Implement graceful degradation for missing services  
- Follow existing error handling and logging patterns
- Verify Render environment variables before final testing

## Notes

- **Architecture is Excellent**: This is implementation work, not redesign
- **Services are Ready**: Comprehensive service layer exists and is well-tested
- **Focus on Connection**: Connect existing services to HTTP endpoints
- **Production Focus**: Per RULES.md, action not complete until production verified
- **Fast Implementation**: Well-defined scope with existing architecture patterns
