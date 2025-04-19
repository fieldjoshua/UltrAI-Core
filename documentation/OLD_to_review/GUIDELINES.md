# UltraAI Documentation Guidelines

This document establishes the comprehensive standards and rules for all documentation in the UltraAI Framework. It serves as the authoritative reference for how documentation should be structured, organized, formatted, and maintained.

## Documentation Principles

1. **Documentation-First Development**:
   - Documentation precedes implementation
   - Code changes must follow documented patterns
   - Documentation is the single source of truth
   - All features must be documented before implementation

2. **Two-Level Structure**:
   - Root level: only broad, controlling documents (README, GUIDELINES, PLANS_INDEX)
   - Plan level: all documentation related to specific features/components

3. **Plan-Centric Organization**:
   - All documentation is organized by implementation plans
   - Each plan contains all related technical and process documentation
   - Active plans stay in `plans/`
   - Completed plans move to `archive/`

## Required Documents

### Root Level

| Document | Purpose |
|----------|---------|
| README.md | Project overview and introduction |
| GUIDELINES.md | This document - rules for documentation |
| PLANS_INDEX.md | Dashboard of all active plans |
| templates/ | Standard document templates |

### Plan Level

Each plan directory must contain:

| Document | Purpose |
|----------|---------|
| PLAN.md | The plan itself with timeline, owner, and status |
| Technical documentation | Specifications, APIs, architecture |
| Process documentation | Workflows, procedures, guides |

## Documentation Format Standards

### Markdown Conventions

- **Filenames**: ALL_CAPS with underscores
- **Headers**: Start at H1 (#), section headers use H2 (##)
- **Lists**: Use - for bullet points, numbered lists for sequences
- **Code**: Use triple backticks with language identifier ```python
- **Links**: Always use relative links: `[Link Text](relative/path/to/file.md)`
- **Tables**: Use standard Markdown tables with headers
- **Images**: Include alt text: `![Alt text](path/to/image.png)`
- **Emphasis**: Use **bold** for important points, *italic* for emphasis

### Document Structure

Every document must include:

1. **Title**: Clear H1 title at the top
2. **Overview**: Brief introduction explaining purpose (1-2 paragraphs)
3. **Main Content**: Organized into logical sections with H2 headers
4. **Cross-References**: Links to related documentation
5. **Dates**: Last updated date at the bottom

## Appendix: Document Templates

The following templates are provided as appendices to these guidelines. Each template implements the standards defined in this document and should be used to ensure compliance with documentation requirements:

| Template | Purpose | When to Use |
|----------|---------|------------|
| [CONCEPT_TEMPLATE.md](templates/CONCEPT_TEMPLATE.md) | Core concepts and theories | When explaining foundational ideas |
| [GUIDE_TEMPLATE.md](templates/GUIDE_TEMPLATE.md) | How-to instructions | When providing step-by-step guidance |
| [COMPARISON_TEMPLATE.md](templates/COMPARISON_TEMPLATE.md) | Option evaluation | When comparing multiple approaches |
| [DECISION_RECORD_TEMPLATE.md](templates/DECISION_RECORD_TEMPLATE.md) | Decision documentation | When recording important decisions |
| [RESEARCH_FINDINGS_TEMPLATE.md](templates/RESEARCH_FINDINGS_TEMPLATE.md) | Research outcomes | When documenting investigation results |
| [IMPLEMENTATION_PLAN_TEMPLATE.md](templates/IMPLEMENTATION_PLAN_TEMPLATE.md) | Feature planning | When planning implementation of features |
| [TECHNICAL_SPEC_TEMPLATE.md](templates/TECHNICAL_SPEC_TEMPLATE.md) | Technical details | When specifying technical components |
| [WORKFLOW_TEMPLATE.md](templates/WORKFLOW_TEMPLATE.md) | Process documentation | When describing multi-step processes |
| [TESTING_PLAN_TEMPLATE.md](templates/TESTING_PLAN_TEMPLATE.md) | Testing approach | When planning test strategies |

These templates should be considered extensions of these guidelines and the definitive implementation of the standards described herein. Always start with the appropriate template when creating new documentation.

## Plan Template

Each plan document must follow this structure:

```markdown
# Plan: [Feature/Component Name]

## Overview
[Brief description of what this plan addresses]

## Status
- **Current Phase**: [Planning/Implementation/Testing/Complete]
- **Progress**: [0-100%]
- **Owner**: [Name or team]
- **Started**: [YYYY-MM-DD]
- **Target Completion**: [YYYY-MM-DD]

## Objectives
- [Clear, measurable objective 1]
- [Clear, measurable objective 2]

## Implementation Steps
1. [First step with details]
2. [Second step with details]

## Documentation Components
- [List of documentation files included in this plan]

## Related Plans
- [Links to related plans]

## Last Updated: YYYY-MM-DD
```

## Documentation Categories and Placement

When creating or modifying documentation, determine the appropriate location:

### Conceptual Documentation

- **Purpose**: Explains the "why" behind the system
- **Location**: Inside relevant plan directory
- **Template**: See Appendix: [CONCEPT_TEMPLATE.md](templates/CONCEPT_TEMPLATE.md)
- **Example**: Core architecture concepts, methodology explanations

### Instructional Documentation

- **Purpose**: Provides step-by-step guidance
- **Location**: Inside relevant plan directory
- **Template**: See Appendix: [GUIDE_TEMPLATE.md](templates/GUIDE_TEMPLATE.md)
- **Example**: How to use features, configuration procedures

### Technical Documentation

- **Purpose**: Details implementation specifics
- **Location**: Inside relevant plan directory
- **Template**: See Appendix: [TECHNICAL_SPEC_TEMPLATE.md](templates/TECHNICAL_SPEC_TEMPLATE.md)
- **Example**: API specifications, data models, component architecture

### Process Documentation

- **Purpose**: Describes workflows and procedures
- **Location**: Inside relevant plan directory
- **Template**: See Appendix: [WORKFLOW_TEMPLATE.md](templates/WORKFLOW_TEMPLATE.md)
- **Example**: Analysis workflows, review processes

## Status Tracking

The PLANS_INDEX.md must be updated:

1. Whenever a plan is created, modified, or completed
2. With accurate status information for each plan
3. With links to all plan documents
4. With dates of last activity

## Cross-Referencing Rules

1. All documents must link to related documents
2. Links should use relative paths from the repository root
3. The specific section should be linked when possible
4. External references must include the date accessed

## Review Process

All documentation must be reviewed:

1. When first created
2. When substantially updated
3. When the related implementation is complete
4. During periodic documentation audits

### Review Checklist

Before submitting documentation:

- [ ] Document follows the prescribed structure
- [ ] All cross-references are valid and use relative links
- [ ] Code examples are accurate and follow project conventions
- [ ] Terminology is consistent with other documentation
- [ ] Document is in the correct location according to its type
- [ ] Document includes links to related documentation
- [ ] Spelling and grammar have been checked
- [ ] Document is up-to-date with current implementation

## Git Commit Standards

When committing documentation changes:

1. Use the prefix `docs:` in commit messages
2. Include the document name being modified
3. Briefly describe the nature of the change
4. Link to related issues or PRs

Example: `docs(ANALYSIS_API_PLAN): Update timeline and add architecture diagram`

## Writing Style Guidelines

1. **Clarity**: Use plain language and precise terminology
2. **Consistency**: Maintain consistent terminology and formatting
3. **Completeness**: Cover all necessary information without redundancy
4. **Accessibility**: Use descriptive link text and alt text for images
5. **Relevance**: Keep documentation focused on its specific purpose
6. **Maintenance**: Include review dates and update history

## Working with AI Assistants

When using AI assistants with documentation:

1. **Share Context**: Provide AI with links to relevant existing documentation first
2. **Documentation First**: Ask AI to draft documentation before implementing code
3. **Template Adherence**: Ensure AI uses the appropriate template from the Appendix
4. **Cross-Reference Check**: Have AI verify all cross-references are correct
5. **Standard Validation**: Confirm AI output follows these guidelines

Example prompt: "I need to document [feature]. Please follow the template in the appendix to our documentation guidelines (templates/[TEMPLATE].md) and ensure adherence to our documentation standards."

## Migration and Consolidation

As we transition to this structure:

1. Existing documentation should be moved into appropriate plans
2. Documentation not related to specific plans should be archived
3. The PLANS_INDEX.md should track migration progress
4. Cross-references should be updated to reflect new locations

## Conclusion

Following these guidelines ensures our documentation remains the single source of truth for UltraAI. All contributors are expected to adhere to these standards.

## Last Updated: 2023-08-06
