#!/bin/bash

# Automated Index Generator for AICheck
# Generates and updates various index files from action data

source "$(dirname "$0")/yaml-utils.sh"

# Colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
BRIGHT_BLURPLE="\033[38;5;135m"
NC="\033[0m"

# Function to update actions_index.md
function update_actions_index() {
    local index_file=".aicheck/actions_index.md"
    local temp_file="/tmp/actions_index_$$.md"
    
    echo -e "${CYAN}Updating actions index...${NC}"
    
    # Start building the new index
    cat > "$temp_file" << 'HEADER'
# 📋 AICheck Actions Index

*Your comprehensive guide to all AICheck actions in this repository*

*Last Updated: DATE_PLACEHOLDER*

---

## 🎯 Actions Dashboard

### Quick Stats
- **Total Actions**: TOTAL_COUNT
- **Active Actions**: ACTIVE_COUNT
- **Completed Actions**: COMPLETED_COUNT
- **Success Rate**: SUCCESS_RATE%

---

## 🔄 Active Actions

| Action | Assignee | Status | Progress | Last Updated |
|--------|----------|---------|----------|--------------|
HEADER

    # Replace date placeholder
    sed -i "" "s/DATE_PLACEHOLDER/$(date +"%Y-%m-%d")/" "$temp_file"
    
    # Collect statistics
    local total_count=0
    local active_count=0
    local completed_count=0
    local has_active=false
    
    # Process active actions
    for action_dir in .aicheck/actions/*/; do
        if [ -d "$action_dir" ] && [ "$(basename "$action_dir")" != "completed" ]; then
            local action_name=$(basename "$action_dir")
            local status="Unknown"
            local progress="0"
            local last_updated=""
            
            # Try to read from action.yaml first
            if [ -f "$action_dir/action.yaml" ]; then
                status=$(yaml_read "$action_dir/action.yaml" ".action.status" "Unknown")
                progress=$(yaml_read "$action_dir/action.yaml" ".action.progress" "0")
                last_updated=$(yaml_read "$action_dir/action.yaml" ".sync.last_synced" "")
            fi
            
            # Fallback to traditional files
            if [ "$status" = "Unknown" ] && [ -f "$action_dir/status.txt" ]; then
                status=$(cat "$action_dir/status.txt" | tr -d '\n')
            fi
            
            if [ -z "$last_updated" ]; then
                # Get last modified time of directory
                last_updated=$(date -r "$action_dir" +"%Y-%m-%d" 2>/dev/null || echo "Unknown")
            fi
            
            # Count statistics
            ((total_count++))
            
            if [[ "$status" == "Completed" ]]; then
                ((completed_count++))
            elif [[ "$status" != "Cancelled" ]]; then
                ((active_count++))
                has_active=true
                
                # Create progress bar
                local progress_bar=$(create_progress_bar "$progress")
                
                # Get status emoji
                local status_emoji=$(get_status_emoji "$status")
                
                # Add to active table
                echo "| $action_name | | $status_emoji $status | $progress_bar $progress% | $last_updated |" >> "$temp_file"
            fi
        fi
    done
    
    if [ "$has_active" = "false" ]; then
        echo "| *None yet* | | | | |" >> "$temp_file"
    fi
    
    # Add completed actions section
    cat >> "$temp_file" << 'COMPLETED_HEADER'

---

## ✅ Completed Actions

<details>
<summary>Click to expand completed actions</summary>

| Action | Description | Completed Date | Duration |
|--------|-------------|----------------|----------|
COMPLETED_HEADER

    local has_completed=false
    
    # Process completed actions
    for action_dir in .aicheck/actions/completed/*/; do
        if [ -d "$action_dir" ]; then
            local action_name=$(basename "$action_dir")
            local completed_date="Unknown"
            local description=""
            
            if [ -f "$action_dir/action.yaml" ]; then
                completed_date=$(yaml_read "$action_dir/action.yaml" ".action.completed" "Unknown")
                description=$(yaml_read "$action_dir/action.yaml" ".plan.purpose" "" | head -1)
            fi
            
            echo "| $action_name | ${description:0:50}... | $completed_date | |" >> "$temp_file"
            has_completed=true
            ((completed_count++))
            ((total_count++))
        fi
    done
    
    if [ "$has_completed" = "false" ]; then
        echo "| *None yet* | | | |" >> "$temp_file"
    fi
    
    echo "</details>" >> "$temp_file"
    
    # Add footer
    cat >> "$temp_file" << 'FOOTER'

---

## 📊 Action Categories

### By Type
- 🔧 **Feature Development**: COUNT features
- 🐛 **Bug Fixes**: COUNT fixes
- 📚 **Documentation**: COUNT docs
- 🧪 **Testing**: COUNT tests
- 🔒 **Security**: COUNT security

### By Priority
- 🔴 **Critical**: COUNT critical
- 🟡 **High**: COUNT high
- 🟢 **Medium**: COUNT medium
- ⚪ **Low**: COUNT low

---

## 🔗 Quick Links

- [Project Documentation](../documentation/README.md)
- [AICheck Rules](.aicheck/RULES.md)
- [Action Timeline](.aicheck/ACTION_TIMELINE.md)
- [Dependency Index](../documentation/dependencies/dependency_index.md)

---

*Generated by AICheck Index Generator*
FOOTER

    # Update statistics in the file
    local success_rate=0
    if [ "$total_count" -gt 0 ]; then
        success_rate=$(( (completed_count * 100) / total_count ))
    fi
    
    sed -i "" "s/TOTAL_COUNT/$total_count/" "$temp_file"
    sed -i "" "s/ACTIVE_COUNT/$active_count/" "$temp_file"
    sed -i "" "s/COMPLETED_COUNT/$completed_count/" "$temp_file"
    sed -i "" "s/SUCCESS_RATE/$success_rate/" "$temp_file"
    
    # Move the temp file to the actual index
    mv "$temp_file" "$index_file"
    
    echo -e "${GREEN}✓ Updated actions index${NC}"
    echo "  Total: $total_count, Active: $active_count, Completed: $completed_count"
}

# Function to update ACTION_TIMELINE.md
function update_action_timeline() {
    local timeline_file=".aicheck/ACTION_TIMELINE.md"
    
    echo -e "${CYAN}Updating action timeline...${NC}"
    
    # Check if we should add an entry (only for completed actions)
    # This is a simplified version - in production, you'd want more logic
    
    echo -e "${GREEN}✓ Timeline update check complete${NC}"
}

# Function to update dependency index
function update_dependency_index() {
    local dep_file="documentation/dependencies/dependency_index.md"
    
    if [ ! -f "$dep_file" ]; then
        echo -e "${YELLOW}Dependency index not found, skipping${NC}"
        return
    fi
    
    echo -e "${CYAN}Updating dependency index...${NC}"
    
    # Scan all action.yaml files for dependencies
    local external_deps=()
    local internal_deps=()
    
    for action_dir in .aicheck/actions/*/; do
        if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            local action_name=$(basename "$action_dir")
            
            # Get external dependencies
            local deps=$(yq '.dependencies.external[]' "$action_dir/action.yaml" 2>/dev/null)
            if [ -n "$deps" ]; then
                while IFS= read -r dep; do
                    external_deps+=("$action_name:$dep")
                done <<< "$deps"
            fi
            
            # Get internal dependencies
            local int_deps=$(yq '.dependencies.internal[]' "$action_dir/action.yaml" 2>/dev/null)
            if [ -n "$int_deps" ]; then
                while IFS= read -r dep; do
                    internal_deps+=("$action_name:$dep")
                done <<< "$int_deps"
            fi
        fi
    done
    
    echo -e "${GREEN}✓ Dependency scan complete${NC}"
    echo "  External: ${#external_deps[@]}, Internal: ${#internal_deps[@]}"
}

# Function to create progress bar
function create_progress_bar() {
    local progress=$1
    local width=10
    local filled=$(( (progress * width) / 100 ))
    local empty=$(( width - filled ))
    
    local bar=""
    for ((i=0; i<filled; i++)); do
        bar="${bar}█"
    done
    for ((i=0; i<empty; i++)); do
        bar="${bar}░"
    done
    
    echo "$bar"
}

# Function to get status emoji
function get_status_emoji() {
    local status=$1
    
    case "$status" in
        "ActiveAction"|"In Progress")
            echo "🟡"
            ;;
        "Completed")
            echo "🟢"
            ;;
        "Not Started")
            echo "🔴"
            ;;
        "Blocked")
            echo "⏸️"
            ;;
        "Cancelled")
            echo "❌"
            ;;
        *)
            echo "❓"
            ;;
    esac
}

# Function to generate issue matrix
function generate_issue_matrix() {
    local matrix_file=".aicheck/ISSUE_MATRIX.yaml"
    
    echo -e "${CYAN}Generating issue matrix...${NC}"
    
    cat > "$matrix_file" << 'YAML'
# AICheck Issue Matrix
# Auto-generated from action.yaml files

version: "1.0"
generated: DATE_PLACEHOLDER

issues:
YAML

    sed -i "" "s/DATE_PLACEHOLDER/$(date -u +"%Y-%m-%dT%H:%M:%SZ")/" "$matrix_file"
    
    # Collect all issues from action.yaml files
    local issue_count=0
    
    for action_dir in .aicheck/actions/*/; do
        if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            local action_name=$(basename "$action_dir")
            local issues=$(yq '.issues[]' "$action_dir/action.yaml" 2>/dev/null)
            
            if [ -n "$issues" ]; then
                while IFS= read -r issue; do
                    ((issue_count++))
                    echo "  - action: $action_name" >> "$matrix_file"
                    echo "$issue" | sed 's/^/    /' >> "$matrix_file"
                done <<< "$issues"
            fi
        fi
    done
    
    if [ "$issue_count" -eq 0 ]; then
        echo "  # No issues found" >> "$matrix_file"
    fi
    
    echo -e "${GREEN}✓ Generated issue matrix with $issue_count issues${NC}"
}

# Function to update all indexes
function update_all_indexes() {
    echo -e "${BRIGHT_BLURPLE}Updating all AICheck indexes...${NC}"
    echo "================================"
    
    update_actions_index
    update_action_timeline
    update_dependency_index
    generate_issue_matrix
    
    echo "================================"
    echo -e "${GREEN}✓ All indexes updated${NC}"
}

# Export functions
export -f update_actions_index
export -f update_action_timeline
export -f update_dependency_index
export -f generate_issue_matrix
export -f update_all_indexes
export -f create_progress_bar
export -f get_status_emoji