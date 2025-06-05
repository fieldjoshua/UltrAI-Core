# AICheck System Update Instructions

## Overview

This document provides step-by-step instructions for the AICheck team to update the existing system with enhanced streamlined action management capabilities. The update preserves all existing functionality while adding deployment verification and automated tracking.

## Pre-Update Checklist

- [ ] Backup current `.aicheck` directory
- [ ] Ensure all active actions are in a stable state
- [ ] Commit any pending changes
- [ ] Install `yq` for YAML support (see dependencies)

## Dependencies

### Required
- **yq** - YAML parser for bash
  ```bash
  # macOS
  brew install yq
  
  # Linux
  wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq
  chmod +x /usr/bin/yq
  ```

### Optional but Recommended
- **jq** - JSON parser (for deployment verification results)
  ```bash
  # macOS
  brew install jq
  
  # Linux
  apt-get install jq  # or yum install jq
  ```

## Update Process

### Step 1: Backup Current System

```bash
# Create timestamped backup
cp -r .aicheck .aicheck_backup_$(date +%Y%m%d_%H%M%S)

# Verify backup
ls -la .aicheck_backup_*
```

### Step 2: Update AICheck Script

**Option A: Safe Gradual Update (Recommended)**

1. Copy the enhanced script alongside the original:
```bash
cp /path/to/aicheck-enhanced.sh ./aicheck-enhanced
chmod +x ./aicheck-enhanced
```

2. Test enhanced version in parallel:
```bash
# Test new commands without affecting current workflow
./aicheck-enhanced deploy verify
./aicheck-enhanced issue report "test issue" low
./aicheck-enhanced doctor
```

3. Once verified, replace original:
```bash
cp ./aicheck ./aicheck.original
cp ./aicheck-enhanced ./aicheck
```

**Option B: Direct Update**

1. Apply the enhancements directly to existing aicheck:
```bash
# Add new functions to existing aicheck script
# Insert after existing functions, before main command handling
```

### Step 3: Update Git Hooks

1. Enhanced pre-commit hook for deployment verification:

```bash
cat > .aicheck/hooks/pre-commit << 'HOOK'
#!/bin/bash

# Enhanced pre-commit hook with deployment verification

# Check if committing action completion
if git diff --cached --name-only | grep -q "status.txt" && \
   git diff --cached .aicheck/actions/*/status.txt | grep -q "Completed"; then
   
  # Find which action is being completed
  for action_dir in .aicheck/actions/*/; do
    if git diff --cached "$action_dir/status.txt" 2>/dev/null | grep -q "Completed"; then
      action_name=$(basename "$action_dir")
      
      # Check if action.yaml exists and deployment is required
      if [ -f "$action_dir/action.yaml" ]; then
        deploy_required=$(yq '.deployment.required' "$action_dir/action.yaml" 2>/dev/null)
        deploy_verified=$(yq '.deployment.environments.production.verified' "$action_dir/action.yaml" 2>/dev/null)
        
        if [ "$deploy_required" = "true" ] && [ "$deploy_verified" != "true" ]; then
          echo "ERROR: Action $action_name requires deployment verification"
          echo "Run: ./aicheck deploy verify $action_name"
          exit 1
        fi
      fi
    fi
  done
fi

exit 0
HOOK

chmod +x .aicheck/hooks/pre-commit
```

2. Install the hook:
```bash
.aicheck/hooks/install-hooks.sh
```

### Step 4: Add action.yaml to Existing Actions

For each existing action, create a companion action.yaml:

```bash
# Migration script
for action_dir in .aicheck/actions/*/; do
  if [ -d "$action_dir" ] && [ ! -f "$action_dir/action.yaml" ]; then
    action_name=$(basename "$action_dir")
    status=$(cat "$action_dir/status.txt" 2>/dev/null || echo "unknown")
    
    # Generate action.yaml
    cat > "$action_dir/action.yaml" << YAML
version: "1.0"
action:
  name: $action_name
  status: $status
  created: "2024-01-01"  # Update with actual date if known
  
files:
  plan: $action_name-plan.md
  todo: todo.md
  progress: progress.md
  
deployment:
  required: false  # Set to true for actions that need deployment
  
dependencies:
  external: []
  internal: []
  
issues: []

notes: |
  Migrated from legacy format
YAML

    echo "Created action.yaml for $action_name"
  fi
done
```

### Step 5: Update Templates

1. Update action creation template in aicheck script (already included in enhanced version)

2. Create deployment verification template:
```bash
mkdir -p .aicheck/templates
cp /path/to/verify-deployment-template.py .aicheck/templates/
```

### Step 6: Test the Update

Run comprehensive tests:

```bash
# 1. Test existing commands still work
./aicheck status
./aicheck action set [current-action]

# 2. Test new commands
./aicheck doctor  # System health check
./aicheck deploy verify  # Should work on actions with deployment config
./aicheck issue report "Test issue" low
./aicheck sync

# 3. Create a test action
./aicheck action new test-enhanced-action
# Verify it has action.yaml

# 4. Test completion with deployment check
# (Configure test-enhanced-action with deployment.required: true)
./aicheck action complete test-enhanced-action
# Should fail without verification
```

### Step 7: Update Documentation

1. Add new command reference to team docs
2. Update RULES.md (requires approval)
3. Create quick reference card for new commands

## Rollback Plan

If issues arise:

```bash
# Restore original aicheck
cp ./aicheck.original ./aicheck

# Remove action.yaml files if needed
find .aicheck/actions -name "action.yaml" -delete

# Restore from backup if necessary
rm -rf .aicheck
cp -r .aicheck_backup_[timestamp] .aicheck
```

## Post-Update Verification

- [ ] All existing commands work as before
- [ ] New actions get action.yaml automatically
- [ ] Deployment verification blocks completion when required
- [ ] Issue tracking works
- [ ] Sync command updates files correctly
- [ ] Git hooks enforce deployment verification

## Gradual Adoption Strategy

### Week 1: Parallel Testing
- Run enhanced version alongside original
- Test with non-critical actions
- Gather feedback

### Week 2: Soft Launch
- Update aicheck script
- Keep deployment.required: false for existing actions
- Train team on new commands

### Week 3: Full Adoption
- Enable deployment verification for critical actions
- Migrate all active actions to include action.yaml
- Update team workflows

### Week 4: Optimization
- Tune based on team feedback
- Add custom verification scripts
- Document best practices

## Troubleshooting

### Common Issues

1. **yq not found**
   - Install yq as per dependencies section
   - Fallback: Commands work without YAML features

2. **action.yaml syntax errors**
   - Run: `yq '.' action.yaml` to validate
   - Check for proper indentation

3. **Git hooks not triggering**
   - Ensure hooks are executable
   - Check .git/hooks/ symlinks

4. **Sync conflicts**
   - Manual resolution required
   - Check sync.conflicts in action.yaml

## Support

For issues or questions:
- Check `./aicheck doctor` output first
- Review error messages for specific commands
- Consult this update guide
- Escalate to Joshua Field for RULES.md changes