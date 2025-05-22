# Action Index Automation - Usage Guide

This guide explains how to use and maintain the Action Index Automation system.

## Installation

### Git Hook Method (Recommended)

For automatic updates during normal Git workflow:

```bash
# Install Git hooks (one-time setup)
./.aicheck/actions/setup_git_hook.sh
```

This will install two Git hooks:

- **post-commit**: Updates the index when you commit changes to action files
- **post-merge**: Updates the index when you pull/merge changes that include action file modifications

These hooks ensure the index is always up-to-date without any manual intervention.

### File Watcher Method (For Active Development)

For real-time updates during development:

```bash
# Start the file watcher (keeps running until Ctrl+C)
./.aicheck/actions/watch_and_update.sh
```

This continuously watches for changes to action files and updates the index in real-time. It's useful when:

- You're creating or modifying multiple action files
- You're reviewing actions and want immediate feedback
- You're not ready to commit changes but want to see the index update

## Manual Updates

You can also update the index manually:

```bash
# Update the index once
python3 ./.aicheck/actions/update_index.py
```

This is useful when:

- You need to regenerate the index after changes
- The automatic updates aren't working for some reason
- You're troubleshooting issues with the index

## Using the HTML Index

The HTML index provides several features:

### Searching for Actions

1. Open the HTML index in any web browser
2. Use the search box at the top to filter actions
3. Results update in real-time as you type
4. Search matches action names, status, and extracted keywords

### Viewing Action Categories

The index organizes actions into key categories:

- **Completed Actions**: Actions marked as completed
- **In Progress Actions**: Actions currently in progress
- **Planning Stage Actions**: Actions in the planning phase
- **All Actions**: Complete list of all actions

Each section shows relevant actions with status indicators and links to documentation.

### Understanding Status Indicators

Actions are color-coded by status:

- **Green**: Completed actions
- **Blue**: In-progress actions
- **Purple**: Planning stage actions
- **Orange**: Pending actions

### Viewing Action Details

Each action card includes:

- Action name
- Status indicator
- Links to relevant documentation (Plan, Completion Report, etc.)

### Project Statistics

The top of the index shows key statistics:

- Number of completed actions
- Number of in-progress actions
- Total number of actions

## Common Questions

### How are action statuses determined?

Action statuses are determined based on file presence:

- **Completed**: Has a `*-COMPLETED.md` file
- **In Progress**: Has progress-related files or implementation files
- **Planning**: Has plan files but no progress/implementation
- **Pending**: Has no plan, progress, or implementation files

### How are keywords extracted?

Keywords are extracted from:

- The action name (split into individual words)
- Headers in plan files (section titles)
- Common terms in action documentation

This improves search relevance and helps find actions by topic.

### How can I add more actions to the index?

Just create new action directories following the standard format:

1. Create a directory in `.aicheck/actions/`
2. Add a plan file (e.g., `ActionName-PLAN.md`)
3. Add supporting documentation as needed

The index will automatically update to include the new action.

## Troubleshooting

### The index isn't updating automatically

1. Check that Git hooks are installed correctly:

   ```bash
   ls -la .git/hooks/post-commit .git/hooks/post-merge
   ```

   If these files don't exist or aren't executable, reinstall using the setup script.

2. Verify the Python script is executable:

   ```bash
   chmod +x .aicheck/actions/update_index.py
   ```

3. Try running the update script manually to check for errors:
   ```bash
   python3 .aicheck/actions/update_index.py
   ```

### The file watcher isn't detecting changes

1. Check if you have the required tools:

   - macOS: `brew install fswatch`
   - Linux: `apt-get install inotify-tools`

2. If tools aren't available, the watcher falls back to polling, which checks every 10 seconds.

3. Verify the path configuration in the watch script.

### Search isn't working in the HTML index

1. Make sure JavaScript is enabled in your browser
2. Try opening the file in a different browser
3. Check for JavaScript errors in the browser console
