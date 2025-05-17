# ACTION: mvp-minimal-deployment

Version: 1.0
Last Updated: 2025-05-17
Status: ActiveAction
Progress: 75%

## Objective

Create a minimal deployment configuration that maintains ALL MVP functionality while optimizing for resource efficiency on Render's limited infrastructure.

## Problem Statement

The current minimal deployment is failing because:

1. Critical MVP dependencies (SQLAlchemy, Redis) are missing from requirements-minimal.txt
2. app_minimal.py doesn't properly initialize all MVP features
3. The deployment attempts to strip functionality rather than optimize it
4. Missing proper database and caching setup for MVP features

## Success Criteria

1. ALL MVP features work in minimal deployment:
   - Document upload and analysis
   - Multiple LLM orchestration
   - Authentication and user accounts
   - Parameter optimization
   - Result caching and storage
2. Deployment succeeds on Render with minimal resources
3. Fast startup time (< 30 seconds)
4. Memory usage under 512MB
5. All existing MVP tests pass

## Approach

### Phase 1: MVP Feature Analysis (Day 1)

- Review all MVP ACTIONS to identify required functionality
- List all MVP features that must work
- Map dependencies to features
- Create minimal but complete dependency set

### Phase 2: Test Suite Preparation (Day 1) ✓ COMPLETED

- ✓ Gathered all MVP tests from previous ACTIONS
- ✓ Written tests for resource-constrained scenarios
- ✓ Created deployment validation tests
- ✓ Test memory usage and startup time

### Phase 3: Implementation (Day 2) ✓ COMPLETED

1. ✓ Updated requirements-minimal.txt with ALL required dependencies:

   - ✓ SQLAlchemy (for user accounts, document storage)
   - ✓ Redis (for caching, session management)
   - ✓ All LLM provider libraries
   - ✓ Authentication libraries
   - ✓ Document processing libraries

2. ✓ Enhanced app_minimal.py to:

   - ✓ Initialize database properly
   - ✓ Set up Redis connection with fallback
   - ✓ Import ALL MVP routes with error handling
   - ✓ Configure minimal middleware
   - ✓ Optimize startup sequence

3. ✓ Created resource optimization:
   - ✓ Dependency checking on startup
   - ✓ Connection pooling for database
   - ✓ Graceful degradation for optional features
   - ✓ Minimal logging in production

### Phase 4: Testing (Day 3)

- Run full MVP test suite
- Test document upload/analysis flow
- Test multi-LLM orchestration
- Test authentication flow
- Monitor resource usage
- Deploy to Render test environment

### Phase 5: Documentation and Deployment (Day 3)

- Document minimal deployment approach
- Create troubleshooting guide
- Deploy to production
- Verify all MVP features work

## Dependencies

- AuthenticationSystem ACTION (for user auth features)
- DocumentAnalysis ACTION (for document processing)
- LLMOrchestration ACTION (for multi-model support)
- DatabaseSetup ACTION (for storage requirements)

## Test Requirements

1. **MVP Feature Tests**

   - All tests from AuthenticationSystem ACTION
   - All tests from DocumentAnalysis ACTION
   - All tests from LLMOrchestration ACTION
   - All integration tests

2. **Resource Tests**

   - Memory usage under load
   - Startup time measurement
   - Database connection limits
   - Concurrent request handling

3. **Deployment Tests**
   - Full E2E flow on Render
   - Health check verification
   - Error recovery scenarios
   - Graceful degradation tests

## Implementation Details

### Key Files to Modify

1. `requirements-minimal.txt`

   ```
   # Core framework
   fastapi==0.109.0
   uvicorn[standard]==0.27.0

   # Database (REQUIRED for MVP)
   SQLAlchemy==2.0.23
   psycopg2-binary==2.9.9

   # Caching (REQUIRED for MVP)
   redis==5.0.1

   # Authentication (REQUIRED for MVP)
   python-jose[cryptography]==3.3.0
   passlib[bcrypt]==1.7.4
   python-multipart==0.0.6

   # LLM Providers (REQUIRED for MVP)
   openai==1.6.1
   anthropic==0.8.1
   google-generativeai==0.3.2

   # Document Processing (REQUIRED for MVP)
   python-magic==0.4.27
   chardet==5.2.0

   # Utilities
   python-dotenv==1.0.0
   httpx==0.25.2
   pydantic==2.5.3
   ```

2. `backend/app_minimal.py`

   - Import ALL routes (not just some)
   - Initialize database on startup
   - Set up Redis connection
   - Configure proper error handling
   - Add resource monitoring

3. `render-prod.yaml`
   - Ensure sufficient memory allocation
   - Set correct environment variables
   - Configure health check properly

## Resource Optimization Strategies

1. **Lazy Loading**

   - Load LLM clients only when needed
   - Defer heavy imports
   - Use connection pooling

2. **Caching Strategy**

   - Cache frequently used data
   - Implement cache expiration
   - Use Redis efficiently

3. **Database Optimization**
   - Connection pooling
   - Query optimization
   - Proper indexing

## Risk Mitigation

1. **Risk**: Memory overflow

   - Mitigation: Implement memory monitoring
   - Solution: Optimize data structures

2. **Risk**: Slow startup

   - Mitigation: Profile startup sequence
   - Solution: Defer non-critical initialization

3. **Risk**: Missing MVP features
   - Mitigation: Comprehensive test suite
   - Solution: Full MVP validation before deployment

## Approval Required From

Joshua Field

## Notes

- This is NOT about removing features, it's about optimizing resource usage
- ALL MVP functionality must work exactly as in full deployment
- Focus on smart loading and caching, not feature reduction
- Must pass all existing MVP tests without modification
