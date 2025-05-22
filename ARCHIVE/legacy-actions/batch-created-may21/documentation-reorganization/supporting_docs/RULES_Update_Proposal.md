# RULES.md Update Proposal

This document outlines proposed changes to the RULES.md file to clarify documentation organization policies within the Ultra project.

## Current State

The current RULES.md file contains basic information about directory structure and documentation requirements but lacks specific guidance on:

1. How to distinguish between temporary ACTION documentation and enduring system documentation
2. When and how to migrate documentation from ACTION directories to main documentation
3. Clear criteria for what belongs in each location

## Proposed Changes

The following changes should be made to the RULES.md file:

### 1. Expand Documentation First Section

```markdown
### 2. Documentation First

The PROJECT objective must be made clear to all editors.

All ACTIONS have their own directory and must be approved and include a documented PLAN before implementation.

PLANS must be kept up to date and, along with objective instructions, must detail the value of that ACTION to the overall creation of the PROGRAM being built.

Changes, including which sole ActiveAction is being worked on, must be reflected in the ACTIONS INDEX and in relevant docs.

Supporting documentation for the ACTION must be maintained in the ACTION's supporting_docs directory.

Documentation is categorized into two main types:
- **Process Documentation**: Temporary documents relevant only during an ACTION's lifecycle, stored in .aicheck/actions/[ACTION_NAME]/supporting_docs/
- **Product Documentation**: Enduring documents with relevance beyond an ACTION's completion, stored in /documentation/[CATEGORY]/

When an ACTION is completed, any documentation with enduring value must be migrated to the appropriate /documentation/ subdirectory.
```

### 2. Add Documentation Organization Section

Add a new section after "Style Requirements":

```markdown
## Documentation Organization

### Documentation Types and Locations

1. **ACTION Process Documentation** (.aicheck/actions/[ACTION_NAME]/supporting_docs/)
   - Documents with temporary relevance during the ACTION lifecycle
   - Implementation details specific to the ACTION
   - Research notes, experiments, and progress tracking
   - Design worksheets and ACTION-specific planning

2. **Product Documentation** (/documentation/[CATEGORY]/)
   - Documents with enduring relevance beyond ACTION completion
   - System architecture and component descriptions
   - User guides and API references
   - Standards, patterns, and best practices
   - Configuration and deployment guides

### Documentation Migration

When an ACTION is completed:

1. Evaluate all documentation for enduring value
2. Prepare documents for migration by:
   - Updating ACTION-specific terminology
   - Ensuring completeness and accuracy
   - Adding appropriate metadata
3. Move relevant documents to appropriate /documentation/ subdirectories
4. Update references and documentation indexes
5. Note migrations in the ACTION completion record

A complete Documentation Migration Checklist can be found in documentation/technical/processes/documentation_migration.md
```

## Implementation Plan

After approval, these changes will be implemented as part of the DocumentationReorganization action:

1. Update RULES.md with the proposed additions
2. Create the referenced documentation_migration.md checklist
3. Communicate changes to the development team
4. Begin auditing existing documentation against the new standards

## Timeline

These changes should be implemented in Week 1 of the DocumentationReorganization action as part of Phase 1: Policy Definition and Documentation Updates.
