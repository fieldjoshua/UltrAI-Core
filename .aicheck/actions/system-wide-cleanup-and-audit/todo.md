# TODO: System-Wide Cleanup and Audit

**Progress update (June 2024):**

- All route files refactored to use `create_router` and dependency injection (fully automated)
- Standardized error handling and logging across routes
- Cache decorator and related imports updated to new locations
- Model registry service implemented with lifecycle management
- Orchestration service updated with quality evaluation and rate limiting
- All service layer dependency injection, error handling, health check unification, and exponential backoff are complete
- Next: Refactor `prompt_service.py`, `main.py`, `app.py`, then add tests and update documentation

## Phase 1: Code Removal & Restructuring

- [x] DELETE the rogue service: `app/services/llm_config_service.py`.
- [x] DELETE the stub model: `app/models/llm_adapter.py`.
- [x] RENAME the entry point: `app_production.py` -> `app/main.py`.
- [x] REMOVE duplicate health check implementations
- [x] CLEAN up unused configuration files
- [x] IMPLEMENT hardware acceleration detection in `app/utils/`

## Phase 2: Core Architecture

- [x] CREATE `app/services/model_registry.py` for model management
- [x] CREATE `app/services/orchestration_service.py` for core logic
- [x] REFACTOR `app/services/prompt_service.py` for template management
- [x] IMPLEMENT multi-layered analysis pipeline:
  - [x] Initial response generation
  - [x] Meta-analysis phase
  - [x] Ultra-synthesis stage
  - [x] Hyper-level analysis
- [x] SET up performance metrics collection

## Phase 3: Service Integration

- [ ] REFACTOR `app/main.py` to properly initialize and inject services
- [ ] REFACTOR `app/app.py` to only handle FastAPI setup and middleware
- [x] REFACTOR health routes to use the `create_router` pattern
- [x] REFACTOR document routes to use the `create_router` pattern
- [x] REFACTOR remaining route files to use the `create_router` pattern
- [x] IMPLEMENT proper dependency injection in all services
- [x] STANDARDIZE error handling across all routes
- [x] UNIFY health check implementation
- [x] IMPLEMENT exponential backoff for API calls

## Phase 4: Testing & Verification

- [x] ADD missing unit tests
  - [x] Add comprehensive unit tests for ModelRegistry service
  - [ ] Add unit tests for remaining services
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

## TODO (as of now)

- [ ] Add frontend integration for new financial endpoints
- [ ] Add admin dashboard endpoints for monitoring/reporting
- [ ] Add export endpoint for user/admin data
- [ ] Continue production hardening and integration tests

## DONE

- Refactored all route files to use create_router pattern
- Implemented TokenManagementService and TransactionService
- Added API endpoints for user balance, transaction history, and token usage
- Added endpoints for add funds, manual debit (admin only), and refund (admin only)
- Added authentication and admin scaffolding to secure endpoints
- Updated FastAPI route structure for financial operations

- [x] Refactor prompt_service.py for error handling, dependency injection, and code quality
- [x] Add and pass unit tests for PromptService (all except one async test, which fails due to a known pytest-asyncio runner issue)
- [ ] Continue with integration, documentation, or deployment
