# Directory Inventory

This document catalogues all directories at the root level of the UltraAI codebase, providing an analysis of their purpose, content, and which action they relate to.

## Root-Level Directories

| Directory | Purpose | Content Type | Action Relationship | Target Location | Migration Priority |
|-----------|---------|--------------|---------------------|-----------------|-------------------|
| Actions/ | Action plans | Documentation | DOCUMENTATION_REPOPULATION | Keep as-is | N/A |
| documentation/ | Core documentation | Documentation | DOCUMENTATION_REPOPULATION | Keep as-is | N/A |
| frontend/ | Frontend application | Code | FRONTEND_DEVELOPMENT | Keep as-is | N/A |
| backend/ | Backend services | Code | BACKEND_INTEGRATION | Keep as-is | N/A |
| src/ | Core application code | Code | Multiple | Keep as-is | N/A |
| tests/ | Test code | Code | TESTING_STRATEGY | Keep as-is | N/A |
| mock-api/ | API mocking | Code | API_DEVELOPMENT | src/api/mocks | Medium |
| public_api/ | Public API code | Code | API_DEVELOPMENT | src/api/public | High |
| cloud_frontend/ | Cloud UI | Code | CLOUD_INTEGRATION | frontend/cloud | High |
| cloud_backend/ | Cloud services | Code | CLOUD_INTEGRATION | backend/cloud | High |
| test_frontend/ | Frontend tests | Code | TESTING_STRATEGY | tests/frontend | Medium |
| cypress/ | E2E tests | Code | TESTING_STRATEGY | tests/e2e | Medium |
| benchmarks/ | Performance tests | Code | TESTING_STRATEGY | tests/performance | Low |
| examples/ | Example code | Code | INTELLIGENCE_MULTIPLICATION | src/examples | Low |
| data/ | Data storage | Data | DATA_MANAGEMENT | src/data | Medium |
| deployment/ | Deployment config | Configuration | DEPLOYMENT_ARCHITECTURE | src/deployment | Medium |
| monitoring/ | System monitoring | Code | DEPLOYMENT_ARCHITECTURE | src/monitoring | Low |
| NEWArchive/ | Legacy code | Various | N/A | Review/Archive | Low |
| docs/ | Legacy documentation | Documentation | Multiple | Various action directories | High |
| scripts/ | Utility scripts | Code | Multiple | Keep as-is | N/A |
| config/ | Configuration files | Configuration | Multiple | src/config | Medium |
| .vscode/ | Editor config | Configuration | N/A | Keep as-is | N/A |
| .github/ | GitHub config | Configuration | N/A | Keep as-is | N/A |
| node_modules/ | Dependencies | External | N/A | Keep as-is | N/A |
| .venv/ | Python environment | External | N/A | Keep as-is | N/A |

## Analysis of Directories to Migrate

### High Priority

1. **public_api/** (→ src/api/public)
   - Contains API interfaces exposed to external users
   - Critical for API integration
   - Currently referenced by documentation

2. **cloud_frontend/** (→ frontend/cloud)
   - Cloud-specific UI components
   - Active development area
   - Multiple dependencies with frontend code

3. **cloud_backend/** (→ backend/cloud)
   - Cloud service implementations
   - Active development area
   - High integration with backend systems

4. **docs/** (→ Various action directories)
   - Legacy documentation that needs proper organization
   - May contain critical information not yet migrated
   - Needs careful analysis to distribute to appropriate action directories

### Medium Priority

1. **mock-api/** (→ src/api/mocks)
   - Used for development and testing
   - API mocking functions
   - Should align with main API structure

2. **test_frontend/** (→ tests/frontend)
   - Frontend-specific tests
   - Should be consolidated with other test code

3. **data/** (→ src/data)
   - Data management utilities
   - Used by multiple components
   - Needs careful dependency analysis

4. **deployment/** (→ src/deployment)
   - Deployment configuration and scripts
   - Used in CI/CD processes
   - Critical for production deployments

5. **config/** (→ src/config)
   - Configuration management
   - Used across the application
   - May have complex dependencies

### Low Priority

1. **benchmarks/** (→ tests/performance)
   - Performance testing tools
   - Not used in production
   - Limited dependencies

2. **examples/** (→ src/examples)
   - Example code for developers
   - Not used in production
   - Documentation-focused

3. **monitoring/** (→ src/monitoring)
   - System monitoring utilities
   - Limited integration with core code

4. **NEWArchive/** (→ Review/Archive)
   - Legacy code
   - Requires careful review before integration or archiving

## Next Steps

1. For each directory to be migrated:
   - Create detailed inventory of files and subdirectories
   - Map dependencies with other code
   - Create specific migration plan

2. Validate target directory structure:
   - Confirm final target locations for each directory
   - Evaluate impact on build system
   - Document migration strategy

3. Implement migration sequence:
   - Start with low-dependency directories
   - Progress to more complex integrations
   - Ensure continuous testing throughout

## Directory Maintenance

This inventory should be updated as the migration progresses. Each directory should include:

- Migration status
- Completion percentage
- Issues encountered
- Dependencies resolved

## Last Updated: [Current Date]
