# Claude Integration Enhancements for AICheck

## Custom Claude Commands (No Approval Required)

These commands allow Claude to work more efficiently within the AICheck system while maintaining all existing approval requirements:

### 1. Task Management Commands

```bash
# Claude can update task status without approval
aicheck task update [task-id] [status]
# Updates task in todo.md AND syncs to action.yaml

# Claude can add subtasks to existing approved tasks
aicheck task add-subtask [parent-task-id] [description]
# Adds subtask under approved parent task

# Claude can mark tasks blocked with reason
aicheck task block [task-id] [reason]
# Documents blockers for human attention
```

### 2. Progress Tracking Commands

```bash
# Claude can update progress percentage based on completed tasks
aicheck progress update
# Automatically calculates from todo.md completion ratio

# Claude can add progress notes
aicheck progress note [message]
# Adds timestamped progress updates to progress.md
```

### 3. Documentation Commands

```bash
# Claude can update supporting documentation
aicheck docs add [type] [file-path]
# Types: research, test-results, claude-interaction

# Claude can link related documentation
aicheck docs link [action1] [action2] [relationship]
# Creates cross-references between actions
```

### 4. Verification Commands

```bash
# Claude can run verification tests
aicheck verify tests
# Runs all tests and updates results

# Claude can check deployment readiness
aicheck verify ready-to-deploy
# Checks all pre-deployment criteria

# Claude can validate action consistency
aicheck verify consistency
# Ensures all files are in sync
```

### 5. Issue Tracking Commands

```bash
# Claude can report issues discovered during work
aicheck issue report [description] [severity]
# Creates issue in action.yaml and notifies

# Claude can link issues to specific code/tasks
aicheck issue link [issue-id] [task-id]
# Associates issues with tasks for tracking
```

## Commands Requiring Human Approval

These commands ALWAYS require explicit human approval before Claude can execute:

### 1. Action Lifecycle Commands (APPROVAL REQUIRED)

```bash
# Creating new actions
aicheck action new [name]  # ❌ REQUIRES APPROVAL

# Changing active action  
aicheck action set [name]  # ❌ REQUIRES APPROVAL

# Completing actions
aicheck action complete    # ❌ REQUIRES APPROVAL

# Modifying action plans
aicheck plan modify       # ❌ REQUIRES APPROVAL
```

### 2. Deployment Commands (APPROVAL REQUIRED)

```bash
# Deploying to production
aicheck deploy production  # ❌ REQUIRES APPROVAL

# Rolling back deployments
aicheck deploy rollback    # ❌ REQUIRES APPROVAL
```

### 3. Dependency Changes (APPROVAL REQUIRED)

```bash
# Adding new external dependencies
aicheck dependency add [package] [version]  # ❌ REQUIRES APPROVAL

# Updating dependency versions
aicheck dependency update [package] [version]  # ❌ REQUIRES APPROVAL
```

## Claude Workflow Enhancements

### 1. Automatic Status Updates

Claude automatically updates action status based on activity:
- When first task starts → `in_progress`
- When code is ready → `ready_to_deploy`
- When deployment verified → `verified`

### 2. Smart Task Management

Claude's TodoWrite integrations:
- Automatically creates subtasks from plan phases
- Links tasks to success criteria
- Tracks dependencies between tasks
- Estimates completion based on similar past tasks

### 3. Continuous Verification

Claude runs verification checks:
- Before marking tasks complete
- After code changes
- Before suggesting deployment
- When blockers are resolved

### 4. Context Preservation

Claude maintains context across sessions:
- Reads action.yaml for quick context
- Checks recent progress notes
- Reviews open issues
- Understands current blockers

## Integration with Native Claude Functions

### TodoRead/TodoWrite Enhancement

```yaml
# action.yaml includes todo metadata
todo_config:
  auto_subtasks: true      # Claude can create subtasks
  track_time: true         # Track time spent on tasks
  link_commits: true       # Link git commits to tasks
  require_tests: true      # Tasks need tests to complete
```

### Enhanced Task Format

```markdown
# TODO: [Action Name]

## Active Tasks
- [ ] Task description (id: task-001, priority: high, estimate: 2h)
  - [ ] Subtask auto-created by Claude (parent: task-001)
  - [ ] Test for this feature (type: test, blocks: task-001)
  
## Completed Tasks  
- [x] Completed task (id: task-002, completed: 2024-05-26, time: 1.5h)
```

## Approval Boundaries Summary

### Claude CAN (No Approval Needed):
- ✅ Update task status within approved action
- ✅ Add subtasks to approved tasks
- ✅ Update progress percentages
- ✅ Add documentation and notes
- ✅ Run verification tests
- ✅ Report discovered issues
- ✅ Update supporting documentation
- ✅ Link related items

### Claude CANNOT (Approval Required):
- ❌ Create new actions
- ❌ Change active action
- ❌ Complete actions
- ❌ Modify action plans
- ❌ Deploy to production
- ❌ Add external dependencies
- ❌ Change project structure
- ❌ Modify templates

## Example Claude Workflow with Commands

```bash
# Claude working on approved action
$ aicheck status  # Check current context

# Claude discovers issue while working
$ aicheck issue report "API endpoint returns 404" high

# Claude updates task progress
$ aicheck task update task-001 in_progress
$ aicheck progress note "Fixed import issue, testing now"

# Claude adds test results
$ aicheck docs add test-results ./test-results.json

# Claude finds task blocked
$ aicheck task block task-002 "Waiting for API credentials"

# Claude runs verification
$ aicheck verify tests
$ aicheck verify ready-to-deploy

# Claude ASKS HUMAN for approval to complete
Human: "Please complete the action"
$ aicheck action complete  # Now allowed with approval
```

This enhancement maintains the human-in-the-loop for critical decisions while giving Claude powerful tools to work efficiently within approved boundaries.