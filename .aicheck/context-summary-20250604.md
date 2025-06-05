# Context Summary - Wed Jun  4 15:45:44 PDT 2025

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
critical-path-execution

## Active Files (Modified in last 7 days)
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/deployment-validation-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/resource-monitoring-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/test_minimal_deployment.py
./.aicheck/.aicheck_backup_20250524_095556/templates/performance_optimizer.py
./.aicheck/actions_index.md
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/deployment-validation-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/resource-monitoring-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/test_minimal_deployment.py
./.aicheck/.aicheck_backup_20250524_095601/templates/performance_optimizer.py
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/deployment-validation-test.py
./.aicheck/actions/completed/mvp-minimal-deployment/supporting_docs/resource-monitoring-test.py

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
bb434799 Fix API endpoint paths and orchestrator integration
66d4048e Fix UI visibility and deploy current frontend
0a1a7e1b Fix CSP and rebuild frontend with correct API URL
9d07051a Add render.yaml for consistent production deployments
954106ee Fix frontend API URL to point to correct Render backend
f542e98f Fix frontend API URL and force CSP to include required domains
45ef5d01 Fix frontend CSP and API URL configuration for production
7fe09fbc Fix frontend asset loading and CSP for Google Fonts
4e0b40be Add missing HTTPException import for React Router fix
21b4b250 Fix React Router SPA routing for frontend

*This summary can be used instead of reading many individual files to understand project context*
