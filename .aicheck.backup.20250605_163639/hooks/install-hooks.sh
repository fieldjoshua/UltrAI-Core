#!/bin/bash
# install-hooks.sh - Install AICheck git hooks

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Installing AICheck git hooks...${NC}"

# Create hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install post-commit hook
cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
# AICheck post-commit hook

# Check if this commit mentions action completion
if git log -1 --pretty=%B | grep -q -i "action.*complete\|complete.*action\|✅.*COMPLETED"; then
    # Extract action name from commit message
    ACTION_NAME=$(git log -1 --pretty=%B | grep -oP '(?:action:|complete:|completed:)\s*\K[\w-]+' | head -1)
    
    # If we found an action name, run the completion check
    if [[ -n "$ACTION_NAME" ]]; then
        .aicheck/hooks/post-action-complete.sh action complete "$ACTION_NAME"
    else
        # Try to get from current_action file
        .aicheck/hooks/post-action-complete.sh
    fi
fi
EOF

# Install prepare-commit-msg hook
cat > .git/hooks/prepare-commit-msg << 'EOF'
#!/bin/bash
# AICheck prepare-commit-msg hook

# Add reminder about action completion requirements
if [[ -f ".aicheck/current_action" ]]; then
    CURRENT_ACTION=$(cat .aicheck/current_action)
    
    # Check if user is trying to complete an action
    if grep -q -i "complete\|finish\|done" "$1"; then
        cat >> "$1" << REMINDER

# AICheck Reminder: Action Completion Requirements
# ================================================
# Before marking action '${CURRENT_ACTION}' as complete:
# 1. Migrate universal docs from supporting_docs/ to /documentation/
# 2. Update .aicheck/actions_index.md (mark as Completed)
# 3. Update .aicheck/ACTION_TIMELINE.md (add completion entry)
# 4. Document all dependencies (external and internal)
# 5. Move action directory to .aicheck/actions/completed/
#
# Run: .aicheck/hooks/post-action-complete.sh to verify
REMINDER
    fi
fi
EOF

# Install pre-push hook for Vision Guardian (optional)
if [[ -f ".aicheck/guardian" ]]; then
    cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
# Vision Guardian pre-push hook

echo "🛡️ Running Vision Guardian IP protection audit..."
.aicheck/guardian audit --pre-push
if [ $? -ne 0 ]; then
    echo "❌ IP protection concerns detected. Push blocked."
    echo "Run: .aicheck/guardian audit --details for more info"
    exit 1
fi
echo "✅ IP protection audit passed"
EOF
fi

# Make all hooks executable
chmod +x .git/hooks/post-commit
chmod +x .git/hooks/prepare-commit-msg
[[ -f .git/hooks/pre-push ]] && chmod +x .git/hooks/pre-push

echo -e "${GREEN}✅ Git hooks installed successfully!${NC}"
echo -e "${YELLOW}Hooks installed:${NC}"
echo "  - post-commit: Checks action completion requirements"
echo "  - prepare-commit-msg: Adds completion reminders"
[[ -f .git/hooks/pre-push ]] && echo "  - pre-push: Vision Guardian IP protection audit"

echo -e "\n${BLUE}To test the completion check manually:${NC}"
echo "  .aicheck/hooks/post-action-complete.sh action complete <action-name>"