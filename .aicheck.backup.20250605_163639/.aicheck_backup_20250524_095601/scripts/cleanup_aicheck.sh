#!/bin/bash
# AICheck cleanup script
# This script cleans up duplicate AICheck installations and ensures correct configuration

set -e  # Exit on error

echo "=== AICheck Cleanup Utility ==="
echo "This script will clean up duplicate AICheck installations and ensure correct configuration."
echo ""

# 1. Ensure core scripts exist in .aicheck
echo "Step 1: Ensuring core scripts exist in .aicheck..."
mkdir -p .aicheck/scripts

# Copy scripts from AICheck if they exist but not in .aicheck
if [ -d "AICheck/.aicheck/scripts" ] && [ ! -f ".aicheck/scripts/common.sh" ]; then
    echo "  - Copying scripts from AICheck/.aicheck/scripts..."
    cp -r AICheck/.aicheck/scripts/* .aicheck/scripts/
fi

# 2. Check current action status
echo "Step 2: Checking current action status..."
CURRENT_ACTION=$(cat .aicheck/current_action 2>/dev/null || echo "None")
echo "  - Current action: $CURRENT_ACTION"

# 3. Merge action directories if needed
echo "Step 3: Merging action information..."
if [ -d "AICheck/.aicheck/actions" ]; then
    mkdir -p .aicheck/actions

    # For each action in AICheck, copy if not exists
    for ACTION_DIR in AICheck/.aicheck/actions/*; do
        ACTION_NAME=$(basename "$ACTION_DIR")
        if [ ! -d ".aicheck/actions/$ACTION_NAME" ]; then
            echo "  - Copying action '$ACTION_NAME' from AICheck..."
            cp -r "$ACTION_DIR" .aicheck/actions/
        else
            echo "  - Action '$ACTION_NAME' already exists in main .aicheck"
        fi
    done
fi

# 4. Ensure templates are available
echo "Step 4: Ensuring templates are available..."
mkdir -p .aicheck/templates
if [ -d "AICheck/.aicheck/templates" ] && [ "$(ls -A .aicheck/templates 2>/dev/null | wc -l)" -eq 0 ]; then
    echo "  - Copying templates from AICheck..."
    cp -r AICheck/.aicheck/templates/* .aicheck/templates/
fi

# 5. Copy any useful documentation
echo "Step 5: Copying documentation..."
mkdir -p .aicheck/docs
if [ -d "AICheck/.aicheck/docs" ]; then
    cp -r AICheck/.aicheck/docs/* .aicheck/docs/ 2>/dev/null || true
fi

# 6. Ensure correct current_action and current_session
echo "Step 6: Setting up current action and session..."

# Create a new session if needed
if [ ! -f ".aicheck/current_session" ]; then
    SESSION_ID="session_$(date +%Y%m%d%H%M%S)"
    echo "$SESSION_ID" > .aicheck/current_session
    mkdir -p .aicheck/sessions
    touch ".aicheck/sessions/$SESSION_ID.session"
    echo "  - Created new session: $SESSION_ID"
else
    echo "  - Using existing session: $(cat .aicheck/current_session)"
fi

# 7. Verify ai script exists
echo "Step 7: Verifying ai script..."
if [ ! -f "ai" ] && [ -f "AICheck/ai" ]; then
    echo "  - Copying ai script from AICheck..."
    cp AICheck/ai .
    chmod +x ai
fi

# 8. Consolidate rules and documentation
echo "Step 8: Consolidating rules and documentation..."
if [ ! -f "RULES.md" ] && [ -f "AICheck/RULES.md" ]; then
    echo "  - Copying RULES.md from AICheck..."
    cp AICheck/RULES.md .
fi

# 9. Create archive of old installations (but don't delete yet)
echo "Step 9: Creating archive of old installations..."
mkdir -p backups
BACKUP_DATE=$(date +%Y%m%d%H%M%S)

if [ -d "AICheckArchive" ]; then
    echo "  - Creating backup of AICheckArchive..."
    tar -czf "backups/AICheckArchive_$BACKUP_DATE.tar.gz" AICheckArchive
fi

if [ -d "AICheckArchjve2" ]; then
    echo "  - Creating backup of AICheckArchjve2..."
    tar -czf "backups/AICheckArchjve2_$BACKUP_DATE.tar.gz" AICheckArchjve2
fi

# 10. Summary
echo ""
echo "=== Cleanup Summary ==="
echo "- Current action: $CURRENT_ACTION"
echo "- Current session: $(cat .aicheck/current_session 2>/dev/null || echo 'None')"
echo "- Backup archives created in backups/ directory"
echo ""
echo "WARNING: This script did NOT delete any directories."
echo "To complete cleanup, run the following commands after verifying everything works:"
echo "  rm -rf AICheckArchive AICheckArchjve2"
echo "  # Only remove AICheck if you're sure all data is migrated:"
echo "  # rm -rf AICheck"
echo ""
echo "Cleanup completed. Run './ai status' to verify configuration."
