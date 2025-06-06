# TODO: System-Wide Cleanup and Audit

## Phase 1: Code Removal & Restructuring

- [x] DELETE the rogue service: `app/services/llm_config_service.py`.
- [ ] DELETE the stub model: `app/models/llm_adapter.py`.
- [ ] RENAME the entry point: `app_production.py` -> `app/main.py`.
- [x] REMOVE duplicate health check implementations
- [ ] CLEAN up unused configuration files
- [ ] IMPLEMENT hardware acceleration detection in `app/utils/`

## Phase 2: Core Architecture

- [ ] CREATE `app/services/model_registry.py` for model management
- [ ] CREATE `app/services/orchestration_service.py` for core logic
- [ ] REFACTOR `app/services/prompt_service.py` for template management
- [ ] IMPLEMENT multi-layered analysis pipeline:
  - [ ] Initial response generation
  - [ ] Meta-analysis phase
  - [ ] Ultra-synthesis stage
  - [ ] Hyper-level analysis
- [ ] SET up performance metrics collection

## Phase 3: Service Integration

- [ ] REFACTOR `app/main.py` to properly initialize and inject services
- [ ] REFACTOR `app/app.py` to only handle FastAPI setup and middleware
- [x] REFACTOR health routes to use the `create_router` pattern
- [ ] REFACTOR document routes to use the `create_router` pattern
- [ ] REFACTOR remaining route files to use the `create_router` pattern
- [ ] IMPLEMENT proper dependency injection in all services
- [ ] STANDARDIZE error handling across all routes
- [x] UNIFY health check implementation
- [ ] IMPLEMENT exponential backoff for API calls

## Phase 4: Testing & Verification

- [ ] ADD missing unit tests
- [ ] IMPLEMENT integration tests
- [ ] ADD end-to-end tests for critical paths
- [ ] VERIFY all functionality works as expected
- [ ] DOCUMENT test coverage
- [ ] TEST hardware acceleration support
- [ ] VERIFY performance metrics collection

## Phase 5: Documentation & Deployment

- [ ] UPDATE API documentation
- [ ] DOCUMENT service interfaces
- [ ] CREATE deployment guide
- [ ] VERIFY deployment configuration
- [ ] TEST production deployment
- [ ] VERIFY patent alignment
- [ ] DOCUMENT performance benchmarks
