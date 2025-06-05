# Context Summary - Wed Jun  4 20:51:21 PDT 2025

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
None

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
./.aicheck/pattern-cache-20250604.md
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py

## Key Dependencies

# UltraAI Production Requirements
# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0.post1
gunicorn==21.2.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6

# Database

## Recent Changes
c49bf9e1 Fix Google client initialization bug in orchestrator
462060a9 Fix orchestrator timeout issue - implement parallel execution
654a184d Implement simplified working orchestrator to fix timeout issue
ceb7f095 Fix integration import path for production deployment
63478923 Fix orchestration timeout issue - model name mapping and timeout handling
317ad9c0 Fix LLM health check to accept 'ok' status from providers
9f4a98af Fix LLM health check error: iterate over dictionary values not keys
ae66e705 Fix API key configuration in render.yaml - remove circular reference
67e97708 Fix API URL - remove /api suffix to match working deployment
91764ac9 Remove environment toggle - hardcode production API URL

*This summary can be used instead of reading many individual files to understand project context*
