#!/bin/bash

# YAML Utilities for AICheck
# Provides YAML parsing functions that work with or without yq

# Check if yq is available
HAS_YQ=$(command -v yq >/dev/null 2>&1 && echo "true" || echo "false")

# Function to read a YAML value (with fallback)
function yaml_read() {
    local file=$1
    local path=$2
    local default=$3
    
    if [ ! -f "$file" ]; then
        echo "${default:-null}"
        return 1
    fi
    
    if [ "$HAS_YQ" = "true" ]; then
        # Use yq if available
        local value=$(yq "$path" "$file" 2>/dev/null)
        if [ -z "$value" ] || [ "$value" = "null" ]; then
            echo "${default:-null}"
        else
            echo "$value"
        fi
    else
        # Fallback: basic grep/sed parsing for simple cases
        case "$path" in
            .action.name)
                grep "^  name:" "$file" | sed 's/.*: *//' | tr -d '"' || echo "${default:-null}"
                ;;
            .action.status)
                grep "^  status:" "$file" | sed 's/.*: *//' | tr -d '"' || echo "${default:-null}"
                ;;
            .deployment.required)
                grep -A1 "^deployment:" "$file" | grep "required:" | sed 's/.*: *//' | tr -d '"' || echo "${default:-false}"
                ;;
            .deployment.environments.production.verified)
                grep -A5 "production:" "$file" | grep "verified:" | sed 's/.*: *//' | tr -d '"' || echo "${default:-false}"
                ;;
            *)
                echo "${default:-null}"
                ;;
        esac
    fi
}

# Function to write a YAML value (with fallback)
function yaml_write() {
    local file=$1
    local path=$2
    local value=$3
    
    if [ "$HAS_YQ" = "true" ]; then
        # Use yq if available
        yq -i "$path = \"$value\"" "$file"
    else
        # Fallback: warn user to edit manually
        echo "Warning: yq not installed. Please manually update $path in $file to: $value"
        return 1
    fi
}

# Function to add to a YAML array
function yaml_add_to_array() {
    local file=$1
    local path=$2
    local value=$3
    
    if [ "$HAS_YQ" = "true" ]; then
        # Use yq to append to array
        yq -i "$path += $value" "$file"
    else
        echo "Warning: yq not installed. Please manually add to $path in $file"
        return 1
    fi
}

# Function to create a basic action.yaml if it doesn't exist
function yaml_create_action() {
    local dir=$1
    local action_name=$2
    local status=${3:-"not_started"}
    
    if [ -f "$dir/action.yaml" ]; then
        return 0
    fi
    
    cat > "$dir/action.yaml" << YAML
version: "1.0"

action:
  name: $action_name
  status: $status
  created: $(date +"%Y-%m-%d")
  completed: null
  
files:
  plan: $action_name-plan.md
  todo: todo.md
  progress: progress.md
  
plan:
  purpose: |
    See $action_name-plan.md for details
  success_criteria: []
  
task_summary:
  total: 0
  completed: 0
  in_progress: 0
  source: todo.md
  
deployment:
  required: false
  environments:
    production:
      url: null
      last_deployed: null
      verified: false
      test_command: null
      verification_results: null
      
dependencies:
  external: []
  internal: []
  
issues: []

sync:
  last_synced: null
  sync_direction: bidirectional
  conflicts: []

notes: |
  Action YAML created $(date)
YAML
}

# Function to sync status between files
function yaml_sync_status() {
    local dir=$1
    local direction=${2:-"files-to-yaml"}  # or "yaml-to-files"
    
    if [ "$direction" = "files-to-yaml" ]; then
        # Read from status.txt and update YAML
        if [ -f "$dir/status.txt" ]; then
            local status=$(cat "$dir/status.txt")
            yaml_write "$dir/action.yaml" ".action.status" "$status"
        fi
    else
        # Read from YAML and update status.txt
        local status=$(yaml_read "$dir/action.yaml" ".action.status" "unknown")
        echo "$status" > "$dir/status.txt"
    fi
}

# Function to count tasks from todo.md
function count_todo_tasks() {
    local todo_file=$1
    
    if [ ! -f "$todo_file" ]; then
        echo "0 0 0"  # total completed in_progress
        return
    fi
    
    local total=$(grep -c "^- \[ \]" "$todo_file" 2>/dev/null || echo "0")
    local completed=$(grep -c "^- \[x\]" "$todo_file" 2>/dev/null || echo "0")
    local in_progress=$(grep -c "^- \[>\]" "$todo_file" 2>/dev/null || echo "0")  # Using [>] for in-progress
    
    echo "$total $completed $in_progress"
}

# Function to sync task counts
function yaml_sync_tasks() {
    local dir=$1
    
    if [ -f "$dir/todo.md" ]; then
        read total completed in_progress <<< $(count_todo_tasks "$dir/todo.md")
        
        yaml_write "$dir/action.yaml" ".task_summary.total" "$total"
        yaml_write "$dir/action.yaml" ".task_summary.completed" "$completed"
        yaml_write "$dir/action.yaml" ".task_summary.in_progress" "$in_progress"
    fi
}

# Function to validate action.yaml
function yaml_validate() {
    local file=$1
    
    if [ ! -f "$file" ]; then
        echo "Error: File not found: $file"
        return 1
    fi
    
    if [ "$HAS_YQ" = "true" ]; then
        # Use yq to validate
        if yq '.' "$file" >/dev/null 2>&1; then
            echo "✓ Valid YAML"
            return 0
        else
            echo "✗ Invalid YAML syntax"
            return 1
        fi
    else
        # Basic validation without yq
        if grep -q "^version:" "$file" && grep -q "^action:" "$file"; then
            echo "✓ Basic structure looks valid (install yq for full validation)"
            return 0
        else
            echo "✗ Missing required sections"
            return 1
        fi
    fi
}

# Function to merge two YAML files (for migrations)
function yaml_merge() {
    local source=$1
    local target=$2
    
    if [ "$HAS_YQ" = "true" ]; then
        # Use yq to merge
        yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' "$source" "$target" > "$target.tmp"
        mv "$target.tmp" "$target"
    else
        echo "Warning: yq required for YAML merging"
        return 1
    fi
}

# Export functions for use in other scripts
export -f yaml_read
export -f yaml_write
export -f yaml_add_to_array
export -f yaml_create_action
export -f yaml_sync_status
export -f yaml_sync_tasks
export -f yaml_validate
export -f yaml_merge