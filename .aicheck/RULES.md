# ICheck Rules

This document serves as the controlling reference for all work managed by the AICheck system which applies to this PROJECT.

## Core Principles

### 1. Defining the Work

The PROJECT's objective is to create a PROGRAM with specific functions and qualities that intentionally benefit humanity in unique ways. PROGRAMS are built through interrelated ACTIONS performed by EDITORS. Each ACTION is a sub-objective that contributes to program functionality.

An EDITOR's work has value when it progresses an ACTION toward completion. Work that doesn't contribute to an ACTION has negative value as it wastes time or may undo progress. Greater efficiency (i.e., producing quality work at a greater pace than one's peers) increases an EDITOR's value.

EDITORS who understand how their work contributes to completing their current ACTION and how that ACTION builds toward PROGRAM completion will hold greater value to the PROJECT's ultimate success than an EDITOR who views their work narrowly.

These logical relationships are the basis of the AICheck system for EDITORS and these controlling RULES.

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

### 3. Development Guidelines

- Focus on one ActiveAction at a time; complete or pause before switching
- Follow the AICheck directory structure and naming conventions
- Update action status and document progress regularly
- Follow language-specific best practices and maintain code quality standards

## Action Management

### AI Editor Scope

AI editors may implement without approval:

- Code implementing the ActiveAction plan
- Documentation updates for ActiveAction
- Bug fixes and tests within ActiveAction scope
- Refactoring within ActiveAction scope

The following ALWAYS require human manager approval:

- Changing the ActiveAction
- Creating a new Action
- Making substantive changes to any Action
- Modifying any Action Plan
- Creating or modifying Templates

### Action Documentation Requirements

- Action plan (PLAN.md)
- Supporting documentation
- Status updates (Not Started, ActiveAction, Completed, Blocked, On Hold)

## Directory Structure

### Core Project Structure

```
/
├── documentation/     # Centralized documentation
│   ├── technical/     # Technical implementation details
│   ├── public/        # User-facing documentation
│   ├── planning/      # Strategic planning documents
│   ├── vision/        # High-level vision documents
│   ├── architecture/  # System design documents
│   ├── research/      # Background research
│   ├── operations/    # Deployment & operations
│   ├── implementation/# Implementation details
│   ├── deliverables/  # Completion records
│   ├── status_updates/# Periodic status reports
│   ├── legal/         # Legal documents
│   └── configuration/ # Configuration documentation
├── src/               # Source code
├── frontend/          # Frontend code
│   └── demos/         # Frontend demos
├── backend/           # Backend services
├── data/              # Data resources
│   └── images/        # Image resources
├── scripts/           # Utility scripts
├── tests/             # Test suites
└── .aicheck/          # AICheck system
    ├── actions/       # Action-specific directories
    │   └── [ACTION_NAME]/
    │       ├── [ACTION_NAME]-PLAN.md
    │       └── supporting_docs/
    ├── cursor/        # Cursor-specific configurations
    ├── docs/          # AICheck documentation
    ├── hooks/         # Git hooks
    ├── insights/      # AI-generated insights
    ├── sessions/      # AI session data
    ├── scripts/       # AICheck scripts
    └── templates/     # Template files
```

## Critical Files

- RULES.md: This document (controlling reference)
- .aicheck/docs/actions_index.md: Action tracking
- .aicheck/current_action: ActiveAction tracking
- .aicheck/current_session: Current session tracking
- documentation/README.md: Documentation organization reference

## Workflow Requirements

- Start sessions with `./ai start` and end with meaningful summaries
- Check status with `./ai status` and generate prompts with `./ai prompt`
- Create, update, and audit Actions with appropriate commands
- Verify context and compliance before starting work

## Style Requirements

### Documentation Style

- Use ATX-style headers, fenced code blocks with language specification, bullet points for lists, and bold for emphasis
- Use PascalCase for Action names, kebab-case for file names, .md extension for documentation, and -PLAN.md suffix for action plans
- Follow language-specific style guides with consistent indentation (4 spaces)
- Use lowercase for directory names, maintain descriptive names and consistent organization
- Documentation should be organized according to the structure defined in documentation/README.md
- Technical implementation details should be separate from user-facing documentation
- Configuration files should be documented in documentation/configuration/
- Each project component should have appropriate documentation in its respective documentation category

### Commit and Status Practices

- Write commit messages in present tense starting with a verb, under 50 characters, including action reference
- Use predefined status values with progress percentage, document blockers clearly, and update timestamps
- Create clear error messages with error codes, resolution steps, and appropriate logging

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

## Script Usage

- Project scripts are located in:
  - Root directory for critical system scripts
  - scripts/ for utility scripts
  - .aicheck/scripts/ for AICheck-specific scripts
- Scripts should use relative paths when possible to maintain portability
- Scripts should be tested after any relocation or path changes

## Last Updated

Date: 2025-05-03
Version: 1.2.0

## Test Rule

This is a test rule added to verify critical file change approvals.
