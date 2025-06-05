#!/bin/bash

# Enhanced Git Hooks for AICheck
# Provides deployment verification and action completion checks

# This file contains the hook implementations
# They should be installed to .git/hooks/ via install script

# ============= PRE-COMMIT HOOK =============
cat > pre-commit-enhanced << 'PRECOMMIT'
#!/bin/bash

# Enhanced pre-commit hook for AICheck
# Checks deployment verification and action completion requirements

# Colors
RED="\033[0;31m"
YELLOW="\033[0;33m"
GREEN="\033[0;32m"
NC="\033[0m"

# Check if yq is available
HAS_YQ=$(command -v yq >/dev/null 2>&1 && echo "true" || echo "false")

# Function to check if an action is being completed
check_action_completion() {
    local changed_files=$(git diff --cached --name-only)
    
    for file in $changed_files; do
        # Check if status.txt is being changed to Completed
        if [[ "$file" =~ \.aicheck/actions/.*/status\.txt$ ]]; then
            local action_dir=$(dirname "$file")
            local action_name=$(basename "$action_dir")
            
            # Check if status is being changed to Completed
            local new_status=$(git diff --cached "$file" | grep "^+[^+]" | sed 's/^+//')
            if [[ "$new_status" == "Completed" ]]; then
                echo -e "${YELLOW}Action '$action_name' is being marked as completed${NC}"
                
                # Check deployment verification if action.yaml exists
                if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
                    local deploy_required=$(yq '.deployment.required' "$action_dir/action.yaml" 2>/dev/null)
                    local deploy_verified=$(yq '.deployment.environments.production.verified' "$action_dir/action.yaml" 2>/dev/null)
                    
                    if [ "$deploy_required" = "true" ] && [ "$deploy_verified" != "true" ]; then
                        echo -e "${RED}ERROR: Deployment verification required but not completed${NC}"
                        echo -e "${RED}Action: $action_name${NC}"
                        echo -e "${YELLOW}Run: ./aicheck deploy verify $action_name${NC}"
                        return 1
                    fi
                    
                    # Check for open critical issues
                    local critical_issues=$(yq '.issues[] | select(.severity == "critical" and .status == "open") | .id' "$action_dir/action.yaml" 2>/dev/null | wc -l)
                    if [ "$critical_issues" -gt 0 ]; then
                        echo -e "${RED}ERROR: $critical_issues critical issues remain open${NC}"
                        echo -e "${RED}Resolve critical issues before completing action${NC}"
                        return 1
                    fi
                fi
                
                # Check if todo.md has incomplete tasks
                if [ -f "$action_dir/todo.md" ]; then
                    local incomplete_tasks=$(grep -c "^- \[ \]" "$action_dir/todo.md" 2>/dev/null || echo "0")
                    if [ "$incomplete_tasks" -gt 0 ]; then
                        echo -e "${YELLOW}WARNING: $incomplete_tasks tasks remain incomplete in todo.md${NC}"
                        echo -e "${YELLOW}Consider completing all tasks before marking action as complete${NC}"
                        # This is a warning, not a blocker
                    fi
                fi
                
                echo -e "${GREEN}✓ Action completion checks passed${NC}"
            fi
        fi
    done
    
    return 0
}

# Main pre-commit logic
main() {
    # Check action completion
    if ! check_action_completion; then
        exit 1
    fi
    
    # Add more checks here as needed
    
    exit 0
}

main "$@"
PRECOMMIT

# ============= PREPARE-COMMIT-MSG HOOK =============
cat > prepare-commit-msg-enhanced << 'PREPARECOMMIT'
#!/bin/bash

# Enhanced prepare-commit-msg hook for AICheck
# Adds helpful context to commit messages

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2
SHA1=$3

# Check if we're completing an action
if grep -q "action complete" "$COMMIT_MSG_FILE"; then
    # Extract action name
    action_name=$(grep -oE "action complete \S+" "$COMMIT_MSG_FILE" | awk '{print $3}')
    
    if [ -n "$action_name" ]; then
        # Add deployment verification reminder
        cat >> "$COMMIT_MSG_FILE" << MSG

# AICheck Reminder:
# - Ensure deployment is verified (if required)
# - Check all tasks are completed
# - Verify dependencies are documented
# - Update ACTION_TIMELINE.md after merge
MSG
    fi
fi
PREPARECOMMIT

# ============= POST-COMMIT HOOK =============
cat > post-commit-enhanced << 'POSTCOMMIT'
#!/bin/bash

# Enhanced post-commit hook for AICheck
# Updates indexes and performs post-commit actions

# Colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
NC="\033[0m"

# Source the index generator if available
if [ -f ".aicheck/actions/streamlined-action-management/supporting_docs/index-generator.sh" ]; then
    source ".aicheck/actions/streamlined-action-management/supporting_docs/index-generator.sh"
fi

# Check if an action was completed
check_completed_actions() {
    local commit_msg=$(git log -1 --pretty=%B)
    
    if [[ "$commit_msg" =~ "action complete" ]]; then
        echo -e "${CYAN}Action completion detected${NC}"
        
        # Update indexes
        if command -v update_actions_index >/dev/null 2>&1; then
            echo -e "${CYAN}Updating action indexes...${NC}"
            update_actions_index
        fi
        
        # Remind about timeline update
        echo -e "${YELLOW}Remember to update ACTION_TIMELINE.md${NC}"
        
        # Check if action should be moved to completed/
        local action_name=$(echo "$commit_msg" | grep -oE "action complete \S+" | awk '{print $3}')
        if [ -n "$action_name" ]; then
            local action_dir=".aicheck/actions/$action_name"
            if [ -d "$action_dir" ]; then
                echo -e "${YELLOW}Consider moving action to .aicheck/actions/completed/${NC}"
                echo -e "${YELLOW}Command: mv '$action_dir' .aicheck/actions/completed/${NC}"
            fi
        fi
    fi
}

# Check if deployment was verified
check_deployment_verification() {
    local commit_msg=$(git log -1 --pretty=%B)
    
    if [[ "$commit_msg" =~ "deploy verify" ]]; then
        echo -e "${GREEN}✓ Deployment verification recorded${NC}"
        
        # Could trigger additional actions here
        # e.g., notify team, update dashboards, etc.
    fi
}

# Main post-commit logic
main() {
    check_completed_actions
    check_deployment_verification
}

main "$@"
POSTCOMMIT

# ============= PRE-PUSH HOOK =============
cat > pre-push-enhanced << 'PREPUSH'
#!/bin/bash

# Enhanced pre-push hook for AICheck
# Final verification before pushing to remote

# Colors
RED="\033[0;31m"
YELLOW="\033[0;33m"
GREEN="\033[0;32m"
CYAN="\033[0;36m"
NC="\033[0m"

# Check for uncommitted deployment verifications
check_deployment_sync() {
    echo -e "${CYAN}Checking deployment verification status...${NC}"
    
    # Look for action.yaml files with verified=true but not committed
    for action_yaml in .aicheck/actions/*/action.yaml; do
        if [ -f "$action_yaml" ]; then
            # Check if file has uncommitted changes
            if git diff --name-only | grep -q "$action_yaml"; then
                echo -e "${YELLOW}WARNING: Uncommitted changes in $action_yaml${NC}"
                echo -e "${YELLOW}Consider committing deployment verification status${NC}"
            fi
        fi
    done
}

# Check for action inconsistencies
check_action_consistency() {
    echo -e "${CYAN}Checking action consistency...${NC}"
    
    # Add consistency checks here
    # e.g., status.txt matches action.yaml status
    
    return 0
}

# Main pre-push logic
main() {
    check_deployment_sync
    check_action_consistency
    
    echo -e "${GREEN}✓ Pre-push checks complete${NC}"
    exit 0
}

main "$@"
PREPUSH

# ============= INSTALLATION SCRIPT =============
cat > install-enhanced-hooks.sh << 'INSTALL'
#!/bin/bash

# Install enhanced AICheck git hooks

HOOKS_DIR=".git/hooks"
SOURCE_DIR="$(dirname "$0")"

echo "Installing enhanced AICheck git hooks..."

# Backup existing hooks
for hook in pre-commit prepare-commit-msg post-commit pre-push; do
    if [ -f "$HOOKS_DIR/$hook" ]; then
        echo "Backing up existing $hook hook..."
        cp "$HOOKS_DIR/$hook" "$HOOKS_DIR/$hook.backup"
    fi
done

# Install new hooks
cp "$SOURCE_DIR/pre-commit-enhanced" "$HOOKS_DIR/pre-commit"
cp "$SOURCE_DIR/prepare-commit-msg-enhanced" "$HOOKS_DIR/prepare-commit-msg"
cp "$SOURCE_DIR/post-commit-enhanced" "$HOOKS_DIR/post-commit"
cp "$SOURCE_DIR/pre-push-enhanced" "$HOOKS_DIR/pre-push"

# Make executable
chmod +x "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/prepare-commit-msg"
chmod +x "$HOOKS_DIR/post-commit"
chmod +x "$HOOKS_DIR/pre-push"

echo "✓ Enhanced git hooks installed successfully"
echo ""
echo "Hooks installed:"
echo "  - pre-commit: Checks deployment verification before completing actions"
echo "  - prepare-commit-msg: Adds helpful reminders to commit messages"
echo "  - post-commit: Updates indexes after action completion"
echo "  - pre-push: Final consistency checks before pushing"
INSTALL

chmod +x install-enhanced-hooks.sh

echo "Enhanced git hooks created. Run ./install-enhanced-hooks.sh to install."