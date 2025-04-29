#!/bin/bash
# .aicheck/scripts/action.sh
# RULES.md-compliant action management functions

actions_dir=".aicheck/actions"
index_file=".aicheck/docs/actions_index.md"

# Colors for output
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Create a new action
action_create() {
    local action_name="$1"
    local action_dir="$actions_dir/$action_name"
    local plan_file="$action_dir/${action_name}-PLAN.md"
    local status_file="$action_dir/status.md"
    local progress_file="$action_dir/progress.md"
    local docs_dir="$action_dir/supporting_docs"

    if [[ -z "$action_name" ]]; then
        echo "[action_create] Error: Action name required." >&2
        return 1
    fi
    if [[ ! "$action_name" =~ ^[A-Z][a-zA-Z0-9]+$ ]]; then
        echo "[action_create] Error: Action name must be PascalCase (e.g., MyAction)." >&2
        return 1
    fi
    if [[ -d "$action_dir" ]]; then
        echo "[action_create] Error: Action '$action_name' already exists." >&2
        return 1
    fi
    mkdir -p "$docs_dir"
    cat > "$plan_file" <<EOL
# $action_name Action Plan

## Purpose
[Describe the purpose of this action.]

## Value
[Briefly explain the value or benefit of this action to the project.]

## Steps
- [ ] Step 1
- [ ] Step 2

## Notes
EOL
    echo "Not Started" > "$status_file"
    echo "0%" > "$progress_file"
    echo "[action_create] Created action '$action_name' at $action_dir."
}

# Switch to an action
action_switch() {
    local action_name="$1"
    local action_dir="$actions_dir/$action_name"
    local current_action_file=".aicheck/current_action"
    if [[ -z "$action_name" ]]; then
        echo "[action_switch] Error: Action name required." >&2
        return 1
    fi
    if [[ ! -d "$action_dir" ]]; then
        echo "[action_switch] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    echo "$action_name" > "$current_action_file"
    echo "[action_switch] Switched to action '$action_name'."
}

# Show action status
action_status() {
    local action_name="$1"
    local action_dir="$actions_dir/$action_name"
    local plan_file="$action_dir/${action_name}-PLAN.md"
    local status_file="$action_dir/status.md"
    local progress_file="$action_dir/progress.md"
    if [[ -z "$action_name" ]]; then
        echo "[action_status] Error: Action name required." >&2
        return 1
    fi
    if [[ ! -d "$action_dir" ]]; then
        echo "[action_status] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    echo "[action_status] Action: $action_name"
    [[ -f "$status_file" ]] && echo "Status: $(cat "$status_file")"
    [[ -f "$progress_file" ]] && echo "Progress: $(cat "$progress_file")"
    if [[ -f "$plan_file" ]]; then
        echo "Plan file: $plan_file"
        cat "$plan_file"
    else
        echo "No plan file found for action '$action_name'."
    fi
}

# Delete an action
action_delete() {
    local action_name="$1"
    local action_dir="$actions_dir/$action_name"
    if [[ -z "$action_name" ]]; then
        echo "[action_delete] Error: Action name required." >&2
        return 1
    fi
    if [[ ! -d "$action_dir" ]]; then
        echo "[action_delete] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    rm -rf "$action_dir"
    echo "[action_delete] Deleted action '$action_name'."
}

# Update action status
action_update_status() {
    local action_name="$1"
    local status="$2"
    local status_file="$actions_dir/$action_name/status.md"
    if [[ -z "$action_name" || -z "$status" ]]; then
        echo "[action_update_status] Error: Action name and status required." >&2
        return 1
    fi
    if [[ ! -d "$actions_dir/$action_name" ]]; then
        echo "[action_update_status] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    echo "$status" > "$status_file"
    echo "[action_update_status] Updated status for '$action_name' to '$status'."
}

# Update action progress
action_update_progress() {
    local action_name="$1"
    local progress="$2"
    local progress_file="$actions_dir/$action_name/progress.md"
    if [[ -z "$action_name" || -z "$progress" ]]; then
        echo "[action_update_progress] Error: Action name and progress required." >&2
        return 1
    fi
    if [[ ! -d "$actions_dir/$action_name" ]]; then
        echo "[action_update_progress] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    echo "$progress" > "$progress_file"
    echo "[action_update_progress] Updated progress for '$action_name' to '$progress'."

    # If progress is 100%, prompt for additional improvements
    if [[ "$progress" == "100%" ]]; then
        # Play alert sound if available
        if command -v afplay &> /dev/null; then
            afplay /System/Library/Sounds/Glass.aiff &> /dev/null
        elif command -v paplay &> /dev/null; then
            paplay /usr/share/sounds/freedesktop/stereo/complete.oga &> /dev/null
        fi

        echo ""
        echo -e "${BOLD}${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}${YELLOW}║                 !!! ACTION COMPLETION CHECK !!!                ║${NC}"
        echo -e "${BOLD}${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        echo -e "${BOLD}Action '${BLUE}$action_name${NC}' has reached 100% progress."
        echo -e "${BOLD}Before closing this action, please review:${NC}"
        echo ""
        echo -e "${BOLD}1. Additional Improvements${NC}"
        echo -e "   ${YELLOW}• Are there any improvements that could be made within scope?${NC}"
        echo -e "   ${YELLOW}• Have all planned steps been completed to the highest quality?${NC}"
        echo -e "   ${YELLOW}• Is there any documentation that needs to be updated or added?${NC}"
        echo ""
        echo -e "${BOLD}2. Quality Assurance${NC}"
        echo -e "   ${YELLOW}• Have all tests been run and passed?${NC}"
        echo -e "   ${YELLOW}• Is the code/documentation following best practices?${NC}"
        echo -e "   ${YELLOW}• Are there any potential issues or edge cases to address?${NC}"
        echo ""
        echo -e "${BOLD}${YELLOW}Would you like to make any additional improvements? (y/n)${NC}"
        read -r make_improvements
        if [[ "$make_improvements" == "y" ]]; then
            echo ""
            echo -e "${BOLD}Please describe the improvements you'd like to make:${NC}"
            read -r improvements
            echo ""
            echo -e "${BOLD}📝 Improvements noted:${NC}"
            echo -e "${BLUE}$improvements${NC}"
            echo ""
            echo -e "${BOLD}The action will remain active.${NC}"
            echo -e "${BOLD}Next steps:${NC}"
            echo -e "${GREEN}1. Update the Action PLAN with these improvements${NC}"
            echo -e "${GREEN}2. Proceed with work on these specific improvements${NC}"
            echo -e "${GREEN}3. Update progress again when improvements are complete${NC}"
        else
            echo ""
            echo -e "${BOLD}${GREEN}✓ No additional improvements needed. The action can be closed when ready.${NC}"
        fi
    fi
} 