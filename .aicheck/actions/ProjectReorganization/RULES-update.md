# RULES.md Update Recommendations

The following changes should be made to RULES.md to reflect the new project organization structure.

## Directory Structure Update

Replace the current Directory Structure section with:

```
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
    │       └── [ACTION_NAME]-PLAN.md
    ├── cursor/        # Cursor-specific configurations
    ├── indexing/      # Action indexing and tracking
    │   └── actions_index.md # Action tracking
    ├── hooks/         # Git hooks
    ├── insights/      # AI-generated insights
    ├── sessions/      # AI session data
    ├── scripts/       # AICheck scripts
    └── templates/     # Template files

```

## Critical Files Update

Update the Critical Files section to include:

```

## Critical Files

- RULES.md: This document (controlling reference)
- .aicheck/indexing/actions_index.md: Action tracking
- .aicheck/current_action: ActiveAction tracking
- .aicheck/current_session: Current session tracking
- documentation/README.md: Documentation organization reference

```

## Action Documentation Management

Add a new section on Action Documentation Management:

```

## Action Documentation Management

- Action directories (.aicheck/actions/[ACTION_NAME]/) must contain ONLY:
  - [ACTION_NAME]-PLAN.md: The action plan
  - status.md: Current status of the action
  - progress.md: Progress percentage tracking

- All supporting documentation MUST be placed in the appropriate category
  under /documentation/ directory.

- When documentation relates to a specific action, use file naming that references
  the action: [ACTION_NAME]-[DOCUMENT_TYPE].md

- Editors MUST NOT attempt to save supporting documentation in action directories.
  The system includes validation hooks that will reject such changes.

- When referencing action-specific documentation in a PLAN.md file, use relative
  links to the appropriate files in the /documentation/ directory.

```

## Documentation Style Update

Add the following to the Documentation Style section:

```

- Documentation should be organized according to the structure defined in documentation/README.md
- Technical implementation details should be separate from user-facing documentation
- Configuration files should be documented in documentation/configuration/
- Each project component should have appropriate documentation in its respective documentation category
- Action-specific supporting documentation should be placed in the appropriate category under /documentation

```

## Script Usage Update

Add a new section:

```

## Script Usage

- Project scripts are located in:
  - Root directory for critical system scripts
  - scripts/ for utility scripts
  - .aicheck/scripts/ for AICheck-specific scripts
- Scripts should use relative paths when possible to maintain portability
- Scripts should be tested after any relocation or path changes

```

## Version Update

Update the version number:

```

## Last Updated

Date: $(date +"%Y-%m-%d")
Version: 1.1.0

```

## Implementation Notes

These changes should be carefully reviewed before implementation to ensure they align with the project's overall direction and do not conflict with existing workflows. The new documentation structure aims to improve organization while maintaining compatibility with existing systems.
