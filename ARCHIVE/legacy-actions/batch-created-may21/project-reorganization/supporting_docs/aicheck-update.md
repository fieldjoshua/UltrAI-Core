# .aicheck System Update Recommendations

This document outlines the necessary changes to the .aicheck system to align with the new project organization.

## Script Path Updates

### Issue

The current AICheck scripts (`ai` and `cleanup_aicheck.sh`) contain hardcoded paths that reference `.aicheck/scripts/`, making them difficult to relocate without breaking functionality.

### Recommended Changes

1. Update the `ai` script to use relative path detection:

```bash
#!/bin/bash

# Get the absolute path to the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Determine .aicheck location relative to script location
if [[ "$SCRIPT_DIR" == *".aicheck/scripts" ]]; then
    # Script is already in .aicheck/scripts
    AICHECK_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
else
    # Script is likely in root, assume .aicheck is there
    AICHECK_DIR="$ROOT_DIR/.aicheck"
fi

# Source component scripts using determined paths
source "$AICHECK_DIR/scripts/common.sh"
source "$AICHECK_DIR/scripts/session.sh"
source "$AICHECK_DIR/scripts/action.sh"
source "$AICHECK_DIR/scripts/security_utils.sh"

# ... rest of script ...
```

2. Update all AICheck scripts to follow this pattern, enabling them to work regardless of their location in the repository.

3. Create proper symlinks once path handling is corrected:

```bash
ln -sf .aicheck/scripts/ai ./ai
ln -sf .aicheck/scripts/cleanup_aicheck.sh ./cleanup_aicheck.sh
```

## .aicheck Directory Structure

The `.aicheck` directory should be updated to follow this structure:

```
.aicheck/
├── actions/           # Action-specific directories
│   └── [ACTION_NAME]/
│       └── [ACTION_NAME]-PLAN.md  # Action plan only
├── cursor/            # Cursor-specific configurations
├── indexing/          # Action indexing and tracking
│   ├── actions_index.md     # Action tracking
│   └── aicheck_usage.md     # AICheck usage reference
├── hooks/             # Git hooks
│   ├── pre-commit     # Pre-commit hook
│   └── action_doc_validator.sh # Action documentation validator
├── insights/          # AI-generated insights
├── sessions/          # AI session data
├── scripts/           # AICheck scripts with updated paths
│   ├── ai             # Main AICheck interface
│   ├── cleanup_aicheck.sh # Cleanup script
│   ├── common.sh      # Common functions
│   ├── session.sh     # Session management
│   ├── action.sh      # Action management
│   └── security_utils.sh # Security utilities
└── templates/         # Template files
```

## Action Directory Hook Implementation

A key aspect of the new organization is ensuring that only PLAN.md files are saved in Action directories, with all supporting documentation moved to the central `/documentation` directory.

### Git Hook Implementation

1. Create an `action_doc_validator.sh` script in `.aicheck/hooks/` that enforces this policy:

```bash
#!/bin/bash

# Validate that only allowed files are being committed to action directories
validate_action_files() {
    # Get all staged files
    staged_files=$(git diff --cached --name-only)

    # Check each staged file
    for file in $staged_files; do
        # If file is in an action directory
        if [[ $file =~ ^\.aicheck/actions/[^/]+/(.+)$ ]]; then
            filename="${BASH_REMATCH[1]}"
            action_name=$(echo $file | cut -d'/' -f3)

            # Allow only these files in action directories
            if [[ "$filename" == "$action_name-PLAN.md" ||
                  "$filename" == "status.md" ||
                  "$filename" == "progress.md" ]]; then
                continue
            else
                echo "ERROR: Only PLAN.md, status.md, and progress.md files are allowed in action directories."
                echo "Please move supporting documentation to the appropriate category in /documentation/"
                echo "Attempted to commit: $file"
                exit 1
            fi
        fi
    done

    return 0
}

# Run the validation
validate_action_files
```

2. Add this script to the pre-commit hook in `.aicheck/hooks/pre-commit`:

```bash
#!/bin/bash

# Run the action documentation validator
if ! bash .aicheck/hooks/action_doc_validator.sh; then
    exit 1
fi

# Continue with other pre-commit checks
# ...
```

3. Ensure the hook is activated in the git configuration:

```bash
git config core.hooksPath .aicheck/hooks
```

### Automated Documentation Guidance

Update the `action.sh` script to:

1. No longer create `supporting_docs` directories
2. Provide guidance when creating new actions:

```bash
# Add to action_create function
echo "NOTE: All supporting documentation should be placed in the appropriate"
echo "category under /documentation/, not in the action directory."
echo "Only PLAN.md, status.md, and progress.md files should exist in action directories."
```

### Editor Instruction Updates

Update the prompt and editor instruction generation to specifically mention:

```
IMPORTANT: All supporting documentation must be placed in the appropriate
category under /documentation/, not in the Action directory. Action directories
should contain only the PLAN.md file and status tracking files.
```

## Documentation Updates

Update AICheck documentation to:

1. Reference the new centralized documentation structure in `/documentation/`
2. Reference the updated paths for scripts
3. Move all supporting documentation out of action directories into the appropriate `/documentation/` subdirectories
4. Update all references to `.aicheck/docs/` to use `.aicheck/indexing/` instead

Create a new file `.aicheck/indexing/documentation_guidelines.md` that links to the main documentation structure and explains how AICheck-specific documentation relates to the overall project documentation.

## Path References to Update

The following scripts and files need to be updated to reference the new structure:

1. `ai` script - Replace references to `.aicheck/docs/` with `.aicheck/indexing/`
2. `action.sh` - Update path handling to no longer create supporting_docs directories
3. Templates - Update any templates that reference supporting_docs

## RULES.md Updates

In addition to the structure changes, the following should be added to RULES.md:

```
### Action Documentation Management

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
```

## Testing Process

Before implementing these changes:

1. Create a test branch
2. Implement path detection in scripts
3. Test script functionality from multiple locations
4. Verify all commands work as expected
5. Document any issues encountered

## Migration Approach

The recommended migration approach is:

1. First update all scripts to use relative path detection
2. Move action supporting documentation to respective `/documentation/` directories
3. Create the new `.aicheck/indexing/` directory and move files from `.aicheck/docs/`
4. Update all scripts to reference `.aicheck/indexing/` instead of `.aicheck/docs/`
5. Test all functionality thoroughly before finalizing changes

## Backward Compatibility

To maintain backward compatibility:

1. Keep symlinks in original locations
2. Consider creating a temporary symlink from `.aicheck/docs` to `.aicheck/indexing`
3. Add deprecation notices for old approaches that will eventually be removed
4. Update any CI/CD pipelines or automation that might rely on specific paths
