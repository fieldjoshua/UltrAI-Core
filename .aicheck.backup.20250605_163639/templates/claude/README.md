# Claude Templates Documentation

This directory contains templates for use with Claude Code interactions.

## Available Templates

### System Review Templates

- `system-review/status-update.md` - Comprehensive AICheck system status review

### Action Implementation Templates

- `action-implementation/basic.md` - Standard implementation template
- Additional pattern-specific templates as needed

### Testing Templates

- `testing/unit-tests.md` - Unit test generation template
- `testing/integration-tests.md` - Integration test template
- `testing/e2e-tests.md` - End-to-end test template

### Documentation Templates

- `documentation/action-docs.md` - ACTION documentation template
- `documentation/api-docs.md` - API documentation template

### Code Review Templates

- `code-review/security-review.md` - Security review template
- `code-review/performance-review.md` - Performance review template

### Migration Templates

- `migration/code-migration.md` - Code migration template
- `migration/test-migration.md` - Test migration template

## Custom Commands

### /aicheck

A custom command for comprehensive AICheck system status reviews.

**Usage:**

```bash
# In conversation with Claude:
/aicheck

# Or using the AI CLI:
./ai claude prompt system-review/status-update
```

This command triggers a comprehensive review including:

- Active Action status
- Action pipeline analysis
- System health metrics
- Compliance verification
- Risk assessment
- Recommendations

## Template Versioning

All templates include version headers:

```markdown
<!-- Template Version: 1.0 -->
<!-- Last Updated: 2025-05-16 -->
<!-- Changes: Initial version -->
```

## Adding New Templates

1. Create template in appropriate subdirectory
2. Include version header
3. Document in this README
4. Update change log below

## Change Log

### Version 1.0 (2025-05-16)

- Initial template structure
- Added system review template
- Created /aicheck custom command documentation
