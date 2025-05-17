#!/bin/bash
# update.sh - System status checker for Ultra project
# Provides a summary of current action status and next steps

# Colors for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo -e "${BOLD}${BLUE}==== Ultra Project Status Update ====${NC}"
echo ""

# Check the current action
if [ -f ".aicheck/current_action" ]; then
    CURRENT_ACTION=$(cat .aicheck/current_action)
    if [[ $CURRENT_ACTION == *"-COMPLETED"* ]]; then
        ACTION_NAME=${CURRENT_ACTION%-COMPLETED}
        echo -e "${GREEN}Current Action:${NC} ${ACTION_NAME} (${BOLD}Completed${NC})"
        echo -e "${YELLOW}Status:${NC} Ready for new action selection"
    else
        echo -e "${GREEN}Current Action:${NC} ${CURRENT_ACTION}"

        # Check if there's an active plan
        if [ -f ".aicheck/actions/${CURRENT_ACTION}/${CURRENT_ACTION}-PLAN.md" ]; then
            echo -e "${YELLOW}Status:${NC} Active plan exists"
        else
            echo -e "${YELLOW}Status:${NC} Plan needs to be created"
        fi
    fi
else
    echo -e "${RED}No current action set${NC}"
fi

echo ""
echo -e "${BLUE}${BOLD}Completed Actions:${NC}"
# Find all completed actions
find .aicheck/actions -name "*-COMPLETED.md" | while read -r completed_file; do
    action_dir=$(dirname "$completed_file")
    action_name=$(basename "$completed_file" | sed 's/-COMPLETED.md//')
    echo -e "  - ${GREEN}${action_name}${NC}"
done

echo ""
echo -e "${BLUE}${BOLD}Pending Actions:${NC}"
# Parse the actions_index.md for pending actions
grep -A 3 "PendingApproval" .aicheck/docs/actions_index.md | grep "Goal:" | sed 's/- \*\*Goal:\*\* /  - /' | head -5

echo ""
echo -e "${PURPLE}${BOLD}Project Insights:${NC}"

# Check critical directories for status
check_directory_status() {
    local dir=$1
    local description=$2

    if [ -d "$dir" ]; then
        local file_count=$(find "$dir" -type f | wc -l | tr -d ' ')
        echo -e "  - ${YELLOW}${description}${NC}: ${file_count} files"
    else
        echo -e "  - ${RED}${description} directory not found${NC}"
    fi
}

check_directory_status "documentation" "Documentation"
check_directory_status "src" "Source code"
check_directory_status "frontend" "Frontend"
check_directory_status "backend" "Backend"
check_directory_status "tests" "Tests"

echo ""
echo -e "${BLUE}${BOLD}Recommended Next Steps:${NC}"

if [[ $CURRENT_ACTION == *"-COMPLETED"* ]]; then
    echo -e "  1. ${BOLD}Select a new action${NC} with: './ai action switch <ActionName>'"
    echo -e "  2. Review pending actions from the list above"
    echo -e "  3. If needed, create a new action with: './ai action create <NewActionName>'"
else
    echo -e "  1. ${BOLD}Continue work on${NC}: ${CURRENT_ACTION}"
    echo -e "  2. Review the action plan at: .aicheck/actions/${CURRENT_ACTION}/${CURRENT_ACTION}-PLAN.md"
    echo -e "  3. Update action status with: './ai action update_status ${CURRENT_ACTION} <status>'"
fi

echo ""
echo -e "${YELLOW}For more detailed information:${NC}"
echo -e "  - Run './ai status' for system status"
echo -e "  - Check '.aicheck/docs/actions_index.md' for complete actions list"
echo -e "  - View RULES.md for project guidelines"
echo ""
