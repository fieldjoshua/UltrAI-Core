# Documentation Migration Process

## Overview

This document outlines the official process for migrating documentation from ACTION-specific directories to the main documentation system, ensuring that valuable documentation is preserved while maintaining a well-organized knowledge repository.

## When to Migrate Documentation

Documentation should be migrated in the following circumstances:

1. **ACTION Completion**: During the completion review of an ACTION
2. **VALUE Recognition**: When a document is identified as having enduring value beyond its originating ACTION
3. **Periodic Audit**: During scheduled documentation audits

## Migration Decision Criteria

To determine if a document should be migrated to the main documentation system, evaluate it against these criteria:

| Criteria | Description | Example |
|----------|-------------|---------|
| System Relevance | Document describes core system components or architecture | Component design document, API specification |
| Ongoing Utility | Information useful for ongoing development or maintenance | Configuration guide, troubleshooting procedures |
| Educational Value | Helps new team members understand the system | System overview, architectural principles |
| Standards Establishment | Defines patterns, practices, or standards | Coding standards, design pattern usage |
| Reference Material | Serves as a reference for system operation | API reference, configuration options |

Documents meeting two or more criteria should generally be migrated.

## Migration Process

### 1. Pre-Migration Assessment

- Review all documentation in the ACTION directory
- Evaluate each document against the migration criteria
- Create a migration plan for documents meeting the criteria
- Obtain approval for migration if required

### 2. Document Preparation

- Update content to remove temporary or ACTION-specific information
- Expand abbreviations or terminology that might not be understood outside the ACTION context
- Verify all information is current and accurate
- Add appropriate metadata (creation date, migration date, originating ACTION)

### 3. Migration Execution

- Copy the document to the appropriate category in the main documentation directory
- Update document name if needed to follow naming conventions
- Update internal links and references
- Add to appropriate index files or documentation registry
- Add a migration notice to the original file or remove it if redundant

### 4. Post-Migration Verification

- Verify the document displays correctly in its new location
- Test all links and ensure all referenced assets are accessible
- Update the documentation migration log
- Update the ACTION completion record with migration notes
- Notify the team of the new documentation location

## Documentation Categories

When migrating documents, place them in the most appropriate category:

| Category | Purpose | Example Documents |
|----------|---------|-------------------|
| technical/ | Implementation details and technical specifications | API documentation, database schemas |
| architecture/ | System design and structure | Component diagrams, design decisions |
| public/ | User-facing documentation | User guides, feature documentation |
| planning/ | Strategic and long-term planning | Roadmaps, strategy documents |
| operations/ | Deployment and system operation | Deployment guides, monitoring setup |
| implementation/ | Specific implementation details with enduring value | Algorithm implementations, optimization techniques |

## Quality Standards for Migrated Documentation

All migrated documentation must meet these minimum standards:

1. **Complete**: Contains all necessary information without relying on ACTION context
2. **Accurate**: Reflects the current state of the system
3. **Well-Structured**: Follows standard document structure with clear headings
4. **Properly Formatted**: Uses correct Markdown formatting throughout
5. **Well-Named**: Has a clear, descriptive filename that indicates content

## Tools and Templates

### Migration Checklist

Use the [Documentation Migration Checklist](/.aicheck/actions/DocumentationReorganization/supporting_docs/Documentation_Migration_Checklist.md) for each document being migrated.

### Documentation Registry

Record all migrations in the [Documentation Migration Registry](documentation/technical/documentation_registry.md).

## Governance

The documentation migration process is governed by:

- The Documentation Standards Committee
- The ACTION completion review process
- Regular documentation audits

## Related Documents

- [Documentation Organization Policy](/.aicheck/actions/DocumentationReorganization/supporting_docs/Documentation_Organization_Policy.md)
- [RULES.md](/.aicheck/RULES.md)
