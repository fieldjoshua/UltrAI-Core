#!/bin/bash

# AICheck Advanced Action Management
# Enhanced action management with status tracking and validation

# Source security utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/security.sh"

# Configuration
ACTIONS_DIR=".aicheck/actions"
COMPLETED_DIR=".aicheck/actions/completed"
INDEX_FILE=".aicheck/actions_index.md"
CURRENT_ACTION_FILE=".aicheck/current_action"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create action with enhanced validation
action_create_advanced() {
    local action_name="$1"
    
    if [[ -z "$action_name" ]]; then
        echo -e "${RED}Error:${NC} Action name required"
        return 1
    fi
    
    # Validate action name format
    if ! validate_action_name "$action_name"; then
        return 1
    fi
    
    # Sanitize input
    action_name=$(sanitize_input "$action_name")
    
    local action_dir="$ACTIONS_DIR/$action_name"
    
    if [[ -d "$action_dir" ]]; then
        echo -e "${RED}Error:${NC} Action '$action_name' already exists"
        log_security_event "WARN" "Attempted to create duplicate action: $action_name"
        return 1
    fi
    
    # Create directory structure
    mkdir -p "$action_dir/supporting_docs"
    
    # Create PLAN.md from template
    if [ -f ".aicheck/templates/action/PLAN.md" ]; then
        cp ".aicheck/templates/action/PLAN.md" "$action_dir/PLAN.md"
        
        # Replace placeholders
        sed -i '' "s/\[Action Name\]/$action_name/g" "$action_dir/PLAN.md" 2>/dev/null || \
        sed -i "s/\[Action Name\]/$action_name/g" "$action_dir/PLAN.md"
        
        sed -i '' "s/\[Date\]/$(date +%Y-%m-%d)/g" "$action_dir/PLAN.md" 2>/dev/null || \
        sed -i "s/\[Date\]/$(date +%Y-%m-%d)/g" "$action_dir/PLAN.md"
    else
        # Fallback template
        cat > "$action_dir/PLAN.md" << EOF
# ACTION: $action_name

**Version**: 1.0
**Status**: Not Started
**Progress**: 0%
**Created**: $(date +%Y-%m-%d)

## Objective
[Clear statement of what this action will accomplish]

## Success Criteria
- [ ] [Specific, measurable outcome 1]
- [ ] [Specific, measurable outcome 2]

## Approach
### Phase 1: Planning
- [Task 1]

### Phase 2: Implementation  
- [Task 1]

### Phase 3: Testing
- [Task 1]

## Test Requirements
- [Test descriptions]

## Timeline
- **Target Completion**: [Date]
EOF
    fi
    
    # Create todo.md from template
    if [ -f ".aicheck/templates/action/todo.md" ]; then
        cp ".aicheck/templates/action/todo.md" "$action_dir/todo.md"
        sed -i '' "s/\[Action Name\]/$action_name/g" "$action_dir/todo.md" 2>/dev/null || \
        sed -i "s/\[Action Name\]/$action_name/g" "$action_dir/todo.md"
    else
        cat > "$action_dir/todo.md" << EOF
# TODO: $action_name

## Active Tasks
- [ ] Review and understand PLAN.md (priority: high, status: pending)
- [ ] Set up development environment (priority: high, status: pending)

## Completed Tasks
<!-- Move completed items here -->

## Notes
- Follow test-driven development
- Update progress in PLAN.md as tasks complete
EOF
    fi
    
    # Create status and progress tracking files
    echo "Not Started" > "$action_dir/status.txt"
    echo "0" > "$action_dir/progress.txt"
    
    # Set secure permissions
    chmod 755 "$action_dir"
    chmod 644 "$action_dir"/*.md "$action_dir"/*.txt
    chmod 755 "$action_dir/supporting_docs"
    
    echo -e "${GREEN}✓${NC} Created action: $action_name"
    echo -e "  ${BLUE}→${NC} Edit plan: $action_dir/PLAN.md"
    echo -e "  ${BLUE}→${NC} Track tasks: $action_dir/todo.md"
    
    log_security_event "INFO" "Action created: $action_name"
}

# Update action status
action_update_status() {
    local action_name="$1"
    local status="$2"
    
    if [[ -z "$action_name" || -z "$status" ]]; then
        echo -e "${RED}Error:${NC} Action name and status required"
        return 1
    fi
    
    local action_dir="$ACTIONS_DIR/$action_name"
    if [[ ! -d "$action_dir" ]]; then
        echo -e "${RED}Error:${NC} Action '$action_name' does not exist"
        return 1
    fi
    
    # Validate status
    case "$status" in
        "Not Started"|"ActiveAction"|"Completed"|"Blocked"|"Cancelled")
            ;;
        *)
            echo -e "${RED}Error:${NC} Invalid status. Use: Not Started, ActiveAction, Completed, Blocked, Cancelled"
            return 1
            ;;
    esac
    
    echo "$status" > "$action_dir/status.txt"
    echo -e "${GREEN}✓${NC} Updated status for '$action_name' to '$status'"
    
    log_security_event "INFO" "Action status updated: $action_name -> $status"
}

# Update action progress
action_update_progress() {
    local action_name="$1"
    local progress="$2"
    
    if [[ -z "$action_name" || -z "$progress" ]]; then
        echo -e "${RED}Error:${NC} Action name and progress required"
        return 1
    fi
    
    # Validate progress is a number 0-100
    if ! [[ "$progress" =~ ^[0-9]+$ ]] || [ "$progress" -lt 0 ] || [ "$progress" -gt 100 ]; then
        echo -e "${RED}Error:${NC} Progress must be a number between 0 and 100"
        return 1
    fi
    
    local action_dir="$ACTIONS_DIR/$action_name"
    if [[ ! -d "$action_dir" ]]; then
        echo -e "${RED}Error:${NC} Action '$action_name' does not exist"
        return 1
    fi
    
    echo "$progress" > "$action_dir/progress.txt"
    echo -e "${GREEN}✓${NC} Updated progress for '$action_name' to $progress%"
    
    log_security_event "INFO" "Action progress updated: $action_name -> $progress%"
}

# Show comprehensive system status
show_system_status() {
    echo -e "${BLUE}═══ AICheck System Status ═══${NC}"
    echo
    
    # Current action
    if [[ -f "$CURRENT_ACTION_FILE" ]]; then
        local current_action=$(cat "$CURRENT_ACTION_FILE")
        if [[ -n "$current_action" ]]; then
            echo -e "${YELLOW}Current ActiveAction:${NC} $current_action"
            
            local action_dir="$ACTIONS_DIR/$current_action"
            if [[ -d "$action_dir" ]]; then
                local status="Unknown"
                local progress="0"
                
                [[ -f "$action_dir/status.txt" ]] && status=$(cat "$action_dir/status.txt")
                [[ -f "$action_dir/progress.txt" ]] && progress=$(cat "$action_dir/progress.txt")
                
                echo -e "  Status: $status"
                echo -e "  Progress: $progress%"
                
                # Generate progress bar
                local filled=$((progress / 10))
                local empty=$((10 - filled))
                local bar=""
                for ((i=0; i<filled; i++)); do bar+="█"; done
                for ((i=0; i<empty; i++)); do bar+="░"; done
                echo -e "  Progress: [$bar] $progress%"
            fi
        else
            echo -e "${YELLOW}Current ActiveAction:${NC} None"
        fi
    else
        echo -e "${YELLOW}Current ActiveAction:${NC} None"
    fi
    
    echo
    
    # Action summary
    local total_actions=0
    local not_started=0
    local active=0
    local completed=0
    local blocked=0
    local cancelled=0
    
    if [[ -d "$ACTIONS_DIR" ]]; then
        for action_dir in "$ACTIONS_DIR"/*; do
            if [[ -d "$action_dir" && "$(basename "$action_dir")" != "completed" ]]; then
                ((total_actions++))
                local status="Unknown"
                [[ -f "$action_dir/status.txt" ]] && status=$(cat "$action_dir/status.txt")
                
                case "$status" in
                    "Not Started") ((not_started++));;
                    "ActiveAction") ((active++));;
                    "Completed") ((completed++));;
                    "Blocked") ((blocked++));;
                    "Cancelled") ((cancelled++));;
                esac
            fi
        done
    fi
    
    echo -e "${BLUE}Action Summary:${NC}"
    echo -e "  🔴 Not Started: $not_started"
    echo -e "  🟡 ActiveAction: $active"
    echo -e "  🟢 Completed: $completed"
    echo -e "  ⏸️  Blocked: $blocked"
    echo -e "  ❌ Cancelled: $cancelled"
    echo -e "  📊 Total: $total_actions"
    
    echo
    
    # Recent activity
    echo -e "${BLUE}Recent Actions:${NC}"
    if [[ -d "$ACTIONS_DIR" ]]; then
        find "$ACTIONS_DIR" -name "PLAN.md" -not -path "*/completed/*" | head -5 | while read -r plan_file; do
            local action_name=$(basename "$(dirname "$plan_file")")
            local action_dir="$(dirname "$plan_file")"
            local status="Unknown"
            local progress="0"
            
            [[ -f "$action_dir/status.txt" ]] && status=$(cat "$action_dir/status.txt")
            [[ -f "$action_dir/progress.txt" ]] && progress=$(cat "$action_dir/progress.txt")
            
            echo -e "  • $action_name ($status, $progress%)"
        done
    else
        echo -e "  No actions found"
    fi
}

# Complete an action (move to completed directory)
action_complete() {
    local action_name="$1"
    
    if [[ -z "$action_name" ]]; then
        echo -e "${RED}Error:${NC} Action name required"
        return 1
    fi
    
    local action_dir="$ACTIONS_DIR/$action_name"
    if [[ ! -d "$action_dir" ]]; then
        echo -e "${RED}Error:${NC} Action '$action_name' does not exist"
        return 1
    fi
    
    # Create completed directory if it doesn't exist
    mkdir -p "$COMPLETED_DIR"
    
    # Move action to completed directory
    if mv "$action_dir" "$COMPLETED_DIR/"; then
        # Update status in the moved action
        echo "Completed" > "$COMPLETED_DIR/$action_name/status.txt"
        echo "100" > "$COMPLETED_DIR/$action_name/progress.txt"
        
        # Clear current action if this was it
        if [[ -f "$CURRENT_ACTION_FILE" ]]; then
            local current=$(cat "$CURRENT_ACTION_FILE")
            if [[ "$current" == "$action_name" ]]; then
                > "$CURRENT_ACTION_FILE"
            fi
        fi
        
        echo -e "${GREEN}✓${NC} Action '$action_name' completed and moved to completed/"
        echo -e "${YELLOW}!${NC} Remember to update actions_index.md and ACTION_TIMELINE.md"
        
        log_security_event "INFO" "Action completed: $action_name"
    else
        echo -e "${RED}Error:${NC} Failed to move action to completed directory"
        return 1
    fi
}

# Export functions
export -f action_create_advanced
export -f action_update_status  
export -f action_update_progress
export -f show_system_status
export -f action_complete