# MVP Feature Requirements for Minimal Deployment

Based on the mvp-minimal-deployment PLAN, these are the MVP features that MUST ALL work in the minimal deployment:

## Core MVP Feature Requirements

### 1. Authentication System (REQUIRED)

- User registration (`/api/auth/register`)
- User login (`/api/auth/login`)
- Password reset (`/api/auth/request-password-reset`)
- Token management (access/refresh tokens)
- JWT authentication with blacklist support
- OAuth2 support for third-party authentication

### 2. Document Management (REQUIRED)

- Document upload (`/api/upload-document`)
- File storage system (local/cloud)
- Document metadata tracking
- Support for multiple file types
- Document processing pipeline

### 3. LLM Provider Integration (REQUIRED)

- Multi-provider support:
  - OpenAI (GPT-4, GPT-4 Turbo)
  - Anthropic (Claude 3 models)
  - Google (Gemini 1.5)
  - DeepSeek
  - Local models (via Docker Model Runner)
- Fallback mechanism between providers
- Mock LLM service for testing
- Resilient client with retry logic

### 4. Analysis & Orchestration (REQUIRED)

- Advanced analysis endpoints (`/analyze`)
- Pattern-based analysis (14 patterns)
- Multi-model orchestration
- Progress tracking via SSE
- Caching for performance
- Document analysis capabilities

### 5. Frontend/UI Components (REQUIRED)

#### Core Pages

- Document Management page (`/documents`)
- Analysis page (`/analyze`) - Main MVP interface
- Model Runner page (`/modelrunner`)
- Orchestrator page (`/orchestrator`)

#### Essential UI Components

- **PromptInput** - Text input for analysis prompts
- **ModelSelector** - Multi-model selection interface
- **AnalysisPatternSelector** - Pattern selection UI
- **AnalysisResults** - Results display with multiple views
- **DocumentUpload** - File upload with drag & drop
- **LoadingSpinner** - Progress indicators
- **ErrorFallback** - Error handling UI

#### Multi-step Analysis Workflow

1. Welcome/Introduction
2. Enter Prompt
3. Select Models
4. Choose Analysis Pattern
5. Upload Documents (optional)
6. Processing Progress
7. View Results

#### Key UI Features

- Side-by-side model comparison
- Combined results view
- Export functionality (JSON, CSV, Markdown)
- Analysis history
- Real-time progress tracking
- Responsive design
- Error recovery UI

### 6. Performance Requirements

- Deployment succeeds on Render with minimal resources
- Fast startup time (< 30 seconds)
- Memory usage under 512MB
- All existing MVP tests pass
- UI remains responsive under load

## Key Principles

1. **This is NOT about removing features** - ALL MVP functionality must be preserved
2. **Focus on resource optimization** - Smart loading, caching, connection pooling
3. **Graceful degradation** - Optional dependencies can fail without breaking core features
4. **Test-driven validation** - All MVP tests must pass without modification

## Critical Endpoints That Must Work

### Authentication

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/refresh`
- `POST /api/auth/request-password-reset`

### Documents

- `POST /api/upload-document`
- `GET /api/documents/{document_id}`
- `DELETE /api/documents/{document_id}`

### Analysis

- `POST /analyze`
- `GET /analyze/stream/{analysis_id}`
- `GET /analyze/results/{analysis_id}`

### LLM Management

- `GET /api/available-models`
- `GET /api/llm/status`
- `POST /api/llm/health-check`

### Orchestrator

- `POST /api/orchestrator/analyze`
- `GET /api/orchestrator/models`
- `GET /api/orchestrator/patterns`

### Health & Monitoring

- `GET /api/health`
- `GET /api/metrics`
- `GET /api/internal/resources`

### Frontend Routes

- `/` - Redirects to analyze page
- `/analyze` - Main analysis interface
- `/documents` - Document management
- `/modelrunner` - Model runner interface
- `/orchestrator` - Orchestrator interface

## Resource Optimization Strategies

1. **Dependency Management**

   - Include ALL required dependencies
   - Implement graceful fallbacks for optional ones
   - Use lazy loading where possible

2. **Memory Management**

   - Connection pooling for database
   - Efficient caching strategies
   - Limit concurrent operations
   - Monitor resource usage

3. **Startup Optimization**

   - Defer non-critical initialization
   - Lazy load heavy components
   - Minimize import time

4. **Runtime Efficiency**
   - Single worker process
   - Limited thread pool
   - Efficient request handling
   - Resource monitoring

## Success Criteria

The minimal deployment is successful when:

1. ALL MVP features work exactly as in full deployment
2. Resource usage stays within limits (512MB RAM, < 30s startup)
3. All existing MVP tests pass without modification
4. Deployment succeeds on Render's minimal infrastructure
5. Performance is acceptable for production use

## Notes

- Use SQLite for development/testing, PostgreSQL for production
- Redis is optional but recommended for caching
- Sentry is optional for monitoring
- Focus on core functionality, not bells and whistles
- Document any trade-offs made for resource optimization
