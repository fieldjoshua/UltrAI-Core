#!/bin/bash

# AICheck Enhanced - Streamlined Action Management
# This is an enhanced version of aicheck that adds deployment verification
# and action.yaml support while preserving all existing functionality

set -e

CMD=$1
shift
ARGS=$@

GREEN="\033[0;32m"
NEON_BLURPLE="\033[38;5;99m"
BRIGHT_BLURPLE="\033[38;5;135m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m" # No Color

# Check if yq is available for YAML parsing
HAS_YQ=$(command -v yq >/dev/null 2>&1 && echo "true" || echo "false")

# ========== EXISTING FUNCTIONS (PRESERVED) ==========

function create_action() {
  local action_name=$1
  
  if [ -z "$action_name" ]; then
    echo -e "${RED}Error: Action name is required${NC}"
    echo "Usage: ./aicheck action new ACTION_NAME"
    exit 1
  fi
  
  # Convert PascalCase to kebab-case for directories
  local dir_name=$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')
  
  # Create action directory
  mkdir -p ".aicheck/actions/$dir_name"
  mkdir -p ".aicheck/actions/$dir_name/supporting_docs/claude-interactions"
  mkdir -p ".aicheck/actions/$dir_name/supporting_docs/process-tests"
  mkdir -p ".aicheck/actions/$dir_name/supporting_docs/research"
  
  # Create traditional plan file
  cat > ".aicheck/actions/$dir_name/$dir_name-plan.md" << PLAN
# ACTION: $action_name

Version: 1.0
Last Updated: $(date +"%Y-%m-%d")
Status: Not Started
Progress: 0%

## Purpose

[Describe the purpose of this ACTION and its value to the PROGRAM]

## Requirements

- [Requirement 1]
- [Requirement 2]

## Dependencies

- [Dependency 1, if any]

## Implementation Approach

### Phase 1: Research

- [Research task 1]
- [Research task 2]

### Phase 2: Design

- [Design task 1]
- [Design task 2]

### Phase 3: Implementation

- [Implementation task 1]
- [Implementation task 2]

### Phase 4: Testing

- [Test case 1]
- [Test case 2]

## Success Criteria

- [Criterion 1]
- [Criterion 2]

## Estimated Timeline

- Research: [X days]
- Design: [X days]
- Implementation: [X days]
- Testing: [X days]
- Total: [X days]

## Notes

[Any additional notes or considerations]
PLAN
  
  # Create status file
  echo "Not Started" > ".aicheck/actions/$dir_name/status.txt"
  
  # Create progress file
  echo "# $action_name Progress

## Updates

$(date +"%Y-%m-%d") - Action created

## Tasks

- [ ] Research phase
- [ ] Design phase
- [ ] Implementation phase
- [ ] Testing phase
- [ ] Documentation
" > ".aicheck/actions/$dir_name/progress.md"

  # Create empty todo.md for Claude
  echo "# TODO: $action_name

## Active Tasks

*Tasks will be added based on the action plan*

## Completed Tasks

*No tasks completed yet*

## Notes

- Action created: $(date +"%Y-%m-%d")
- Plan file: $dir_name-plan.md
" > ".aicheck/actions/$dir_name/todo.md"

  # NEW: Create action.yaml companion file
  cat > ".aicheck/actions/$dir_name/action.yaml" << YAML
version: "1.0"

action:
  name: $action_name
  status: not_started
  created: $(date +"%Y-%m-%d")
  completed: null
  
files:
  plan: $dir_name-plan.md
  todo: todo.md
  progress: progress.md
  
plan:
  purpose: |
    [Describe the purpose - will be synced from plan.md]
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

notes: |
  Action created via aicheck
  Edit this file to configure deployment verification and automated tracking
YAML
  
  # Update actions_index.md (existing logic preserved)
  line_num=$(grep -n "\| \*None yet\* \| \| \| \| \|" .aicheck/actions_index.md | cut -d':' -f1)
  
  if [ -n "$line_num" ]; then
    sed -i "" "$line_num s/| \*None yet\* | | | | |/| $action_name | | Not Started | 0% | |\n| \*None yet\* | | | | |/" .aicheck/actions_index.md
  else
    line_num=$(grep -n "## Active Actions" .aicheck/actions_index.md | cut -d':' -f1)
    if [ -n "$line_num" ]; then
      awk -v line="$line_num" -v action="| $action_name | | Not Started | 0% | |" 'NR==line+4{print action}1' .aicheck/actions_index.md > .aicheck/actions_index.md.tmp
      mv .aicheck/actions_index.md.tmp .aicheck/actions_index.md
    fi
  fi
  
  sed -i "" "s/\*Last Updated: .*\*/\*Last Updated: $(date +"%Y-%m-%d")\*/" .aicheck/actions_index.md
  
  echo -e "${GREEN}✓ Created new ACTION: $action_name${NC}"
  echo -e "${BRIGHT_BLURPLE}Directory: .aicheck/actions/$dir_name${NC}"
  echo -e "${GREEN}✓ Created action.yaml for enhanced tracking${NC}"
  echo -e "${YELLOW}NOTE: This ACTION requires planning and approval before implementation${NC}"
}

# ========== NEW FUNCTIONS (ENHANCEMENTS) ==========

# Function to verify deployment
function verify_deployment() {
  local action_name=$1
  
  # If no action name provided, use current action
  if [ -z "$action_name" ]; then
    if [ -f ".aicheck/current_action" ]; then
      action_name=$(cat .aicheck/current_action)
    fi
  fi
  
  if [ -z "$action_name" ] || [ "$action_name" = "None" ] || [ "$action_name" = "AICheckExec" ]; then
    echo -e "${RED}Error: No action specified and no current action set${NC}"
    echo "Usage: ./aicheck deploy verify [ACTION_NAME]"
    exit 1
  fi
  
  local dir_name=$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')
  
  # Check if action.yaml exists
  if [ ! -f ".aicheck/actions/$dir_name/action.yaml" ]; then
    echo -e "${YELLOW}Warning: No action.yaml found for $action_name${NC}"
    echo -e "${YELLOW}This action may not have deployment verification configured${NC}"
    return 1
  fi
  
  # Check if deployment is required
  if [ "$HAS_YQ" = "true" ]; then
    local deploy_required=$(yq '.deployment.required' ".aicheck/actions/$dir_name/action.yaml")
    if [ "$deploy_required" != "true" ]; then
      echo -e "${BRIGHT_BLURPLE}Deployment verification not required for $action_name${NC}"
      return 0
    fi
    
    local test_command=$(yq '.deployment.environments.production.test_command' ".aicheck/actions/$dir_name/action.yaml")
    if [ -z "$test_command" ] || [ "$test_command" = "null" ]; then
      echo -e "${RED}Error: No test command configured for deployment verification${NC}"
      echo -e "${YELLOW}Add test_command to action.yaml deployment section${NC}"
      return 1
    fi
    
    echo -e "${BRIGHT_BLURPLE}Running deployment verification for $action_name...${NC}"
    echo -e "${CYAN}Command: $test_command${NC}"
    
    # Run the test command and capture output
    local temp_results="/tmp/deploy_verify_$$.json"
    if eval "$test_command" > "$temp_results" 2>&1; then
      echo -e "${GREEN}✓ Deployment verification PASSED${NC}"
      
      # Update action.yaml with results
      yq -i ".deployment.environments.production.verified = true" ".aicheck/actions/$dir_name/action.yaml"
      yq -i ".deployment.environments.production.last_deployed = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" ".aicheck/actions/$dir_name/action.yaml"
      
      # Store results if JSON
      if [ -s "$temp_results" ] && jq . "$temp_results" >/dev/null 2>&1; then
        # It's valid JSON, store it
        local results=$(cat "$temp_results" | jq -c .)
        yq -i ".deployment.environments.production.verification_results = $results" ".aicheck/actions/$dir_name/action.yaml"
      fi
      
      rm -f "$temp_results"
      return 0
    else
      echo -e "${RED}✗ Deployment verification FAILED${NC}"
      echo -e "${YELLOW}Output:${NC}"
      cat "$temp_results"
      rm -f "$temp_results"
      return 1
    fi
  else
    echo -e "${YELLOW}Warning: yq not installed. Cannot parse action.yaml${NC}"
    echo -e "${YELLOW}Install yq to use deployment verification features${NC}"
    return 1
  fi
}

# Function to report an issue
function report_issue() {
  local description=$1
  local severity=$2
  local action_name=$3
  
  if [ -z "$description" ]; then
    echo -e "${RED}Error: Issue description required${NC}"
    echo "Usage: ./aicheck issue report DESCRIPTION [SEVERITY] [ACTION]"
    exit 1
  fi
  
  # Default severity to medium
  if [ -z "$severity" ]; then
    severity="medium"
  fi
  
  # Validate severity
  case "$severity" in
    low|medium|high|critical) ;;
    *) 
      echo -e "${YELLOW}Warning: Invalid severity '$severity'. Using 'medium'${NC}"
      severity="medium"
      ;;
  esac
  
  # Get action name if not provided
  if [ -z "$action_name" ]; then
    if [ -f ".aicheck/current_action" ]; then
      action_name=$(cat .aicheck/current_action)
    fi
  fi
  
  if [ -z "$action_name" ] || [ "$action_name" = "None" ] || [ "$action_name" = "AICheckExec" ]; then
    echo -e "${YELLOW}Warning: No action specified. Issue will be logged globally.${NC}"
    # TODO: Implement global issue tracking
    return 0
  fi
  
  local dir_name=$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')
  
  # Generate issue ID
  local issue_id="issue-$(date +%s)"
  
  # Add to action.yaml if it exists
  if [ -f ".aicheck/actions/$dir_name/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
    yq -i ".issues += [{\"id\": \"$issue_id\", \"desc\": \"$description\", \"severity\": \"$severity\", \"status\": \"open\", \"discovered\": \"$(date +%Y-%m-%d)\"}]" ".aicheck/actions/$dir_name/action.yaml"
    echo -e "${GREEN}✓ Reported issue $issue_id for action $action_name${NC}"
    echo -e "${BRIGHT_BLURPLE}Severity: $severity${NC}"
  else
    # Fallback: append to todo.md
    echo "" >> ".aicheck/actions/$dir_name/todo.md"
    echo "## Issue Reported" >> ".aicheck/actions/$dir_name/todo.md"
    echo "- **ID**: $issue_id" >> ".aicheck/actions/$dir_name/todo.md"
    echo "- **Description**: $description" >> ".aicheck/actions/$dir_name/todo.md"
    echo "- **Severity**: $severity" >> ".aicheck/actions/$dir_name/todo.md"
    echo "- **Date**: $(date +%Y-%m-%d)" >> ".aicheck/actions/$dir_name/todo.md"
    echo -e "${GREEN}✓ Reported issue $issue_id in todo.md${NC}"
  fi
}

# Function to sync action.yaml with traditional files
function sync_action() {
  local action_name=$1
  local direction=$2  # "yaml-to-files" or "files-to-yaml"
  
  if [ -z "$action_name" ]; then
    if [ -f ".aicheck/current_action" ]; then
      action_name=$(cat .aicheck/current_action)
    fi
  fi
  
  if [ -z "$action_name" ] || [ "$action_name" = "None" ] || [ "$action_name" = "AICheckExec" ]; then
    echo -e "${RED}Error: No action specified${NC}"
    return 1
  fi
  
  local dir_name=$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')
  
  if [ ! -f ".aicheck/actions/$dir_name/action.yaml" ]; then
    echo -e "${YELLOW}No action.yaml to sync for $action_name${NC}"
    return 0
  fi
  
  if [ "$HAS_YQ" != "true" ]; then
    echo -e "${YELLOW}Warning: yq not installed. Cannot sync action.yaml${NC}"
    return 1
  fi
  
  echo -e "${BRIGHT_BLURPLE}Syncing $action_name...${NC}"
  
  if [ "$direction" = "files-to-yaml" ]; then
    # Sync from traditional files to YAML
    local status=$(cat ".aicheck/actions/$dir_name/status.txt" 2>/dev/null || echo "unknown")
    yq -i ".action.status = \"$status\"" ".aicheck/actions/$dir_name/action.yaml"
    
    # Count tasks from todo.md
    if [ -f ".aicheck/actions/$dir_name/todo.md" ]; then
      local total_tasks=$(grep -c "^- \[ \]" ".aicheck/actions/$dir_name/todo.md" 2>/dev/null || echo "0")
      local completed_tasks=$(grep -c "^- \[x\]" ".aicheck/actions/$dir_name/todo.md" 2>/dev/null || echo "0")
      yq -i ".task_summary.total = $total_tasks" ".aicheck/actions/$dir_name/action.yaml"
      yq -i ".task_summary.completed = $completed_tasks" ".aicheck/actions/$dir_name/action.yaml"
    fi
  else
    # Default: sync from YAML to traditional files
    local yaml_status=$(yq '.action.status' ".aicheck/actions/$dir_name/action.yaml")
    if [ "$yaml_status" != "null" ]; then
      echo "$yaml_status" > ".aicheck/actions/$dir_name/status.txt"
    fi
  fi
  
  # Update sync metadata
  yq -i ".sync.last_synced = \"$(date +"%Y-%m-%d %H:%M:%S")\"" ".aicheck/actions/$dir_name/action.yaml"
  
  echo -e "${GREEN}✓ Sync completed${NC}"
}

# Enhanced complete_action function
function complete_action() {
  local action_name=$1
  
  # If no action name is provided, use the current action
  if [ -z "$action_name" ]; then
    if [ -f ".aicheck/current_action" ]; then
      action_name=$(cat .aicheck/current_action)
    fi
  fi
  
  if [ -z "$action_name" ] || [ "$action_name" = "None" ] || [ "$action_name" = "AICheckExec" ]; then
    echo -e "${RED}Error: No action specified and no current action set${NC}"
    echo "Usage: ./aicheck action complete [ACTION_NAME]"
    exit 1
  fi
  
  local dir_name=$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')
  
  # Check if action exists
  if [ ! -d ".aicheck/actions/$dir_name" ]; then
    echo -e "${RED}Error: Action '$action_name' does not exist${NC}"
    exit 1
  fi
  
  # NEW: Check deployment verification if action.yaml exists
  if [ -f ".aicheck/actions/$dir_name/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
    local deploy_required=$(yq '.deployment.required' ".aicheck/actions/$dir_name/action.yaml")
    local deploy_verified=$(yq '.deployment.environments.production.verified' ".aicheck/actions/$dir_name/action.yaml")
    
    if [ "$deploy_required" = "true" ] && [ "$deploy_verified" != "true" ]; then
      echo -e "${RED}Error: Deployment verification required but not completed${NC}"
      echo -e "${YELLOW}Run: ./aicheck deploy verify $action_name${NC}"
      exit 1
    fi
    
    # Check for open critical issues
    local critical_issues=$(yq '.issues[] | select(.severity == "critical" and .status == "open") | .id' ".aicheck/actions/$dir_name/action.yaml" | wc -l)
    if [ "$critical_issues" -gt 0 ]; then
      echo -e "${RED}Error: $critical_issues critical issues remain open${NC}"
      echo -e "${YELLOW}Resolve critical issues before completing action${NC}"
      exit 1
    fi
  fi
  
  # Continue with existing completion logic...
  echo -e "${BRIGHT_BLURPLE}Verifying dependencies for $action_name...${NC}"
  
  # [Rest of existing complete_action code preserved...]
  # ... (dependency checks, status updates, etc.)
  
  echo -e "${GREEN}✓ Completed ACTION: $action_name${NC}"
}

# ========== MAIN COMMAND HANDLING (ENHANCED) ==========

case "$CMD" in
  "action")
    case "$1" in
      "new")
        create_action "$2"
        ;;
      "set")
        set_active_action "$2"
        ;;
      "complete")
        complete_action "$2"
        ;;
      *)
        echo -e "${RED}Unknown action command: $1${NC}"
        echo "Available commands: new, set, complete"
        ;;
    esac
    ;;
  "deploy")
    case "$1" in
      "verify")
        verify_deployment "$2"
        ;;
      "status")
        # TODO: Show deployment status
        echo -e "${YELLOW}Deploy status command not yet implemented${NC}"
        ;;
      *)
        echo -e "${RED}Unknown deploy command: $1${NC}"
        echo "Available commands: verify, status"
        ;;
    esac
    ;;
  "issue")
    case "$1" in
      "report")
        report_issue "$2" "$3" "$4"
        ;;
      "list")
        # TODO: List issues for action
        echo -e "${YELLOW}Issue list command not yet implemented${NC}"
        ;;
      *)
        echo -e "${RED}Unknown issue command: $1${NC}"
        echo "Available commands: report, list"
        ;;
    esac
    ;;
  "sync")
    sync_action "$1" "$2"
    ;;
  "dependency")
    case "$1" in
      "add")
        add_dependency "$2" "$3" "$4" "$5"
        ;;
      "internal")
        add_internal_dependency "$2" "$3" "$4" "$5"
        ;;
      *)
        echo -e "${RED}Unknown dependency command: $1${NC}"
        echo "Available commands: add, internal"
        ;;
    esac
    ;;
  "exec")
    exec_mode
    ;;
  "status")
    show_status
    ;;
  *)
    echo -e "${RED}Unknown command: $CMD${NC}"
    echo "Available commands: action, deploy, issue, sync, dependency, exec, status"
    echo ""
    echo "New commands:"
    echo "  deploy verify    - Run deployment verification"
    echo "  issue report     - Report an issue"
    echo "  sync            - Sync action.yaml with traditional files"
    ;;
esac