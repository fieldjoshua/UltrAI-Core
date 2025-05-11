# UltraAI Actions Index

This directory contains automated tools for maintaining an up-to-date HTML actions index.

## 📄 Files in this directory

- **index.html**: The main actions index page (automatically generated)
- **update_index.py**: Python script to scan the actions directory and generate the HTML index
- **watch_and_update.sh**: Shell script to watch for file changes and update the index in real-time
- **setup_git_hook.sh**: Script to install Git hooks that automatically update the index during Git operations

## 🚀 How to use

### Automatic updates

The actions index is designed to update automatically when changes to action files occur:

1. **Git Hook Method** (recommended):

   ```bash
   # Install Git hooks (one-time setup)
   ./.aicheck/actions/setup_git_hook.sh
   ```

   This will install Git hooks that update the index whenever:

   - You commit changes to action files
   - You pull/merge changes that include action file modifications

2. **File Watcher Method** (for live development):
   ```bash
   # Start the file watcher (keeps running until Ctrl+C)
   ./.aicheck/actions/watch_and_update.sh
   ```
   This continuously watches for changes to action files and updates the index in real-time.

### Manual updates

You can also update the index manually:

```bash
# Update the index once
python3 ./.aicheck/actions/update_index.py
```

## 📋 How it works

1. The `update_index.py` script:

   - Scans the actions directory structure
   - Identifies completed, in-progress, planning, and pending actions
   - Extracts keywords from action files
   - Creates a structured HTML index with filterable categories

2. The HTML index:
   - Organizes actions by status (completed, in-progress, planning)
   - Provides search functionality to filter actions
   - Shows key links for each action
   - Displays statistics about the project's progress

## 🔄 Maintenance

The index is self-maintaining as long as the Git hooks or file watcher are used. If the structure of action directories changes significantly, you may need to update the `update_index.py` script.
