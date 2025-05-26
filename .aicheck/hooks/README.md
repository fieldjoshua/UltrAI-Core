# AICheck Git Hooks

This directory contains git hooks that help enforce AICheck workflow requirements, particularly around action completion.

## Available Hooks

### post-action-complete.sh
A comprehensive check that runs when an action is marked complete. It verifies:
- Documentation migration requirements
- Actions index updates
- ACTION_TIMELINE.md updates
- Dependency documentation
- Directory organization

### install-hooks.sh
Installation script that sets up all AICheck git hooks in your repository.

## Installation

```bash
# From the project root
.aicheck/hooks/install-hooks.sh
```

This will install:
- **post-commit**: Automatically checks for action completion in commit messages
- **prepare-commit-msg**: Adds reminders about completion requirements
- **pre-push**: (Optional) Vision Guardian IP protection audit

## Usage

### Automatic Checks
When you commit with messages containing "complete", "finished", or "done", the hooks will automatically run completion checks.

### Manual Checks
You can manually verify action completion requirements:

```bash
# Check specific action
.aicheck/hooks/post-action-complete.sh action complete <action-name>

# Check current action
.aicheck/hooks/post-action-complete.sh
```

## Completion Requirements

Per RULES.md Section 6.1, when completing an action:

1. **Migrate Universal Documentation**
   - Review supporting_docs/ for enduring documentation
   - Move to appropriate /documentation/ subdirectories

2. **Update Actions Index**
   - Mark action as Completed in actions_index.md
   - Include completion date

3. **Update Timeline**
   - Add entry to ACTION_TIMELINE.md
   - Include status, philosophy, accomplishments, and impact

4. **Document Dependencies**
   - External: `./aicheck dependency add NAME VERSION JUSTIFICATION`
   - Internal: `./aicheck dependency internal DEP_ACTION ACTION TYPE`

5. **Move to Completed**
   - Move action directory to .aicheck/actions/completed/

## Customization

The hooks are designed to warn but not block by default. To enforce strict compliance:

1. Edit `.aicheck/hooks/post-action-complete.sh`
2. Uncomment `exit 1` at the end to block non-compliant completions

## Troubleshooting

If hooks aren't running:
- Ensure they're executable: `chmod +x .git/hooks/*`
- Check git version: `git --version` (requires 2.9+)
- Verify hook installation: `ls -la .git/hooks/`