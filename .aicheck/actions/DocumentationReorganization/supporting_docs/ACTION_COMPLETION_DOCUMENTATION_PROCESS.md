# ACTION Completion Documentation Process

## Overview

This document outlines the official process for handling documentation as part of the ACTION completion procedure. It ensures that all valuable documentation is preserved and properly organized as ACTIONS move to completion.

## Process Steps

### 1. Documentation Audit

Before marking an ACTION as complete, perform a comprehensive documentation audit:

- [ ] Identify all documentation files in the ACTION directory
- [ ] Ensure all documentation is properly stored in the supporting_docs directory
- [ ] Evaluate each document against the migration criteria in the [Documentation Migration Process](documentation/technical/processes/documentation_migration.md)

### 2. Documentation Migration

For each document with enduring value:

- [ ] Complete the [Documentation Migration Checklist](/.aicheck/actions/DocumentationReorganization/supporting_docs/Documentation_Migration_Checklist.md)
- [ ] Move the document to the appropriate location in the main documentation system
- [ ] Add a migration notice to the original file
- [ ] Update the [Documentation Migration Registry](documentation/technical/documentation_registry.md)

### 3. Documentation Clean-up

After migration is complete:

- [ ] Ensure all remaining ACTION documentation is properly organized in supporting_docs
- [ ] Verify that all documentation follows naming conventions
- [ ] Remove any redundant or obsolete documentation

### 4. Documentation Summary

As part of the ACTION completion record:

- [ ] Create a summary of the documentation produced during the ACTION
- [ ] List all documents that were migrated to the main documentation system
- [ ] Note any documentation that should be revisited in future ACTIONS

## Verification

Before final completion approval:

- [ ] Verify that all migration checklists are completed
- [ ] Confirm that the Documentation Migration Registry has been updated
- [ ] Check that all documentation references have been updated

## Integration with ACTION Completion Process

This documentation process should be integrated into the standard ACTION completion workflow:

1. Complete ACTION objectives
2. Perform documentation audit and migration
3. Create completion record with documentation summary
4. Request approval for ACTION completion
5. On approval, finalize documentation status

## Documentation Completion Approval

ACTION completion approval should include verification that documentation has been properly handled:

- [ ] Documentation audit completed
- [ ] Valuable documentation migrated
- [ ] Documentation Migration Registry updated
- [ ] Documentation summary included in completion record

## Templates

### Documentation Migration Summary Template

```markdown
## Documentation Migration Summary

| Document Name | Original Location | Migration Status | New Location |
|---------------|-------------------|------------------|--------------|
| [Document 1]  | [Path]            | Migrated         | [New Path]   |
| [Document 2]  | [Path]            | Not Applicable   | N/A          |

**Migration Rationale:**
[Brief explanation of why certain documents were or weren't migrated]
```

### Documentation Completion Verification Template

```markdown
## Documentation Completion Verification

- [x] Documentation audit completed on [DATE]
- [x] [NUMBER] documents evaluated for migration
- [x] [NUMBER] documents migrated to main documentation
- [x] Documentation Migration Registry updated
- [x] All remaining documentation properly organized in supporting_docs
- [ ] Documentation references updated

**Approved by:** [NAME]
**Date:** [DATE]
```

## Implementation Timeline

This process should be implemented:

1. Immediately for all newly completed ACTIONS
2. Retroactively for recently completed ACTIONS
3. Gradually for older completed ACTIONS as resources permit

## Responsibilities

- **ACTION Owner**: Responsible for initiating the documentation process
- **Documentation Team**: Provides support for complex migrations
- **Approving Manager**: Verifies documentation completion as part of ACTION approval
