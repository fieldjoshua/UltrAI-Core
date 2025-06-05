#!/bin/bash

# Sync Mechanism for AICheck
# Synchronizes data between action.yaml and traditional files

source "$(dirname "$0")/yaml-utils.sh"

# Colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m"

# Function to sync a single action
function sync_action() {
    local action_dir=$1
    local direction=${2:-"auto"}  # auto, yaml-to-files, files-to-yaml
    local action_name=$(basename "$action_dir")
    
    echo -e "${CYAN}Syncing $action_name...${NC}"
    
    # Check if action.yaml exists
    if [ ! -f "$action_dir/action.yaml" ]; then
        echo -e "${YELLOW}No action.yaml found, creating...${NC}"
        yaml_create_action "$action_dir" "$action_name"
    fi
    
    # Determine sync direction
    if [ "$direction" = "auto" ]; then
        # Auto-detect based on last modified times
        local yaml_time=$(stat -f %m "$action_dir/action.yaml" 2>/dev/null || echo "0")
        local status_time=$(stat -f %m "$action_dir/status.txt" 2>/dev/null || echo "0")
        
        if [ "$status_time" -gt "$yaml_time" ]; then
            direction="files-to-yaml"
        else
            direction="yaml-to-files"
        fi
    fi
    
    echo -e "${CYAN}Sync direction: $direction${NC}"
    
    case "$direction" in
        "files-to-yaml")
            sync_files_to_yaml "$action_dir"
            ;;
        "yaml-to-files")
            sync_yaml_to_files "$action_dir"
            ;;
        *)
            echo -e "${RED}Unknown sync direction: $direction${NC}"
            return 1
            ;;
    esac
    
    # Update sync metadata
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    yaml_write "$action_dir/action.yaml" ".sync.last_synced" "$timestamp"
    yaml_write "$action_dir/action.yaml" ".sync.sync_direction" "$direction"
    
    echo -e "${GREEN}✓ Sync completed${NC}"
}

# Function to sync from traditional files to YAML
function sync_files_to_yaml() {
    local action_dir=$1
    
    # Sync status
    if [ -f "$action_dir/status.txt" ]; then
        local status=$(cat "$action_dir/status.txt" | tr -d '\n')
        yaml_write "$action_dir/action.yaml" ".action.status" "$status"
        echo "  ✓ Status: $status"
    fi
    
    # Sync progress
    if [ -f "$action_dir/progress.md" ]; then
        local progress=$(grep -oE "Progress: [0-9]+%" "$action_dir/progress.md" | grep -oE "[0-9]+" | head -1)
        if [ -n "$progress" ]; then
            yaml_write "$action_dir/action.yaml" ".action.progress" "$progress"
            echo "  ✓ Progress: $progress%"
        fi
    fi
    
    # Sync task counts from todo.md
    if [ -f "$action_dir/todo.md" ]; then
        local total_tasks=$(grep -c "^- \[ \]" "$action_dir/todo.md" 2>/dev/null || echo "0")
        local completed_tasks=$(grep -c "^- \[x\]" "$action_dir/todo.md" 2>/dev/null || echo "0")
        local in_progress_tasks=$(grep -c "^- \[>\]" "$action_dir/todo.md" 2>/dev/null || echo "0")
        
        yaml_write "$action_dir/action.yaml" ".task_summary.total" "$((total_tasks + completed_tasks + in_progress_tasks))"
        yaml_write "$action_dir/action.yaml" ".task_summary.completed" "$completed_tasks"
        yaml_write "$action_dir/action.yaml" ".task_summary.in_progress" "$in_progress_tasks"
        
        echo "  ✓ Tasks: $completed_tasks completed, $in_progress_tasks in progress, $total_tasks pending"
    fi
    
    # Sync plan purpose (first paragraph)
    if [ -f "$action_dir/*-plan.md" ]; then
        local purpose=$(awk '/^## Purpose/{getline; getline; print; exit}' "$action_dir"/*-plan.md)
        if [ -n "$purpose" ]; then
            yaml_write "$action_dir/action.yaml" ".plan.purpose" "$purpose"
            echo "  ✓ Purpose synced from plan"
        fi
    fi
}

# Function to sync from YAML to traditional files
function sync_yaml_to_files() {
    local action_dir=$1
    
    # Sync status
    local status=$(yaml_read "$action_dir/action.yaml" ".action.status" "")
    if [ -n "$status" ] && [ "$status" != "null" ]; then
        echo "$status" > "$action_dir/status.txt"
        echo "  ✓ Status: $status"
    fi
    
    # Note: We don't sync tasks back to todo.md to preserve Claude's management
    echo "  ℹ Todo.md preserved (managed by Claude)"
}

# Function to sync all actions
function sync_all_actions() {
    local direction=${1:-"auto"}
    local count=0
    local synced=0
    
    echo -e "${CYAN}Syncing all actions...${NC}"
    
    for action_dir in .aicheck/actions/*/; do
        if [ -d "$action_dir" ] && [ "$(basename "$action_dir")" != "completed" ]; then
            ((count++))
            if sync_action "$action_dir" "$direction"; then
                ((synced++))
            fi
            echo ""
        fi
    done
    
    echo -e "${GREEN}✓ Synced $synced of $count actions${NC}"
}

# Function to detect and report sync conflicts
function detect_sync_conflicts() {
    local action_dir=$1
    local conflicts=()
    
    # Check for status mismatch
    if [ -f "$action_dir/status.txt" ] && [ -f "$action_dir/action.yaml" ]; then
        local file_status=$(cat "$action_dir/status.txt" | tr -d '\n')
        local yaml_status=$(yaml_read "$action_dir/action.yaml" ".action.status" "")
        
        if [ "$file_status" != "$yaml_status" ] && [ -n "$file_status" ] && [ -n "$yaml_status" ]; then
            conflicts+=("Status mismatch: status.txt='$file_status' vs action.yaml='$yaml_status'")
        fi
    fi
    
    # Report conflicts
    if [ ${#conflicts[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠ Sync conflicts detected:${NC}"
        for conflict in "${conflicts[@]}"; do
            echo "  - $conflict"
        done
        return 1
    else
        return 0
    fi
}

# Function to resolve sync conflicts
function resolve_sync_conflicts() {
    local action_dir=$1
    local strategy=${2:-"newest"}  # newest, yaml-wins, files-win, interactive
    
    if ! detect_sync_conflicts "$action_dir"; then
        echo -e "${CYAN}Resolving conflicts with strategy: $strategy${NC}"
        
        case "$strategy" in
            "newest")
                # Use newest file
                sync_action "$action_dir" "auto"
                ;;
            "yaml-wins")
                sync_action "$action_dir" "yaml-to-files"
                ;;
            "files-win")
                sync_action "$action_dir" "files-to-yaml"
                ;;
            "interactive")
                echo "Interactive resolution not yet implemented"
                ;;
        esac
    fi
}

# Function to generate sync report
function generate_sync_report() {
    local report_file=".aicheck/sync-report-$(date +%Y%m%d-%H%M%S).md"
    
    echo "# AICheck Sync Report" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "" >> "$report_file"
    
    echo "## Action Status" >> "$report_file"
    echo "" >> "$report_file"
    echo "| Action | Has YAML | Status | Last Synced | Conflicts |" >> "$report_file"
    echo "|--------|----------|---------|-------------|-----------|" >> "$report_file"
    
    for action_dir in .aicheck/actions/*/; do
        if [ -d "$action_dir" ] && [ "$(basename "$action_dir")" != "completed" ]; then
            local action_name=$(basename "$action_dir")
            local has_yaml="No"
            local status="Unknown"
            local last_synced="Never"
            local conflicts="None"
            
            if [ -f "$action_dir/action.yaml" ]; then
                has_yaml="Yes"
                status=$(yaml_read "$action_dir/action.yaml" ".action.status" "Unknown")
                last_synced=$(yaml_read "$action_dir/action.yaml" ".sync.last_synced" "Never")
                
                if ! detect_sync_conflicts "$action_dir" >/dev/null 2>&1; then
                    conflicts="Yes"
                fi
            elif [ -f "$action_dir/status.txt" ]; then
                status=$(cat "$action_dir/status.txt")
            fi
            
            echo "| $action_name | $has_yaml | $status | $last_synced | $conflicts |" >> "$report_file"
        fi
    done
    
    echo "" >> "$report_file"
    echo "Report saved to: $report_file"
    
    # Also display summary
    local total_actions=$(find .aicheck/actions -maxdepth 1 -type d | grep -v "^.aicheck/actions$" | grep -v "completed" | wc -l)
    local yaml_actions=$(find .aicheck/actions -name "action.yaml" | wc -l)
    
    echo -e "${CYAN}Sync Summary:${NC}"
    echo "  Total actions: $total_actions"
    echo "  With action.yaml: $yaml_actions"
    echo "  Need migration: $((total_actions - yaml_actions))"
}

# Export functions
export -f sync_action
export -f sync_files_to_yaml
export -f sync_yaml_to_files
export -f sync_all_actions
export -f detect_sync_conflicts
export -f resolve_sync_conflicts
export -f generate_sync_report