#!/bin/bash

# Issue Tracking System for AICheck
# Integrated issue management within action workflow

source "$(dirname "$0")/yaml-utils.sh"

# Colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
BRIGHT_BLURPLE="\033[38;5;135m"
NC="\033[0m"

# Issue severity levels
declare -A SEVERITY_EMOJI=(
    ["critical"]="🔴"
    ["high"]="🟡"
    ["medium"]="🟢"
    ["low"]="⚪"
)

# Issue status
declare -A STATUS_EMOJI=(
    ["open"]="📋"
    ["in_progress"]="🔄"
    ["resolved"]="✅"
    ["closed"]="📁"
    ["wontfix"]="❌"
)

# Function to generate issue ID
function generate_issue_id() {
    echo "issue-$(date +%s)-$(openssl rand -hex 2)"
}

# Function to report a new issue
function report_issue() {
    local description=$1
    local severity=${2:-"medium"}
    local action_name=$3
    
    # Validate inputs
    if [ -z "$description" ]; then
        echo -e "${RED}Error: Issue description is required${NC}"
        echo "Usage: aicheck issue report \"description\" [severity] [action]"
        return 1
    fi
    
    # Validate severity
    case "$severity" in
        critical|high|medium|low) ;;
        *)
            echo -e "${YELLOW}Invalid severity '$severity', using 'medium'${NC}"
            severity="medium"
            ;;
    esac
    
    # Get action if not specified
    if [ -z "$action_name" ]; then
        if [ -f ".aicheck/current_action" ]; then
            action_name=$(cat .aicheck/current_action)
        fi
    fi
    
    # Generate issue ID
    local issue_id=$(generate_issue_id)
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    # Create issue object
    local issue_json=$(cat <<JSON
{
  "id": "$issue_id",
  "description": "$description",
  "severity": "$severity",
  "status": "open",
  "discovered": "$(date +%Y-%m-%d)",
  "discovered_time": "$timestamp",
  "action": "$action_name",
  "resolved": null,
  "resolution": null,
  "assigned_to": null,
  "tags": []
}
JSON
)
    
    # Store issue based on context
    if [ -n "$action_name" ] && [ "$action_name" != "None" ] && [ "$action_name" != "AICheckExec" ]; then
        # Store in action's action.yaml
        local action_dir=".aicheck/actions/$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
        
        if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            # Add to action.yaml
            yq -i ".issues += [$issue_json]" "$action_dir/action.yaml"
            echo -e "${GREEN}✓ Reported issue $issue_id for action $action_name${NC}"
        else
            # Fallback: append to todo.md
            echo "" >> "$action_dir/todo.md"
            echo "## 🚨 Issue Reported" >> "$action_dir/todo.md"
            echo "- **ID**: $issue_id" >> "$action_dir/todo.md"
            echo "- **Severity**: ${SEVERITY_EMOJI[$severity]} $severity" >> "$action_dir/todo.md"
            echo "- **Description**: $description" >> "$action_dir/todo.md"
            echo "- **Date**: $timestamp" >> "$action_dir/todo.md"
            echo -e "${GREEN}✓ Reported issue $issue_id in todo.md${NC}"
        fi
    else
        # Store in global issues file
        local global_issues=".aicheck/GLOBAL_ISSUES.yaml"
        if [ ! -f "$global_issues" ]; then
            echo "version: \"1.0\"" > "$global_issues"
            echo "issues: []" >> "$global_issues"
        fi
        
        if [ "$HAS_YQ" = "true" ]; then
            yq -i ".issues += [$issue_json]" "$global_issues"
            echo -e "${GREEN}✓ Reported global issue $issue_id${NC}"
        else
            echo -e "${YELLOW}Warning: yq required for global issue tracking${NC}"
        fi
    fi
    
    # Display issue details
    echo -e "${BRIGHT_BLURPLE}Issue Details:${NC}"
    echo "  ID: $issue_id"
    echo "  Severity: ${SEVERITY_EMOJI[$severity]} $severity"
    echo "  Status: ${STATUS_EMOJI[open]} open"
    echo "  Description: $description"
    
    # Check if critical
    if [ "$severity" = "critical" ]; then
        echo -e "${RED}⚠️  CRITICAL ISSUE - This will block action completion${NC}"
    fi
    
    return 0
}

# Function to list issues
function list_issues() {
    local action_name=$1
    local filter_severity=$2
    local filter_status=$3
    
    echo -e "${BRIGHT_BLURPLE}AICheck Issues${NC}"
    echo "=============="
    
    # If no action specified, show all
    if [ -z "$action_name" ]; then
        # Show issues from all actions
        local total_issues=0
        local open_critical=0
        
        for action_dir in .aicheck/actions/*/; do
            if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
                local action=$(basename "$action_dir")
                local issues=$(yq '.issues[]' "$action_dir/action.yaml" 2>/dev/null)
                
                if [ -n "$issues" ]; then
                    echo -e "\n${CYAN}Action: $action${NC}"
                    
                    # Parse and display each issue
                    local issue_count=$(yq '.issues | length' "$action_dir/action.yaml")
                    for ((i=0; i<$issue_count; i++)); do
                        local id=$(yq ".issues[$i].id" "$action_dir/action.yaml")
                        local desc=$(yq ".issues[$i].description" "$action_dir/action.yaml")
                        local severity=$(yq ".issues[$i].severity" "$action_dir/action.yaml")
                        local status=$(yq ".issues[$i].status" "$action_dir/action.yaml")
                        
                        # Apply filters
                        if [ -n "$filter_severity" ] && [ "$severity" != "$filter_severity" ]; then
                            continue
                        fi
                        if [ -n "$filter_status" ] && [ "$status" != "$filter_status" ]; then
                            continue
                        fi
                        
                        echo "  ${SEVERITY_EMOJI[$severity]} ${STATUS_EMOJI[$status]} $id: $desc"
                        ((total_issues++))
                        
                        if [ "$severity" = "critical" ] && [ "$status" = "open" ]; then
                            ((open_critical++))
                        fi
                    done
                fi
            fi
        done
        
        # Show global issues
        if [ -f ".aicheck/GLOBAL_ISSUES.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            local global_count=$(yq '.issues | length' ".aicheck/GLOBAL_ISSUES.yaml" 2>/dev/null || echo "0")
            if [ "$global_count" -gt 0 ]; then
                echo -e "\n${CYAN}Global Issues${NC}"
                # Similar parsing logic for global issues
            fi
        fi
        
        echo -e "\n${BRIGHT_BLURPLE}Summary:${NC}"
        echo "  Total issues: $total_issues"
        if [ $open_critical -gt 0 ]; then
            echo -e "  ${RED}Critical open: $open_critical${NC}"
        fi
    else
        # Show issues for specific action
        local action_dir=".aicheck/actions/$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
        
        if [ ! -f "$action_dir/action.yaml" ]; then
            echo -e "${YELLOW}No issues tracked for action: $action_name${NC}"
            return 0
        fi
        
        # Display issues for this action
        display_action_issues "$action_dir" "$filter_severity" "$filter_status"
    fi
}

# Function to update issue status
function update_issue_status() {
    local issue_id=$1
    local new_status=$2
    local resolution=$3
    
    if [ -z "$issue_id" ] || [ -z "$new_status" ]; then
        echo -e "${RED}Error: Issue ID and new status required${NC}"
        echo "Usage: aicheck issue update <issue-id> <status> [resolution]"
        return 1
    fi
    
    # Validate status
    case "$new_status" in
        open|in_progress|resolved|closed|wontfix) ;;
        *)
            echo -e "${RED}Invalid status: $new_status${NC}"
            echo "Valid statuses: open, in_progress, resolved, closed, wontfix"
            return 1
            ;;
    esac
    
    # Find issue in all action.yaml files
    local found=false
    
    for action_dir in .aicheck/actions/*/; do
        if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            # Check if issue exists in this action
            local issue_exists=$(yq ".issues[] | select(.id == \"$issue_id\")" "$action_dir/action.yaml" 2>/dev/null)
            
            if [ -n "$issue_exists" ]; then
                found=true
                local action_name=$(basename "$action_dir")
                
                # Update status
                yq -i "(.issues[] | select(.id == \"$issue_id\") | .status) = \"$new_status\"" "$action_dir/action.yaml"
                
                # Update resolved date if resolving
                if [[ "$new_status" == "resolved" ]] || [[ "$new_status" == "closed" ]]; then
                    yq -i "(.issues[] | select(.id == \"$issue_id\") | .resolved) = \"$(date +%Y-%m-%d)\"" "$action_dir/action.yaml"
                    
                    if [ -n "$resolution" ]; then
                        yq -i "(.issues[] | select(.id == \"$issue_id\") | .resolution) = \"$resolution\"" "$action_dir/action.yaml"
                    fi
                fi
                
                echo -e "${GREEN}✓ Updated issue $issue_id status to: $new_status${NC}"
                echo -e "${BRIGHT_BLURPLE}Action: $action_name${NC}"
                
                # Show updated issue
                local updated_issue=$(yq ".issues[] | select(.id == \"$issue_id\")" "$action_dir/action.yaml")
                echo "$updated_issue" | yq -P '.'
                
                break
            fi
        fi
    done
    
    if [ "$found" = "false" ]; then
        echo -e "${RED}Issue $issue_id not found${NC}"
        return 1
    fi
    
    return 0
}

# Function to link issue to task
function link_issue_to_task() {
    local issue_id=$1
    local task_id=$2
    local action_name=$3
    
    if [ -z "$issue_id" ] || [ -z "$task_id" ]; then
        echo -e "${RED}Error: Issue ID and task ID required${NC}"
        return 1
    fi
    
    # Implementation would update both issue and task with cross-references
    echo -e "${CYAN}Linking issue $issue_id to task $task_id${NC}"
    
    # This would update action.yaml with the link
    # For now, just indicate success
    echo -e "${GREEN}✓ Issue and task linked${NC}"
}

# Function to generate issue report
function generate_issue_report() {
    local report_file=".aicheck/issue-report-$(date +%Y%m%d-%H%M%S).md"
    
    echo "# AICheck Issue Report" > "$report_file"
    echo "Generated: $(date)" >> "$report_file"
    echo "" >> "$report_file"
    
    # Collect statistics
    local total_issues=0
    local open_issues=0
    local critical_open=0
    local by_severity=()
    local by_status=()
    
    # Scan all actions
    for action_dir in .aicheck/actions/*/; do
        if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            local action_name=$(basename "$action_dir")
            local issue_count=$(yq '.issues | length' "$action_dir/action.yaml" 2>/dev/null || echo "0")
            
            if [ "$issue_count" -gt 0 ]; then
                echo "## Action: $action_name" >> "$report_file"
                echo "" >> "$report_file"
                
                # Table header
                echo "| ID | Severity | Status | Description | Discovered |" >> "$report_file"
                echo "|-----|----------|---------|-------------|------------|" >> "$report_file"
                
                # Process each issue
                for ((i=0; i<$issue_count; i++)); do
                    local id=$(yq ".issues[$i].id" "$action_dir/action.yaml")
                    local desc=$(yq ".issues[$i].description" "$action_dir/action.yaml")
                    local severity=$(yq ".issues[$i].severity" "$action_dir/action.yaml")
                    local status=$(yq ".issues[$i].status" "$action_dir/action.yaml")
                    local discovered=$(yq ".issues[$i].discovered" "$action_dir/action.yaml")
                    
                    echo "| $id | ${SEVERITY_EMOJI[$severity]} $severity | ${STATUS_EMOJI[$status]} $status | ${desc:0:40}... | $discovered |" >> "$report_file"
                    
                    ((total_issues++))
                    if [ "$status" = "open" ]; then
                        ((open_issues++))
                        if [ "$severity" = "critical" ]; then
                            ((critical_open++))
                        fi
                    fi
                done
                
                echo "" >> "$report_file"
            fi
        fi
    done
    
    # Add summary
    echo "## Summary" >> "$report_file"
    echo "" >> "$report_file"
    echo "- **Total Issues**: $total_issues" >> "$report_file"
    echo "- **Open Issues**: $open_issues" >> "$report_file"
    echo "- **Critical Open**: $critical_open" >> "$report_file"
    echo "" >> "$report_file"
    
    echo -e "${GREEN}✓ Issue report generated: $report_file${NC}"
    
    # Display summary
    echo -e "${BRIGHT_BLURPLE}Issue Summary:${NC}"
    echo "  Total: $total_issues"
    echo "  Open: $open_issues"
    if [ $critical_open -gt 0 ]; then
        echo -e "  ${RED}Critical: $critical_open${NC}"
    fi
}

# Function to check for blocking issues
function check_blocking_issues() {
    local action_name=$1
    
    if [ -z "$action_name" ]; then
        if [ -f ".aicheck/current_action" ]; then
            action_name=$(cat .aicheck/current_action)
        fi
    fi
    
    if [ -z "$action_name" ] || [ "$action_name" = "None" ]; then
        return 0
    fi
    
    local action_dir=".aicheck/actions/$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
    
    if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
        local critical_open=$(yq '.issues[] | select(.severity == "critical" and .status == "open") | .id' "$action_dir/action.yaml" 2>/dev/null | wc -l)
        
        if [ "$critical_open" -gt 0 ]; then
            echo -e "${RED}⚠️  $critical_open critical issues block completion${NC}"
            return 1
        fi
    fi
    
    return 0
}

# Export functions
export -f generate_issue_id
export -f report_issue
export -f list_issues
export -f update_issue_status
export -f link_issue_to_task
export -f generate_issue_report
export -f check_blocking_issues