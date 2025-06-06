# Context Summary - Thu Jun  5 21:06:42 PDT 2025

## Project Overview
# AICheck MCP Project

This project uses AICheck Multimodal Control Protocol for AI-assisted development.

## Claude Code Commands

Claude Code now supports the following AICheck slash commands:

- `./aicheck status` - Show current action status
- `./aicheck action new ActionName` - Create a new action
- `./aicheck action set ActionName` - Set current active action
- `./aicheck action complete [ActionName]` - Complete action with dependency verification
- `./aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]` - Add external dependency
- `./aicheck dependency internal DEP_ACTION ACTION TYPE [DESCRIPTION]` - Add internal dependency
- `./aicheck exec` - Toggle exec mode for system maintenance

## Project Structure

The AICheck system follows a structured approach to development:

## Current Action
system-wide-cleanup-and-audit

## Active Files (Modified in last 7 days)
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/deployment-validation-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/resource-monitoring-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/test_minimal_deployment.py
./.aicheck/.aicheck_backup_20250524_095556/templates/performance_optimizer.py
./.aicheck/actions_index.md
./.aicheck/README.md
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/deployment-validation-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/resource-monitoring-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/test_minimal_deployment.py
./.aicheck/.aicheck_backup_20250524_095601/templates/performance_optimizer.py
./.aicheck/context-summary-20250605.md
./.aicheck/pattern-cache-20250604.md
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py

## Key Dependencies



## Recent Changes
8093776d Refactor app setup, fix router dependency injection, resolve linter errors across app, main, and prompt_service
e9456d7a chore(security): update dependencies and remove unused packages to resolve vulnerabilities [system-wide-cleanup-and-audit]
b87fbfd6 refactor: system-wide cleanup and audit - Phase 3 progress - Refactored health routes and document routes to use dependency injection - Removed duplicate health check implementations - Deleted rogue llm_config_service
a31fcc35 Build: Migrate to Poetry for dependency management
e5191055 Final attempt to fix build
43aef44b Build: Finalize and verify Render deployment configuration
e1835481 Fix: Unpin dependencies to resolve build conflicts
e8fa6e15 Build: Finalize application refactor and import cleanup
4237272a Refactor: Complete system audit and structural refactor
0227ed52 Refactor: Centralize path correction at entry point to fix all imports

*This summary can be used instead of reading many individual files to understand project context*
