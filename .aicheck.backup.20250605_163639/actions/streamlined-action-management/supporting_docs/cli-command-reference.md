# AICheck Enhanced CLI Command Reference

## Overview

AICheck Enhanced preserves all existing functionality while adding deployment verification, issue tracking, and automated synchronization capabilities. All commands are backward compatible.

## Command Categories

### 1. Action Management (Existing + Enhanced)

#### `aicheck action new [name]`
Creates a new action with traditional files PLUS action.yaml
- Creates: plan.md, status.txt, progress.md, todo.md, action.yaml
- Updates: actions_index.md
- **No approval required** (but plan requires approval before implementation)

#### `aicheck action set [name]`
Sets the current active action
- Updates: .aicheck/current_action
- Changes status to ActiveAction
- **REQUIRES APPROVAL**

#### `aicheck action complete [name]`
Completes an action with enhanced verification
- **NEW**: Checks deployment.verified if required
- **NEW**: Blocks if critical issues are open
- Existing dependency checks preserved
- **REQUIRES APPROVAL**

### 2. Deployment Verification (NEW)

#### `aicheck deploy verify [action]`
Runs deployment verification for an action
- Executes test_command from action.yaml
- Updates deployment.verified status
- Records verification results
- **No approval required** (running tests)

#### `aicheck deploy status [action]`
Shows deployment status for an action
- Displays last deployment time
- Shows verification status
- Lists any failed tests
- **No approval required** (read-only)

### 3. Issue Tracking (NEW)

#### `aicheck issue report [description] [severity] [action]`
Reports an issue discovered during work
- Severity: low, medium, high, critical
- Adds to action.yaml issues array
- Generates unique issue ID
- **No approval required** (documenting problems)

#### `aicheck issue list [action]`
Lists all issues for an action
- Shows open/resolved status
- Filters by severity
- **No approval required** (read-only)

#### `aicheck issue resolve [issue-id] [resolution]`
Marks an issue as resolved
- Updates issue status
- Records resolution notes
- **No approval required** (fixing problems)

### 4. Task Management (NEW)

#### `aicheck task update [task-id] [status]`
Updates task status in todo.md
- Status: pending, in_progress, completed, blocked
- Syncs with action.yaml task_summary
- **No approval required** (within approved action)

#### `aicheck task add [description] [priority]`
Adds a new task to current action
- Priority: low, medium, high
- Appends to todo.md
- **No approval required** (subtasks of approved work)

#### `aicheck task block [task-id] [reason]`
Marks a task as blocked
- Documents blocker reason
- Notifies in action status
- **No approval required** (documenting impediments)

### 5. Synchronization (NEW)

#### `aicheck sync [action] [direction]`
Synchronizes action.yaml with traditional files
- Direction: yaml-to-files (default), files-to-yaml
- Updates status, progress, task counts
- Resolves conflicts with warnings
- **No approval required** (maintaining consistency)

#### `aicheck sync all`
Synchronizes all actions
- Batch operation for maintenance
- Shows sync summary
- **No approval required** (maintenance task)

### 6. Progress Tracking (NEW)

#### `aicheck progress update [action]`
Recalculates progress from completed tasks
- Reads todo.md completion status
- Updates progress percentage
- Syncs to action.yaml
- **No approval required** (automated calculation)

#### `aicheck progress note [message]`
Adds a timestamped progress note
- Appends to progress.md
- Useful for status updates
- **No approval required** (documentation)

### 7. Dependency Management (Existing + Enhanced)

#### `aicheck dependency add [name] [version] [justification] [action]`
Adds external dependency (existing command)
- **NEW**: Also updates action.yaml dependencies
- **REQUIRES APPROVAL**

#### `aicheck dependency internal [from] [to] [type] [description]`
Links internal dependencies (existing command)
- **NEW**: Updates action.yaml internal dependencies
- **REQUIRES APPROVAL**

#### `aicheck dependency check [action]`
Verifies all dependencies are documented
- Scans code for imports
- Compares with documented dependencies
- **No approval required** (verification only)

### 8. Migration Tools (NEW)

#### `aicheck migrate [action]`
Migrates an existing action to include action.yaml
- Preserves all existing files
- Generates action.yaml from current state
- Non-destructive operation
- **No approval required** (additive only)

#### `aicheck migrate all`
Migrates all actions to new format
- Batch migration with progress
- Creates backup before migration
- **No approval required** (but recommended to backup first)

### 9. Utility Commands (Enhanced)

#### `aicheck status`
Shows current AICheck status (enhanced)
- **NEW**: Shows deployment status if applicable
- **NEW**: Lists open issues count
- **NEW**: Shows sync status
- Existing git status info preserved
- **No approval required** (read-only)

#### `aicheck exec`
Toggle exec mode (existing)
- For system maintenance only
- **Special mode - different approval rules apply**

#### `aicheck doctor`
Diagnoses AICheck system health (NEW)
- Checks for missing files
- Validates action.yaml syntax
- Verifies dependencies installed
- Suggests fixes for common issues
- **No approval required** (diagnostic only)

## Quick Reference Table

| Command | Requires Approval | Purpose |
|---------|-------------------|---------|
| `action new` | No* | Create new action (*plan needs approval) |
| `action set` | YES | Change active action |
| `action complete` | YES | Complete an action |
| `deploy verify` | No | Run deployment tests |
| `deploy status` | No | Check deployment status |
| `issue report` | No | Report a problem |
| `issue resolve` | No | Fix a problem |
| `task update` | No | Update task status |
| `task add` | No | Add subtask |
| `sync` | No | Sync files |
| `progress update` | No | Calculate progress |
| `dependency add` | YES | Add external package |
| `migrate` | No | Add action.yaml to existing action |
| `status` | No | View current status |
| `doctor` | No | System health check |

## Integration with Claude

Claude can use all "No approval required" commands freely to:
- Track progress on approved work
- Document issues discovered
- Run tests and verifications
- Keep files synchronized
- Add detailed notes and documentation

Claude must request approval before using:
- Action lifecycle commands (new, set, complete)
- Dependency management commands
- Any command that changes project structure

## Examples

### Starting a new action (requires approval)
```bash
# Human approves creating new action
aicheck action new enhance-api-performance
aicheck action set enhance-api-performance  # Requires approval
```

### Working on approved action (no approval needed)
```bash
# Claude working within approved action
aicheck task add "Profile API endpoints" high
aicheck task update task-001 in_progress
aicheck progress note "Found bottleneck in database queries"
aicheck issue report "N+1 query in user endpoint" high
aicheck deploy verify  # Test changes
aicheck task update task-001 completed
aicheck progress update  # Recalculate percentage
```

### Completing action (requires approval)
```bash
# Claude requests approval to complete
aicheck deploy verify  # Final verification
aicheck issue list  # Show any open issues
# Human: "approved to complete"
aicheck action complete enhance-api-performance
```