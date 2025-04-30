# Documentation Organization Policy

## Overview

This document establishes the documentation organization policy for the Ultra project, with a specific focus on properly categorizing and storing documentation artifacts during and after ACTION completion.

## Core Principles

The Ultra documentation system follows two fundamental principles:

1. **Separation of Process vs. Product Documentation**
   - Process documentation (temporary, ACTION-specific) is kept in .aicheck
   - Product documentation (enduring, system-specific) is kept in /documentation

2. **Appropriate Categorization of Documentation Types**
   - Each document has a specific home based on its purpose and lifespan
   - A systematic migration process occurs when ACTIONS are completed

## Documentation Categories and Storage Locations

### 1. ACTION Process Documentation (.aicheck/actions/[ACTION_NAME]/supporting_docs/)

Documentation that belongs in an ACTION's supporting_docs directory has the following characteristics:

- **Temporary relevance**: Only useful during the ACTION's lifecycle
- **Process-focused**: Related to how the ACTION is being implemented
- **Reference value limited**: Minimal value after ACTION completion

Examples:

- Implementation checklists and schedules
- ACTION-specific design worksheets
- Progress tracking documents
- Temporary code experiments
- Research notes specific to the ACTION
- Meeting notes about the ACTION implementation
- Implementation challenges and solutions

### 2. Product Documentation (/documentation/[CATEGORY]/)

Documentation that belongs in the main documentation directory has the following characteristics:

- **Enduring relevance**: Useful beyond the completion of any ACTION
- **Product-focused**: Describes the system, features, or architecture
- **Reference value high**: Provides ongoing value to developers and users

Examples:

- API references and specifications
- Architecture diagrams and descriptions
- User guides and tutorials
- Feature specifications
- Code patterns and best practices
- System configuration guides
- Security protocols
- Testing frameworks
- Deployment procedures

## Documentation Migration Process

### When to Migrate Documentation

Documentation should be evaluated for migration:

1. During ACTION completion review
2. When a document's relevance extends beyond its originating ACTION
3. During periodic documentation audits

### Migration Checklist

When migrating a document from an ACTION to main documentation:

1. **Evaluate document relevance**
   - Determine if the document has enduring value
   - Identify the appropriate category in main documentation

2. **Prepare the document for migration**
   - Update any ACTION-specific terminology to system-wide terminology
   - Ensure the document is complete and accurate
   - Add metadata including originating ACTION and creation/update dates

3. **Place in correct location**
   - Move the document to the appropriate subdirectory in /documentation/
   - Update any references to the document in other files
   - Remove the original document from the ACTION directory

4. **Update documentation indexes**
   - Add the document to relevant documentation indexes
   - Update the ACTION completion record to note the migrated document

## Directory Structure Requirements

### ACTION Documentation Structure

Every ACTION directory must follow this structure for documentation:

```
.aicheck/actions/[ACTION_NAME]/
├── [ACTION_NAME]-PLAN.md           # Required
├── [ACTION_NAME]-IMPLEMENTATION.md # Required for ActiveAction
├── supporting_docs/                # Required directory
│   ├── process_documents/          # Optional subdirectory
│   ├── design_documents/           # Optional subdirectory
│   ├── research_notes/             # Optional subdirectory
│   └── [other documentation]       # As needed
└── ...
```

### Main Documentation Structure

```
/documentation/
├── technical/        # System architecture, design patterns, etc.
├── public/           # User-facing documentation
├── planning/         # Strategic planning documents
├── architecture/     # System design documents
├── implementation/   # Implementation details with enduring value
├── deliverables/     # Completion records, deliverables documentation
└── ...
```

## Document Classification Guidelines

When determining where a document belongs, ask the following questions:

1. Will this document be relevant after the ACTION is completed?
2. Does this document describe a core component of the system?
3. Would this document be useful to someone not involved in the ACTION?
4. Does this document establish standards or patterns to be followed?

If the answer to any of these questions is "yes," the document likely belongs in the main documentation directory.

## Implementation Timeline

This policy will be implemented according to the DocumentationReorganization ACTION plan:

1. **Immediate (Week 1)**: Update RULES.md and create supporting policy documents
2. **Short-term (Weeks 2-3)**: Audit and reorganize existing documentation
3. **Medium-term (Week 4)**: Implement new processes and training

## Responsibility and Enforcement

The documentation organization policy will be enforced through:

1. **ACTION Completion Reviews**: Documentation organization will be checked
2. **Regular Documentation Audits**: Periodic reviews of documentation placement
3. **Development Team Training**: All team members will be trained on the policy
4. **Automated Checks**: Where possible, automated checks will verify compliance

## Conclusion

Proper documentation organization is essential for maintaining an efficient, scalable system. By clearly separating process-focused ACTION documentation from enduring product documentation, we ensure that valuable information is preserved while avoiding clutter from temporary artifacts.
