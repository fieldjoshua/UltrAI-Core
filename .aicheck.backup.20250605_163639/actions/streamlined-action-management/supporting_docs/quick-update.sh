#!/bin/bash

# AICheck Quick Update Script
# This script helps update AICheck with enhanced features

set -e

GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m"

echo -e "${CYAN}AICheck Enhancement Quick Update${NC}"
echo "=================================="

# Step 1: Check prerequisites
echo -e "\n${YELLOW}Checking prerequisites...${NC}"

# Check for yq
if ! command -v yq &> /dev/null; then
    echo -e "${RED}❌ yq not found${NC}"
    echo "Please install yq first:"
    echo "  macOS: brew install yq"
    echo "  Linux: wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64"
    exit 1
else
    echo -e "${GREEN}✓ yq found${NC}"
fi

# Check for jq (optional)
if ! command -v jq &> /dev/null; then
    echo -e "${YELLOW}⚠ jq not found (optional but recommended)${NC}"
else
    echo -e "${GREEN}✓ jq found${NC}"
fi

# Step 2: Backup
echo -e "\n${YELLOW}Creating backup...${NC}"
BACKUP_DIR=".aicheck_backup_$(date +%Y%m%d_%H%M%S)"
cp -r .aicheck "$BACKUP_DIR"
echo -e "${GREEN}✓ Backup created: $BACKUP_DIR${NC}"

# Step 3: Check current state
echo -e "\n${YELLOW}Checking current AICheck state...${NC}"
if [ -f "./aicheck" ]; then
    echo -e "${GREEN}✓ aicheck script found${NC}"
    
    # Check if already enhanced
    if grep -q "deploy verify" ./aicheck; then
        echo -e "${YELLOW}⚠ AICheck appears to already have enhancements${NC}"
        echo -n "Continue anyway? (y/n): "
        read -r response
        if [[ "$response" != "y" ]]; then
            echo "Update cancelled"
            exit 0
        fi
    fi
else
    echo -e "${RED}❌ aicheck script not found${NC}"
    echo "Please run from the project root directory"
    exit 1
fi

# Step 4: Add enhancements
echo -e "\n${YELLOW}Adding enhancement functions...${NC}"

# Create a patch file with just the new functions
cat > /tmp/aicheck_enhancements.patch << 'PATCH'
# ========== NEW FUNCTIONS (ENHANCEMENTS) ==========

# Function to verify deployment
function verify_deployment() {
  local action_name=$1
  
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
  
  if [ ! -f ".aicheck/actions/$dir_name/action.yaml" ]; then
    echo -e "${YELLOW}Warning: No action.yaml found for $action_name${NC}"
    echo -e "${YELLOW}This action may not have deployment verification configured${NC}"
    return 1
  fi
  
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
    
    local temp_results="/tmp/deploy_verify_$$.json"
    if eval "$test_command" > "$temp_results" 2>&1; then
      echo -e "${GREEN}✓ Deployment verification PASSED${NC}"
      
      yq -i ".deployment.environments.production.verified = true" ".aicheck/actions/$dir_name/action.yaml"
      yq -i ".deployment.environments.production.last_deployed = \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\"" ".aicheck/actions/$dir_name/action.yaml"
      
      if [ -s "$temp_results" ] && jq . "$temp_results" >/dev/null 2>&1; then
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
    return 1
  fi
}

# Function to run system diagnostics
function doctor() {
  echo -e "${BRIGHT_BLURPLE}AICheck System Diagnostics${NC}"
  echo "=========================="
  
  local issues=0
  
  # Check for required directories
  echo -e "\n${CYAN}Checking directory structure...${NC}"
  for dir in ".aicheck" ".aicheck/actions" ".aicheck/hooks"; do
    if [ -d "$dir" ]; then
      echo -e "${GREEN}✓ $dir exists${NC}"
    else
      echo -e "${RED}❌ $dir missing${NC}"
      ((issues++))
    fi
  done
  
  # Check for required files
  echo -e "\n${CYAN}Checking core files...${NC}"
  for file in ".aicheck/current_action" ".aicheck/actions_index.md"; do
    if [ -f "$file" ]; then
      echo -e "${GREEN}✓ $file exists${NC}"
    else
      echo -e "${YELLOW}⚠ $file missing (will be created when needed)${NC}"
    fi
  done
  
  # Check YAML support
  echo -e "\n${CYAN}Checking YAML support...${NC}"
  if [ "$HAS_YQ" = "true" ]; then
    echo -e "${GREEN}✓ yq installed$(NC)"
  else
    echo -e "${YELLOW}⚠ yq not installed (reduced functionality)${NC}"
    ((issues++))
  fi
  
  # Check for action.yaml in existing actions
  echo -e "\n${CYAN}Checking action.yaml adoption...${NC}"
  local total_actions=0
  local yaml_actions=0
  
  for action_dir in .aicheck/actions/*/; do
    if [ -d "$action_dir" ]; then
      ((total_actions++))
      if [ -f "$action_dir/action.yaml" ]; then
        ((yaml_actions++))
      fi
    fi
  done
  
  if [ $total_actions -gt 0 ]; then
    echo -e "${CYAN}Actions with action.yaml: $yaml_actions/$total_actions${NC}"
    if [ $yaml_actions -lt $total_actions ]; then
      echo -e "${YELLOW}⚠ Some actions missing action.yaml${NC}"
      echo -e "${YELLOW}  Run: ./aicheck migrate all${NC}"
    fi
  fi
  
  # Summary
  echo -e "\n${CYAN}Summary:${NC}"
  if [ $issues -eq 0 ]; then
    echo -e "${GREEN}✓ No issues found${NC}"
  else
    echo -e "${YELLOW}⚠ $issues issues found${NC}"
  fi
}
PATCH

# Apply the patch (simplified - just showing what would be added)
echo -e "${CYAN}The following functions would be added to aicheck:${NC}"
echo "  - verify_deployment() - Run deployment verification"
echo "  - doctor() - System health diagnostics"
echo "  - report_issue() - Issue tracking"
echo "  - sync_action() - YAML/file synchronization"

# Step 5: Migrate existing actions
echo -e "\n${YELLOW}Checking existing actions for migration...${NC}"
ACTION_COUNT=0
MIGRATED_COUNT=0

for action_dir in .aicheck/actions/*/; do
  if [ -d "$action_dir" ]; then
    ((ACTION_COUNT++))
    if [ ! -f "$action_dir/action.yaml" ]; then
      action_name=$(basename "$action_dir")
      echo -e "${CYAN}Would create action.yaml for: $action_name${NC}"
      ((MIGRATED_COUNT++))
    fi
  fi
done

echo -e "${GREEN}✓ Found $ACTION_COUNT actions, $MIGRATED_COUNT need migration${NC}"

# Step 6: Summary
echo -e "\n${CYAN}Update Summary${NC}"
echo "=============="
echo "This update would:"
echo "  ✓ Add deployment verification commands"
echo "  ✓ Add issue tracking capabilities"
echo "  ✓ Add YAML-based automation"
echo "  ✓ Preserve all existing functionality"
echo "  ✓ Create action.yaml for $MIGRATED_COUNT existing actions"

echo -e "\n${YELLOW}Ready to proceed with update?${NC}"
echo "Note: You can always rollback using the backup in $BACKUP_DIR"
echo -n "Continue? (y/n): "
read -r response

if [[ "$response" != "y" ]]; then
    echo "Update cancelled"
    exit 0
fi

echo -e "\n${GREEN}✓ Update would be applied${NC}"
echo -e "${CYAN}Next steps:${NC}"
echo "1. Review the enhanced aicheck script in supporting_docs/"
echo "2. Test new commands with a test action"
echo "3. Gradually adopt for existing actions"
echo "4. Update team documentation"

echo -e "\n${GREEN}Update preparation complete!${NC}"