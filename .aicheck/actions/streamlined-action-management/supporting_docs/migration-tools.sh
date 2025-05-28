#!/bin/bash
# Migration tools for converting existing actions to the hybrid YAML format
# This preserves all existing data while adding the new action.yaml structure

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Source utilities
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/yaml-utils.sh"

# Migration functions
migrate_action() {
    local action_name="$1"
    local action_dir="${AICHECK_DIR}/actions/${action_name}"
    local yaml_file="${action_dir}/action.yaml"
    
    if [[ ! -d "$action_dir" ]]; then
        echo -e "${RED}Error: Action directory not found: ${action_dir}${NC}"
        return 1
    fi
    
    echo -e "${BLUE}Migrating action: ${action_name}${NC}"
    
    # Check if already migrated
    if [[ -f "$yaml_file" ]]; then
        echo -e "${YELLOW}Warning: action.yaml already exists. Skipping migration.${NC}"
        return 0
    fi
    
    # Create YAML structure
    cat > "$yaml_file" << EOF
# Auto-generated action.yaml for ${action_name}
# Migrated on $(date '+%Y-%m-%d %H:%M:%S')

name: ${action_name}
status: $(cat "${action_dir}/status" 2>/dev/null || echo "pending")
created: $(stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "${action_dir}" 2>/dev/null || date '+%Y-%m-%d %H:%M:%S')
updated: $(date '+%Y-%m-%d %H:%M:%S')

description: |
  $(extract_description "$action_dir")

phases:
$(extract_phases "$action_dir")

dependencies:
  external: []
  internal: []

issues: []

deployment:
  required: $(check_deployment_requirement "$action_name")
  environments: {}

testing:
  unit_tests:
    status: pending
    coverage: 0
  integration_tests:
    status: pending
  
documentation:
  readme: $(check_file_exists "${action_dir}/README.md")
  api_docs: false
  user_guide: false

git:
  branch: $(extract_git_branch "$action_name")
  commits: []
  pull_request: null

team:
  lead: "claude"
  reviewers: []
  
metadata:
  migrated: true
  migration_date: $(date '+%Y-%m-%d %H:%M:%S')
  original_format: "traditional"
EOF

    # Migrate dependencies if they exist
    migrate_dependencies "$action_dir" "$yaml_file"
    
    # Migrate todo items if todo.md exists
    migrate_todos "$action_dir" "$yaml_file"
    
    # Preserve any supporting documents references
    migrate_supporting_docs "$action_dir" "$yaml_file"
    
    echo -e "${GREEN}✓ Migration completed for ${action_name}${NC}"
}

extract_description() {
    local action_dir="$1"
    local plan_file="${action_dir}/${action_name}-plan.md"
    
    if [[ -f "$plan_file" ]]; then
        # Extract first paragraph after "## Objective" or similar
        sed -n '/^##.*Objective/,/^##/{/^##.*Objective/d;/^##/d;/^$/d;p}' "$plan_file" | head -5
    else
        echo "No description available. Please update from plan file."
    fi
}

extract_phases() {
    local action_dir="$1"
    local plan_file="${action_dir}/${action_name}-plan.md"
    local indent="  "
    
    if [[ -f "$plan_file" ]]; then
        # Look for phases section
        if grep -q "## Phases" "$plan_file"; then
            echo "${indent}# Extracted from plan file"
            sed -n '/^## Phases/,/^##/{/^## Phases/d;/^##/d;p}' "$plan_file" | while read -r line; do
                if [[ "$line" =~ ^###[[:space:]]+(.*) ]]; then
                    phase_name="${BASH_REMATCH[1]}"
                    echo "${indent}- name: \"$phase_name\""
                    echo "${indent}  status: pending"
                    echo "${indent}  tasks: []"
                elif [[ "$line" =~ ^-[[:space:]]+(.*) ]]; then
                    # Could parse tasks here if needed
                    :
                fi
            done
        else
            echo "${indent}# No phases found in plan file"
            echo "${indent}# Please define phases manually"
        fi
    else
        echo "${indent}# No plan file found"
        echo "${indent}# Please define phases based on your action plan"
    fi
}

check_deployment_requirement() {
    local action_name="$1"
    
    # Check if action name suggests deployment
    if [[ "$action_name" =~ (deploy|production|release|integration) ]]; then
        echo "true"
    else
        echo "false"
    fi
}

check_file_exists() {
    local file="$1"
    [[ -f "$file" ]] && echo "true" || echo "false"
}

extract_git_branch() {
    local action_name="$1"
    
    # Check if we're in a git repo and on a feature branch
    if git rev-parse --git-dir > /dev/null 2>&1; then
        local current_branch=$(git branch --show-current)
        if [[ "$current_branch" == *"$action_name"* ]]; then
            echo "$current_branch"
        else
            echo "main"
        fi
    else
        echo "main"
    fi
}

migrate_dependencies() {
    local action_dir="$1"
    local yaml_file="$2"
    local deps_file="${action_dir}/dependencies"
    
    if [[ -f "$deps_file" ]]; then
        echo -e "${YELLOW}  Migrating dependencies...${NC}"
        
        # Parse existing dependencies file
        local temp_yaml=$(mktemp)
        
        # Start with existing YAML
        cp "$yaml_file" "$temp_yaml"
        
        # Process each dependency line
        while IFS= read -r line; do
            if [[ "$line" =~ ^external:[[:space:]]+(.*) ]]; then
                # External dependency format: external: package==version (reason)
                local dep_info="${BASH_REMATCH[1]}"
                yaml_add_external_dependency "$temp_yaml" "$dep_info"
            elif [[ "$line" =~ ^internal:[[:space:]]+(.*) ]]; then
                # Internal dependency format: internal: action-name (type: reason)
                local dep_info="${BASH_REMATCH[1]}"
                yaml_add_internal_dependency "$temp_yaml" "$dep_info"
            fi
        done < "$deps_file"
        
        mv "$temp_yaml" "$yaml_file"
    fi
}

migrate_todos() {
    local action_dir="$1"
    local yaml_file="$2"
    local todo_file="${action_dir}/todo.md"
    
    if [[ -f "$todo_file" ]]; then
        echo -e "${YELLOW}  Migrating todos...${NC}"
        
        # Add a note about todo.md in the YAML
        local temp_yaml=$(mktemp)
        cp "$yaml_file" "$temp_yaml"
        
        # Add todo reference
        cat >> "$temp_yaml" << EOF

todos:
  source: "todo.md"
  note: "Todos are managed via Claude's TodoRead/TodoWrite in todo.md file"
EOF
        
        mv "$temp_yaml" "$yaml_file"
    fi
}

migrate_supporting_docs() {
    local action_dir="$1"
    local yaml_file="$2"
    local docs_dir="${action_dir}/supporting_docs"
    
    if [[ -d "$docs_dir" ]]; then
        echo -e "${YELLOW}  Cataloging supporting documents...${NC}"
        
        local temp_yaml=$(mktemp)
        cp "$yaml_file" "$temp_yaml"
        
        # Add supporting docs section
        echo "" >> "$temp_yaml"
        echo "supporting_docs:" >> "$temp_yaml"
        
        find "$docs_dir" -type f -name "*.md" -o -name "*.txt" -o -name "*.sh" | sort | while read -r doc; do
            local doc_name=$(basename "$doc")
            echo "  - $doc_name" >> "$temp_yaml"
        done
        
        mv "$temp_yaml" "$yaml_file"
    fi
}

yaml_add_external_dependency() {
    local yaml_file="$1"
    local dep_info="$2"
    
    # Parse format: package==version (reason)
    if [[ "$dep_info" =~ ([^=]+)==([^[:space:]]+)[[:space:]]*\((.*)\) ]]; then
        local package="${BASH_REMATCH[1]}"
        local version="${BASH_REMATCH[2]}"
        local reason="${BASH_REMATCH[3]}"
        
        # Add to YAML (this is simplified - in production use proper YAML tools)
        # For now, we'll note this needs manual adjustment
        echo "  # TODO: Manually add to dependencies.external:" >> "$yaml_file"
        echo "  # - name: $package" >> "$yaml_file"
        echo "  #   version: $version" >> "$yaml_file"
        echo "  #   justification: $reason" >> "$yaml_file"
    fi
}

yaml_add_internal_dependency() {
    local yaml_file="$1"
    local dep_info="$2"
    
    # Parse format: action-name (type: reason)
    if [[ "$dep_info" =~ ([^[:space:]]+)[[:space:]]*\(([^:]+):[[:space:]]*(.*)\) ]]; then
        local dep_action="${BASH_REMATCH[1]}"
        local dep_type="${BASH_REMATCH[2]}"
        local reason="${BASH_REMATCH[3]}"
        
        # Add to YAML (simplified)
        echo "  # TODO: Manually add to dependencies.internal:" >> "$yaml_file"
        echo "  # - action: $dep_action" >> "$yaml_file"
        echo "  #   type: $dep_type" >> "$yaml_file"
        echo "  #   description: $reason" >> "$yaml_file"
    fi
}

# Batch migration
migrate_all_actions() {
    echo -e "${BLUE}Starting batch migration of all actions...${NC}"
    
    local count=0
    local failed=0
    
    for action_dir in "${AICHECK_DIR}/actions"/*; do
        if [[ -d "$action_dir" ]]; then
            local action_name=$(basename "$action_dir")
            
            if migrate_action "$action_name"; then
                ((count++))
            else
                ((failed++))
            fi
            
            echo ""
        fi
    done
    
    echo -e "${GREEN}Migration complete: ${count} actions migrated successfully${NC}"
    if [[ $failed -gt 0 ]]; then
        echo -e "${RED}Failed migrations: ${failed}${NC}"
    fi
}

# Validation after migration
validate_migration() {
    local action_name="$1"
    local action_dir="${AICHECK_DIR}/actions/${action_name}"
    local yaml_file="${action_dir}/action.yaml"
    
    echo -e "${BLUE}Validating migration for: ${action_name}${NC}"
    
    local issues=0
    
    # Check YAML exists
    if [[ ! -f "$yaml_file" ]]; then
        echo -e "${RED}✗ action.yaml not found${NC}"
        ((issues++))
    else
        echo -e "${GREEN}✓ action.yaml exists${NC}"
    fi
    
    # Check status sync
    if [[ -f "${action_dir}/status" ]]; then
        local file_status=$(cat "${action_dir}/status")
        local yaml_status=$(yaml_read "$yaml_file" "status")
        
        if [[ "$file_status" == "$yaml_status" ]]; then
            echo -e "${GREEN}✓ Status synced correctly: ${file_status}${NC}"
        else
            echo -e "${RED}✗ Status mismatch: file=${file_status}, yaml=${yaml_status}${NC}"
            ((issues++))
        fi
    fi
    
    # Check required fields
    for field in "name" "description" "phases" "dependencies"; do
        if yaml_has_field "$yaml_file" "$field"; then
            echo -e "${GREEN}✓ Required field present: ${field}${NC}"
        else
            echo -e "${RED}✗ Required field missing: ${field}${NC}"
            ((issues++))
        fi
    done
    
    if [[ $issues -eq 0 ]]; then
        echo -e "${GREEN}✓ Migration validated successfully${NC}"
        return 0
    else
        echo -e "${RED}✗ Migration validation failed with ${issues} issues${NC}"
        return 1
    fi
}

yaml_has_field() {
    local yaml_file="$1"
    local field="$2"
    
    grep -q "^${field}:" "$yaml_file"
}

# Rollback function
rollback_migration() {
    local action_name="$1"
    local action_dir="${AICHECK_DIR}/actions/${action_name}"
    local yaml_file="${action_dir}/action.yaml"
    
    echo -e "${YELLOW}Rolling back migration for: ${action_name}${NC}"
    
    if [[ -f "$yaml_file" ]]; then
        # Check if this was a migration
        if grep -q "migrated: true" "$yaml_file"; then
            rm -f "$yaml_file"
            echo -e "${GREEN}✓ Removed action.yaml${NC}"
        else
            echo -e "${RED}✗ Not a migrated file, refusing to remove${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}No action.yaml to remove${NC}"
    fi
}

# Main migration interface
main() {
    case "${1:-}" in
        "migrate")
            if [[ -n "${2:-}" ]]; then
                migrate_action "$2"
                validate_migration "$2"
            else
                echo "Usage: $0 migrate <action-name>"
                exit 1
            fi
            ;;
        "migrate-all")
            migrate_all_actions
            ;;
        "validate")
            if [[ -n "${2:-}" ]]; then
                validate_migration "$2"
            else
                echo "Usage: $0 validate <action-name>"
                exit 1
            fi
            ;;
        "rollback")
            if [[ -n "${2:-}" ]]; then
                rollback_migration "$2"
            else
                echo "Usage: $0 rollback <action-name>"
                exit 1
            fi
            ;;
        *)
            echo "AICheck Migration Tools"
            echo ""
            echo "Usage: $0 <command> [options]"
            echo ""
            echo "Commands:"
            echo "  migrate <action>    Migrate a single action to hybrid format"
            echo "  migrate-all         Migrate all existing actions"
            echo "  validate <action>   Validate a migration"
            echo "  rollback <action>   Remove action.yaml (rollback migration)"
            ;;
    esac
}

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Set AICHECK_DIR if not already set
    export AICHECK_DIR="${AICHECK_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../" && pwd)}"
    main "$@"
fi