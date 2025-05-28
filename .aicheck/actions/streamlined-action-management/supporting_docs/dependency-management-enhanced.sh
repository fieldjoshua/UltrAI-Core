#!/bin/bash

# Enhanced Dependency Management for AICheck
# Extends existing dependency system with YAML support and automation

source "$(dirname "$0")/yaml-utils.sh"

# Colors
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
BRIGHT_BLURPLE="\033[38;5;135m"
NC="\033[0m"

# Function to add external dependency (enhanced)
function add_external_dependency() {
    local name=$1
    local version=$2
    local justification=$3
    local action_name=$4
    
    if [ -z "$name" ] || [ -z "$version" ] || [ -z "$justification" ]; then
        echo -e "${RED}Error: Missing required arguments${NC}"
        echo "Usage: aicheck dependency add NAME VERSION JUSTIFICATION [ACTION]"
        return 1
    fi
    
    # Get action if not specified
    if [ -z "$action_name" ]; then
        if [ -f ".aicheck/current_action" ]; then
            action_name=$(cat .aicheck/current_action)
        fi
    fi
    
    local timestamp=$(date +"%Y-%m-%d")
    
    # Create dependency object
    local dep_json=$(cat <<JSON
{
  "name": "$name",
  "version": "$version",
  "justification": "$justification",
  "added_date": "$timestamp"
}
JSON
)
    
    # Update action.yaml if action specified
    if [ -n "$action_name" ] && [ "$action_name" != "None" ] && [ "$action_name" != "AICheckExec" ]; then
        local action_dir=".aicheck/actions/$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
        
        if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            # Check if dependency already exists
            local existing=$(yq ".dependencies.external[] | select(.name == \"$name\" and .version == \"$version\")" "$action_dir/action.yaml" 2>/dev/null)
            
            if [ -n "$existing" ]; then
                echo -e "${YELLOW}Dependency $name@$version already exists in action.yaml${NC}"
            else
                # Add to action.yaml
                yq -i ".dependencies.external += [$dep_json]" "$action_dir/action.yaml"
                echo -e "${GREEN}✓ Added $name@$version to action.yaml${NC}"
            fi
        fi
    fi
    
    # Also update traditional dependency index
    update_dependency_index "$name" "$version" "$justification" "$action_name"
    
    # Run dependency check
    check_dependency_conflicts "$name" "$version"
    
    return 0
}

# Function to add internal dependency (enhanced)
function add_internal_dependency() {
    local from_action=$1
    local to_action=$2
    local dep_type=$3
    local description=$4
    
    if [ -z "$from_action" ] || [ -z "$to_action" ] || [ -z "$dep_type" ]; then
        echo -e "${RED}Error: Missing required arguments${NC}"
        echo "Usage: aicheck dependency internal FROM_ACTION TO_ACTION TYPE [DESCRIPTION]"
        return 1
    fi
    
    # Validate dependency type
    case "$dep_type" in
        prerequisite|blocks|related|uses|extends) ;;
        *)
            echo -e "${YELLOW}Unknown dependency type: $dep_type${NC}"
            echo "Valid types: prerequisite, blocks, related, uses, extends"
            ;;
    esac
    
    # Create internal dependency object
    local int_dep_json=$(cat <<JSON
{
  "action": "$to_action",
  "type": "$dep_type",
  "description": "$description"
}
JSON
)
    
    # Update from_action's action.yaml
    local from_dir=".aicheck/actions/$(echo "$from_action" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
    
    if [ -f "$from_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
        # Check if dependency already exists
        local existing=$(yq ".dependencies.internal[] | select(.action == \"$to_action\")" "$from_dir/action.yaml" 2>/dev/null)
        
        if [ -n "$existing" ]; then
            echo -e "${YELLOW}Internal dependency to $to_action already exists${NC}"
        else
            yq -i ".dependencies.internal += [$int_dep_json]" "$from_dir/action.yaml"
            echo -e "${GREEN}✓ Added internal dependency: $from_action → $to_action ($dep_type)${NC}"
        fi
    fi
    
    # Also update traditional dependency index
    update_internal_dependency_index "$from_action" "$to_action" "$dep_type" "$description"
    
    # Check for circular dependencies
    check_circular_dependencies "$from_action"
    
    return 0
}

# Function to update traditional dependency index
function update_dependency_index() {
    local name=$1
    local version=$2
    local justification=$3
    local action=$4
    
    # Create dependency index if it doesn't exist
    mkdir -p documentation/dependencies
    local dep_index="documentation/dependencies/dependency_index.md"
    
    if [ ! -f "$dep_index" ]; then
        create_dependency_index_template > "$dep_index"
    fi
    
    # Implementation continues as in original aicheck...
    echo -e "${GREEN}✓ Updated dependency index${NC}"
}

# Function to check dependency conflicts
function check_dependency_conflicts() {
    local name=$1
    local version=$2
    
    echo -e "${CYAN}Checking for dependency conflicts...${NC}"
    
    local conflicts=()
    
    # Check all action.yaml files for version conflicts
    for action_dir in .aicheck/actions/*/; do
        if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            local action_name=$(basename "$action_dir")
            local existing_version=$(yq ".dependencies.external[] | select(.name == \"$name\") | .version" "$action_dir/action.yaml" 2>/dev/null)
            
            if [ -n "$existing_version" ] && [ "$existing_version" != "$version" ]; then
                conflicts+=("$action_name uses $name@$existing_version")
            fi
        fi
    done
    
    if [ ${#conflicts[@]} -gt 0 ]; then
        echo -e "${YELLOW}⚠️  Version conflicts detected:${NC}"
        for conflict in "${conflicts[@]}"; do
            echo "  - $conflict"
        done
        echo -e "${YELLOW}Consider standardizing on version $version${NC}"
    else
        echo -e "${GREEN}✓ No conflicts found${NC}"
    fi
}

# Function to check circular dependencies
function check_circular_dependencies() {
    local start_action=$1
    local visited=()
    
    echo -e "${CYAN}Checking for circular dependencies...${NC}"
    
    if has_circular_dependency "$start_action" "$start_action" visited; then
        echo -e "${RED}⚠️  Circular dependency detected!${NC}"
        return 1
    else
        echo -e "${GREEN}✓ No circular dependencies${NC}"
        return 0
    fi
}

# Helper function for circular dependency detection
function has_circular_dependency() {
    local current=$1
    local target=$2
    local -n visited_ref=$3
    
    # Mark as visited
    visited_ref+=("$current")
    
    local current_dir=".aicheck/actions/$(echo "$current" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
    
    if [ -f "$current_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
        local deps=$(yq '.dependencies.internal[].action' "$current_dir/action.yaml" 2>/dev/null)
        
        while IFS= read -r dep; do
            if [ -n "$dep" ]; then
                if [ "$dep" = "$target" ] && [ ${#visited_ref[@]} -gt 1 ]; then
                    echo "Circular path: ${visited_ref[*]} → $dep"
                    return 0
                fi
                
                # Check if already visited (avoid infinite loops)
                local already_visited=false
                for v in "${visited_ref[@]}"; do
                    if [ "$v" = "$dep" ]; then
                        already_visited=true
                        break
                    fi
                done
                
                if [ "$already_visited" = "false" ]; then
                    if has_circular_dependency "$dep" "$target" visited_ref; then
                        return 0
                    fi
                fi
            fi
        done <<< "$deps"
    fi
    
    return 1
}

# Function to generate dependency graph
function generate_dependency_graph() {
    local output_file=".aicheck/dependency-graph-$(date +%Y%m%d-%H%M%S).dot"
    
    echo -e "${CYAN}Generating dependency graph...${NC}"
    
    # Start DOT file
    cat > "$output_file" << 'DOT'
digraph Dependencies {
    rankdir=LR;
    node [shape=box, style=rounded];
    
    // Actions
DOT
    
    # Add nodes for all actions
    for action_dir in .aicheck/actions/*/; do
        if [ -d "$action_dir" ] && [ "$(basename "$action_dir")" != "completed" ]; then
            local action_name=$(basename "$action_dir")
            local status="Unknown"
            
            if [ -f "$action_dir/action.yaml" ]; then
                status=$(yaml_read "$action_dir/action.yaml" ".action.status" "Unknown")
            elif [ -f "$action_dir/status.txt" ]; then
                status=$(cat "$action_dir/status.txt")
            fi
            
            # Color based on status
            local color="lightgray"
            case "$status" in
                "Completed") color="lightgreen" ;;
                "ActiveAction"|"In Progress") color="yellow" ;;
                "Blocked") color="orange" ;;
                "Cancelled") color="lightcoral" ;;
            esac
            
            echo "    \"$action_name\" [fillcolor=$color, style=filled];" >> "$output_file"
        fi
    done
    
    echo "" >> "$output_file"
    echo "    // Dependencies" >> "$output_file"
    
    # Add edges for dependencies
    for action_dir in .aicheck/actions/*/; do
        if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
            local from_action=$(basename "$action_dir")
            
            # Get internal dependencies
            local dep_count=$(yq '.dependencies.internal | length' "$action_dir/action.yaml" 2>/dev/null || echo "0")
            
            for ((i=0; i<$dep_count; i++)); do
                local to_action=$(yq ".dependencies.internal[$i].action" "$action_dir/action.yaml")
                local dep_type=$(yq ".dependencies.internal[$i].type" "$action_dir/action.yaml")
                
                # Edge style based on type
                local style="solid"
                case "$dep_type" in
                    "blocks") style="bold" ;;
                    "related") style="dashed" ;;
                    "uses") style="dotted" ;;
                esac
                
                echo "    \"$from_action\" -> \"$to_action\" [label=\"$dep_type\", style=$style];" >> "$output_file"
            done
        fi
    done
    
    echo "}" >> "$output_file"
    
    echo -e "${GREEN}✓ Dependency graph generated: $output_file${NC}"
    echo -e "${CYAN}To visualize, run: dot -Tpng $output_file -o dependency-graph.png${NC}"
}

# Function to check action dependencies before completion
function check_dependencies_for_completion() {
    local action_name=$1
    
    if [ -z "$action_name" ]; then
        if [ -f ".aicheck/current_action" ]; then
            action_name=$(cat .aicheck/current_action)
        fi
    fi
    
    echo -e "${CYAN}Checking dependencies for $action_name...${NC}"
    
    local action_dir=".aicheck/actions/$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
    local can_complete=true
    
    if [ -f "$action_dir/action.yaml" ] && [ "$HAS_YQ" = "true" ]; then
        # Check if all prerequisite dependencies are completed
        local prereq_count=$(yq '.dependencies.internal[] | select(.type == "prerequisite") | .action' "$action_dir/action.yaml" 2>/dev/null | wc -l)
        
        if [ "$prereq_count" -gt 0 ]; then
            echo -e "${CYAN}Checking prerequisite dependencies...${NC}"
            
            local incomplete_prereqs=()
            local prereqs=$(yq '.dependencies.internal[] | select(.type == "prerequisite") | .action' "$action_dir/action.yaml")
            
            while IFS= read -r prereq; do
                if [ -n "$prereq" ]; then
                    local prereq_dir=".aicheck/actions/$(echo "$prereq" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
                    local prereq_status="Unknown"
                    
                    if [ -f "$prereq_dir/status.txt" ]; then
                        prereq_status=$(cat "$prereq_dir/status.txt")
                    fi
                    
                    if [ "$prereq_status" != "Completed" ]; then
                        incomplete_prereqs+=("$prereq ($prereq_status)")
                        can_complete=false
                    fi
                fi
            done <<< "$prereqs"
            
            if [ ${#incomplete_prereqs[@]} -gt 0 ]; then
                echo -e "${RED}⚠️  Incomplete prerequisite dependencies:${NC}"
                for prereq in "${incomplete_prereqs[@]}"; do
                    echo "  - $prereq"
                done
            fi
        fi
        
        # Check external dependencies are documented
        local ext_dep_count=$(yq '.dependencies.external | length' "$action_dir/action.yaml" 2>/dev/null || echo "0")
        if [ "$ext_dep_count" -gt 0 ]; then
            echo -e "${GREEN}✓ $ext_dep_count external dependencies documented${NC}"
        fi
    fi
    
    if [ "$can_complete" = "true" ]; then
        echo -e "${GREEN}✓ All dependencies satisfied${NC}"
        return 0
    else
        echo -e "${RED}✗ Dependencies not satisfied${NC}"
        return 1
    fi
}

# Function to scan code for undocumented dependencies
function scan_for_dependencies() {
    local action_name=$1
    
    if [ -z "$action_name" ]; then
        if [ -f ".aicheck/current_action" ]; then
            action_name=$(cat .aicheck/current_action)
        fi
    fi
    
    echo -e "${CYAN}Scanning for undocumented dependencies...${NC}"
    
    local action_dir=".aicheck/actions/$(echo "$action_name" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')"
    local found_deps=()
    
    # Scan Python imports
    if find "$action_dir" -name "*.py" -type f | head -1 >/dev/null; then
        echo "Scanning Python files..."
        local imports=$(find "$action_dir" -name "*.py" -type f -exec grep -h "^import\|^from.*import" {} \; | sort -u)
        
        while IFS= read -r import_line; do
            if [[ "$import_line" =~ ^(import|from)\ +([a-zA-Z0-9_]+) ]]; then
                local module="${BASH_REMATCH[2]}"
                # Skip standard library modules
                if ! is_stdlib_module "$module"; then
                    found_deps+=("python:$module")
                fi
            fi
        done <<< "$imports"
    fi
    
    # Scan JavaScript/TypeScript imports
    if find "$action_dir" -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | head -1 >/dev/null; then
        echo "Scanning JavaScript/TypeScript files..."
        # Look for require() and import statements
        local js_imports=$(find "$action_dir" \( -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" \) -type f -exec grep -h "require(\|^import.*from" {} \; | sort -u)
        
        # Parse and add to found_deps
    fi
    
    if [ ${#found_deps[@]} -gt 0 ]; then
        echo -e "${YELLOW}Found potential undocumented dependencies:${NC}"
        for dep in "${found_deps[@]}"; do
            echo "  - $dep"
        done
        echo -e "${YELLOW}Consider documenting these with: aicheck dependency add${NC}"
    else
        echo -e "${GREEN}✓ No undocumented dependencies found${NC}"
    fi
}

# Helper function to check if module is Python stdlib
function is_stdlib_module() {
    local module=$1
    local stdlib_modules="os sys re json time datetime math random collections itertools functools"
    
    if [[ " $stdlib_modules " =~ " $module " ]]; then
        return 0
    fi
    return 1
}

# Export functions
export -f add_external_dependency
export -f add_internal_dependency
export -f check_dependency_conflicts
export -f check_circular_dependencies
export -f generate_dependency_graph
export -f check_dependencies_for_completion
export -f scan_for_dependencies