# AICheck Git Hooks

This directory contains git hooks to enforce AICheck compliance as defined in RULES.md.

## Phased Implementation

### Phase 1 (Required - Implemented)

- ✅ Commit message format validation (50-char subject, present tense)
- ✅ ACTION directory structure validation for new ACTIONS
- ✅ Basic security checks (via pre-commit framework)
- ✅ File format validation (JSON, YAML)

### Phase 2 (Required - Implemented)

- ✅ Test existence verification for implementation changes
- ✅ Basic documentation completeness checks
- ✅ Status file validation (.aicheck/current_action)
- ✅ ACTION reference in commit messages (warning only)

### Phase 3 (Future - Not Required)

- ❌ Claude interaction logging automation
- ❌ Full PLAN approval workflow integration
- ❌ Comprehensive migration tracking
- ❌ Automated documentation migration

## Hooks

### commit-msg

Location: `.git/hooks/commit-msg`
Purpose: Validates commit message format according to RULES.md

- Enforces 50-character subject line limit
- Requires present-tense verb at start
- Warns about missing ACTION references
- Warns about implementation without tests

### pre-commit-aicheck

Location: `.aicheck/hooks/pre-commit-aicheck`
Purpose: Validates AICheck structure and compliance

- Checks new ACTION directory structure
- Validates current_action file
- Warns about missing documentation updates

## Integration

The hooks are integrated via `.pre-commit-config.yaml` which runs both standard code quality checks and AICheck-specific validations.

## Testing Hooks

To test commit message validation:

```bash
echo "This is a very long commit message that definitely exceeds fifty characters" > test_msg
.git/hooks/commit-msg test_msg
```

To test pre-commit validation:

```bash
.aicheck/hooks/pre-commit-aicheck
```

## Disabling Hooks (Emergency Only)

If you need to bypass hooks in an emergency:

```bash
git commit --no-verify -m "Emergency fix"
```

Note: This should only be used following the Quick Response protocol in RULES.md section 5.3.