# Enhanced AICheck Training Guide

## Introduction

Welcome to the Enhanced AICheck system! This guide will walk you through the new features designed to prevent incomplete deployments and improve action tracking.

## Why the Enhancement?

We discovered that actions were being marked "complete" without actually being deployed to production. The Enhanced AICheck system solves this by:

1. **Requiring deployment verification** before completion
2. **Tracking issues** that block completion
3. **Providing better visibility** into action status

## Getting Started

### 1. Installation (One-time Setup)

```bash
# Install the enhanced aicheck command
sudo cp supporting_docs/aicheck-enhanced.sh /usr/local/bin/aicheck
sudo chmod +x /usr/local/bin/aicheck

# Optional: Install git hooks for automatic tracking
./supporting_docs/git-hooks.sh install
```

### 2. Your First Enhanced Action

Let's create an action that requires deployment:

```bash
# Create new action
aicheck action new my-production-feature

# Set it as current
aicheck action set my-production-feature
```

Notice: Along with traditional files, you now have `action.yaml`!

### 3. Configure Deployment Verification

Edit `.aicheck/actions/my-production-feature/action.yaml`:

```yaml
deployment:
  required: true  # This prevents completion without verification
  environments:
    production:
      url: https://myapp.onrender.com
      test_command: "curl -f https://myapp.onrender.com/health"
      verified: false
```

### 4. Work on Your Feature

Continue using Claude's todo functionality as normal:
- TodoWrite to add tasks
- TodoRead to check progress
- Tasks remain in `todo.md`

### 5. Track Issues

If you discover problems:

```bash
# Report a critical issue (blocks completion)
aicheck issue report "API returns 500 on /users endpoint" critical

# Report a non-critical issue (warning only)
aicheck issue report "Slow response time on search" medium
```

### 6. Before Completing

```bash
# Check your status
aicheck status

# You might see:
# ⚠️  Deployment verification required but not completed
# ❌ Critical issues must be resolved:
#    - ISS-001: API returns 500 on /users endpoint (critical)
```

### 7. Fix Issues and Verify

```bash
# After fixing the API issue
aicheck issue update ISS-001 resolved

# After deploying to production
aicheck verify deployment

# If verification passes, you'll see:
# ✅ Deployment verified for environment: production
```

### 8. Complete the Action

```bash
# Now this will work
aicheck action complete

# Success! Action marked as completed
```

## Common Scenarios

### Scenario 1: Local Development Action

For actions that don't need deployment:

```yaml
deployment:
  required: false  # Can complete without deployment
```

### Scenario 2: Multi-Environment Deployment

```yaml
deployment:
  required: true
  environments:
    staging:
      url: https://staging.myapp.com
      test_command: "python test_staging.py"
      verified: false
    production:
      url: https://myapp.com
      test_command: "python test_production.py"
      verified: false
```

### Scenario 3: Working with Existing Actions

To add enhancement to existing actions:

```bash
# Migrate single action
./supporting_docs/migration-tools.sh migrate old-action-name

# Or migrate all at once
./supporting_docs/migration-tools.sh migrate-all
```

## Best Practices

### 1. Always Configure Deployment for Production Actions

```yaml
# Good: Clear test command
test_command: "curl -f https://app.com/health && curl -f https://app.com/api/status"

# Bad: No actual verification
test_command: "echo 'deployed'"
```

### 2. Use Appropriate Issue Severities

- **critical**: Blocks functionality, security issues
- **high**: Major bugs, performance problems  
- **medium**: Minor bugs, UI issues
- **low**: Nice-to-have improvements

### 3. Keep Issues Updated

```bash
# When starting work on an issue
aicheck issue update ISS-001 in_progress

# When fixed
aicheck issue update ISS-001 resolved
```

### 4. Sync Regularly

If not using git hooks:

```bash
# After making changes
aicheck sync
```

## Troubleshooting

### "Cannot complete action" Error

Check for:
1. Unverified deployment: Run `aicheck verify deployment`
2. Critical issues: Run `aicheck issue list`
3. Out of sync: Run `aicheck sync`

### Verification Keeps Failing

1. Check your test_command actually tests the deployment
2. Ensure the URL is accessible
3. Try running the test_command manually

### Git Push Blocked

The pre-push hook prevents pushing with unverified deployments:

```bash
# Emergency bypass (use sparingly!)
git push --no-verify

# Better: Verify first
aicheck verify deployment
git push
```

## Quick Command Reference

```bash
# Most common workflow
aicheck action new <name>          # Start
aicheck issue report "<>" critical # Track problems
aicheck verify deployment          # Verify deployment
aicheck issue update <id> resolved # Fix issues
aicheck action complete            # Finish

# Checking status
aicheck status                     # Full status
aicheck issue list                 # Just issues
```

## Team Adoption Checklist

- [ ] Install enhanced aicheck command
- [ ] Install git hooks (recommended)
- [ ] Run migration on existing actions
- [ ] Configure deployment verification for production actions
- [ ] Brief team on critical issues blocking completion
- [ ] Set up deployment test commands
- [ ] Update CI/CD to use `aicheck verify deployment`

## Support

- Documentation: `ENHANCED_AICHECK_DOCUMENTATION.md`
- Quick Reference: `QUICK_REFERENCE.md`
- Test Scripts: `test-*.sh`

Remember: The goal is to ensure what we mark as "complete" is actually deployed and working in production!