# UltraAI Documentation Organization Guide

This document clarifies the organization of the UltraAI Framework documentation and establishes clear guidelines for where different types of content should be placed.

## Documentation Categories

The UltraAI documentation is organized into the following key categories:

| Category | Purpose | Audience | Content Types |
|----------|---------|----------|--------------|
| Guidelines | Project standards and principles | Contributors | Standards, conventions, principles |
| Instructions | How-to guides and procedures | Implementers | Step-by-step guides, troubleshooting |
| API | Interface specifications | Integrators | Endpoints, request/response formats |
| Implementation | Technical specifications | Developers | Architecture, data models, algorithms |
| Workflow | Process documentation | All users | Process flows, roles, responsibilities |
| Conceptual | Core concepts and theories | All users | Explanations, rationales, theories |

## Guidelines vs. Instructions

These two categories often cause confusion. Here's how to distinguish between them:

### Guidelines

**Purpose**: Establish standards, principles, and best practices
**Form**: Declarative, principle-based documents
**Examples**:

- Coding standards
- Documentation conventions
- Project organization principles
- Review processes
- Contribution workflows

**When to use**: For documenting standards that should be followed consistently across the project

### Instructions

**Purpose**: Provide specific how-to guidance for completing tasks
**Form**: Procedural, step-by-step documents
**Examples**:

- Troubleshooting guides
- Configuration procedures
- Implementation walkthroughs
- Pattern usage examples
- Feature setup instructions

**When to use**: For documenting specific procedures that users or developers need to follow

## Content Placement Rules

When creating new documentation or migrating existing content, use these rules to determine the appropriate location:

1. **If the document establishes rules or standards** → Place in `guidelines/`
2. **If the document provides step-by-step procedures** → Place in `instructions/`
3. **If the document specifies interfaces** → Place in `api/`
4. **If the document details implementation** → Place in `implementation/`
5. **If the document describes processes** → Place in `workflow/`
6. **If the document explains concepts** → Place in `logic/`

## Examples

| Document Type | Placement | Rationale |
|---------------|-----------|-----------|
| Coding Standards | `guidelines/` | Establishes rules for code |
| Troubleshooting Guide | `instructions/` | Provides steps to resolve issues |
| API Endpoint Spec | `api/` | Documents interface |
| Component Architecture | `implementation/` | Details technical implementation |
| Analysis Process | `workflow/` | Describes a complete process |
| Pattern Theory | `logic/` | Explains conceptual foundation |

## Documentation Prefixes

To further clarify document types, we recommend using these prefixes in filenames:

- `GUIDE_` - For guidelines documents
- `HOWTO_` - For instructional documents
- `API_` - For API specifications
- `SPEC_` - For implementation specifications
- `WORKFLOW_` - For process documentation
- `CONCEPT_` - For conceptual documentation

## Migration Approach

When migrating existing documentation:

1. Review the document's primary purpose
2. Identify the appropriate category based on the rules above
3. Apply appropriate prefix to the filename
4. Move to appropriate directory
5. Update any cross-references

## Conclusion

Following these organization principles will ensure that documentation is easy to find, maintain, and use. If you're unsure where a document belongs, consider its primary purpose and audience to determine the most appropriate category.
