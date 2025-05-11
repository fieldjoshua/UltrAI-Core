#!/bin/bash

# setup_git_hook.sh
# Script to install a Git hook that updates the actions index automatically

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"
INDEX_GENERATOR="$SCRIPT_DIR/update_index.py"

if [ -z "$REPO_ROOT" ]; then
    echo "Error: Could not find Git repository root."
    exit 1
fi

# Make sure the Python script is executable
chmod +x "$INDEX_GENERATOR"

# Create the hooks directory if it doesn't exist
mkdir -p "$REPO_ROOT/.git/hooks"

# Create post-commit hook
POST_COMMIT_HOOK="$REPO_ROOT/.git/hooks/post-commit"
cat > "$POST_COMMIT_HOOK" << 'EOF'
#!/bin/bash

# Get the repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"
ACTIONS_DIR="$REPO_ROOT/.aicheck/actions"
INDEX_GENERATOR="$ACTIONS_DIR/update_index.py"

# Check if any .md files in the actions directory were changed in the last commit
if git diff-tree --no-commit-id --name-only -r HEAD | grep -q "\.aicheck/actions/.*\.md\|\.aicheck/actions/.*PLAN\|\.aicheck/actions/.*COMPLETED"; then
    echo "Actions files changed. Updating actions index..."
    python3 "$INDEX_GENERATOR"

    # If the index.html file changed, stage it
    if git status --porcelain | grep -q "\.aicheck/actions/index.html"; then
        git add "$ACTIONS_DIR/index.html"
        git commit --amend --no-edit
        echo "Actions index updated and added to the commit."
    else
        echo "No changes to actions index."
    fi
fi
EOF

# Make the hook executable
chmod +x "$POST_COMMIT_HOOK"

# Create post-merge hook (for pulls)
POST_MERGE_HOOK="$REPO_ROOT/.git/hooks/post-merge"
cat > "$POST_MERGE_HOOK" << 'EOF'
#!/bin/bash

# Get the repository root
REPO_ROOT="$(git rev-parse --show-toplevel)"
ACTIONS_DIR="$REPO_ROOT/.aicheck/actions"
INDEX_GENERATOR="$ACTIONS_DIR/update_index.py"

# Check if any .md files in the actions directory were changed
if git diff-tree -r --name-only ORIG_HEAD HEAD | grep -q "\.aicheck/actions/.*\.md\|\.aicheck/actions/.*PLAN\|\.aicheck/actions/.*COMPLETED"; then
    echo "Actions files changed. Updating actions index..."
    python3 "$INDEX_GENERATOR"
fi
EOF

# Make the hook executable
chmod +x "$POST_MERGE_HOOK"

echo "Git hooks installed successfully!"
echo ""
echo "The actions index will now automatically update when:"
echo "- You commit changes to action MD files"
echo "- You pull/merge changes that affect action MD files"
echo ""
echo "You can also manually update the index by running:"
echo "python3 $INDEX_GENERATOR"
echo ""
echo "To watch for file changes in real-time, run:"
echo "$SCRIPT_DIR/watch_and_update.sh"
