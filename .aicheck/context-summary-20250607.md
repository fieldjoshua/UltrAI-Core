# Context Summary - Sat Jun  7 09:34:21 PDT 2025

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
investigate-git-commit-omissions

## Active Files (Modified in last 7 days)
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/deployment-validation-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/resource-monitoring-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/test_minimal_deployment.py
./.aicheck/.aicheck_backup_20250524_095556/templates/performance_optimizer.py
./.aicheck/pattern-cache-20250606.md
./.aicheck/context-summary-20250607.md
./.aicheck/actions_index.md
./.aicheck/context-summary-20250606.md
./.aicheck/README.md
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/deployment-validation-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/resource-monitoring-test.py
./.aicheck/.aicheck_backup_20250524_095601/actions/mvp-minimal-deployment/supporting_docs/test_minimal_deployment.py
./.aicheck/.aicheck_backup_20250524_095601/templates/performance_optimizer.py
./.aicheck/context-summary-20250605.md

## Key Dependencies

-r requirements-production.txt

## Recent Changes
938a3927 Complete fix-simple-orchestrator-parallel action [fix-simple-orchestrator-parallel]
f53da54e chore: finalize AICheck investigation completion, migrate docs, and update timeline
e27d9ef9 chore: complete AICheck investigation action and apply remediation fixes
89562db7 Add PDF generation and artifact upload to CI [investigate-git-commit-omissions]
e45514c2 Add MCP CLI install and server-list step to Basic CI
04a52f1c Add MCP config
71c672f8 Finalize Impact Assessment and Recommendations [investigate-git-commit-omissions]
0b97296a Enhance investigation report with CI and working-tree audit [investigate-git-commit-omissions]
55c26eff Populate timeline in investigation report [investigate-git-commit-omissions]
555ce053 Draft investigation report skeleton [investigate-git-commit-omissions]

*This summary can be used instead of reading many individual files to understand project context*
