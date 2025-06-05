# Integration Plan with Existing AICheck System

## Analysis of Current AICheck System

### Existing Structure
- **aicheck** bash script with commands:
  - `action new` - Creates action with plan.md, status.txt, progress.md
  - `action set` - Sets current action
  - `action complete` - Completes action with dependency checks
  - `dependency add` - Adds external dependencies
  - `dependency internal` - Links internal dependencies
  - `exec` - Toggle exec mode
  - `status` - Show current status

### Key Files Currently Used
- `.aicheck/current_action` - Tracks active action
- `.aicheck/actions/[name]/[name]-plan.md` - Action plan
- `.aicheck/actions/[name]/status.txt` - Action status
- `.aicheck/actions/[name]/progress.md` - Progress tracking
- `.aicheck/actions_index.md` - Master action list
- `documentation/dependencies/dependency_index.md` - Dependencies

### Important: Claude's Native Todo Integration
- Claude uses native TodoRead/TodoWrite functions
- These work with todo.md files in action directories
- This functionality MUST be preserved

## Integration Strategy

### 1. Hybrid Approach: action.yaml + Existing Files

Instead of replacing everything, `action.yaml` becomes a **companion file** that:
- Consolidates key information for automation
- Keeps existing files for backward compatibility
- Syncs automatically with traditional files

```yaml
# action.yaml - Machine-readable companion to existing files
version: "1.0"
action:
  name: orchestration-integration-fix
  status: in_progress  # Synced with status.txt
  
# Links to existing files (not replacements)
files:
  plan: orchestration-integration-fix-plan.md
  todo: todo.md  # Claude's native todo file
  progress: progress.md
  
# New consolidated tracking
deployment:
  required: true
  verified: false
  
issues:
  - id: issue-001
    desc: "Orchestration not working"
```

### 2. Enhanced CLI Commands (Backward Compatible)

#### Existing Commands (Preserved)
- `aicheck action new` - Creates traditional structure + action.yaml
- `aicheck action set` - Works as before
- `aicheck action complete` - Enhanced with deployment checks

#### New Commands (Added)
- `aicheck deploy verify` - Run deployment verification
- `aicheck issue add` - Track issues in action.yaml
- `aicheck sync` - Sync action.yaml with traditional files
- `aicheck migrate` - Convert old actions to hybrid format

### 3. File Synchronization Strategy

```bash
# When action.yaml is updated
aicheck sync
# This updates:
# - status.txt from action.status
# - progress.md from action.tasks
# - actions_index.md from all action.yaml files

# When traditional files are updated
aicheck sync --reverse
# This updates:
# - action.yaml from status.txt, todo.md, etc.
```

### 4. Claude Todo Integration Preserved

The todo.md file remains the primary task tracking for Claude:

```yaml
# action.yaml references but doesn't replace todo.md
files:
  todo: todo.md  # Claude continues using TodoRead/TodoWrite
  
# Optional task summary in action.yaml for automation
task_summary:
  total: 10
  completed: 3
  source: todo.md  # Indicates primary source
```

### 5. Deployment Verification Integration

```bash
# New deployment commands
aicheck deploy verify
# Runs verification script
# Updates action.yaml deployment section
# Blocks completion if not verified

aicheck action complete
# Now checks action.yaml deployment.verified
# Falls back to manual check if action.yaml missing
```

### 6. Progressive Migration

#### Phase 1: New Actions (Immediate)
- Create both traditional files AND action.yaml
- Test synchronization
- Preserve all existing workflows

#### Phase 2: Active Actions (Week 1)
- Add action.yaml to active actions
- Run in parallel mode
- Monitor for issues

#### Phase 3: Historical Actions (Week 2-4)
- Migrate completed actions
- Preserve all original files
- Generate action.yaml from existing data

## Implementation Details

### Enhanced aicheck Script Structure

```bash
#!/bin/bash
# Existing functions preserved...

# New function: Create action.yaml
function create_action_yaml() {
  local action_name=$1
  local dir_name=$2
  
  cat > ".aicheck/actions/$dir_name/action.yaml" << YAML
version: "1.0"
action:
  name: $action_name
  status: not_started
  created: $(date +"%Y-%m-%d")
  
files:
  plan: $dir_name-plan.md
  todo: todo.md
  progress: progress.md
  
deployment:
  required: false
  
dependencies:
  external: []
  internal: []
  
issues: []
YAML
}

# Enhanced create_action function
function create_action() {
  # ... existing code ...
  
  # Add action.yaml creation
  create_action_yaml "$action_name" "$dir_name"
  
  # Create empty todo.md for Claude
  touch ".aicheck/actions/$dir_name/todo.md"
}

# New function: Deployment verification
function verify_deployment() {
  local action_name=$1
  # ... implementation ...
}
```

### Git Hook Enhancement

```bash
# Enhanced pre-commit hook
if grep -q "action complete" "$commit_msg_file"; then
  # Check for action.yaml
  if [ -f "$action_dir/action.yaml" ]; then
    # Check deployment.verified in YAML
    verified=$(yq '.deployment.verified' "$action_dir/action.yaml")
    if [ "$verified" != "true" ] && [ "$(yq '.deployment.required' "$action_dir/action.yaml")" = "true" ]; then
      echo "ERROR: Deployment not verified for $action_name"
      exit 1
    fi
  fi
fi
```

## Benefits of This Approach

1. **No Breaking Changes** - Everything continues to work
2. **Claude Integration Preserved** - TodoRead/TodoWrite unchanged
3. **Progressive Enhancement** - Add features without disruption
4. **Dual-Mode Operation** - Use traditional OR automated workflows
5. **Easy Rollback** - Can disable action.yaml anytime
6. **Maintains AICheck Philosophy** - Documentation-first approach

## Risk Mitigation

1. **Sync Conflicts** - Last-write-wins with warnings
2. **Missing action.yaml** - Falls back to traditional files
3. **YAML Parsing Errors** - Validation before write
4. **Claude Compatibility** - todo.md remains canonical source
5. **User Adoption** - Both workflows supported indefinitely