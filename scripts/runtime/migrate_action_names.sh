#!/bin/bash

# AICheck Action Name Migration Script
# Converts existing PascalCase action directories to kebab-case

GREEN="\033[0;32m"
YELLOW="\033[0;33m"
NEON_BLURPLE="\033[38;5;99m"      # Neon blurple highlight color
BRIGHT_BLURPLE="\033[38;5;135m"   # Bright blurple for text
RED="\033[0;31m"
CYAN="\033[0;36m"
NC="\033[0m"

echo -e "${BRIGHT_BLURPLE}AICheck Action Name Migration${NC}"
echo "Converting PascalCase action directories to kebab-case..."
echo ""

if [ ! -d ".aicheck/actions" ]; then
  echo -e "${RED}Error: .aicheck/actions directory not found${NC}"
  exit 1
fi

migrated_count=0
for dir in .aicheck/actions/*/; do
  if [ -d "$dir" ]; then
    action_dir=$(basename "$dir")
    # Convert PascalCase to kebab-case
    kebab_name=$(echo "$action_dir" | sed 's/\([a-z0-9]\)\([A-Z]\)/\1-\2/g' | tr '[:upper:]' '[:lower:]')
    
    if [ "$action_dir" != "$kebab_name" ]; then
      echo -e "${YELLOW}Migrating: $action_dir -> $kebab_name${NC}"
      
      # Create new directory with kebab-case name
      if [ ! -d ".aicheck/actions/$kebab_name" ]; then
        mv ".aicheck/actions/$action_dir" ".aicheck/actions/$kebab_name"
        
        # Update plan file name if it exists
        old_plan=".aicheck/actions/$kebab_name/$action_dir-plan.md"
        new_plan=".aicheck/actions/$kebab_name/$kebab_name-plan.md"
        if [ -f "$old_plan" ]; then
          mv "$old_plan" "$new_plan"
        fi
        
        # Update current_action file if it points to the old name
        if [ -f ".aicheck/current_action" ] && [ "$(cat .aicheck/current_action)" = "$action_dir" ]; then
          echo "$kebab_name" > .aicheck/current_action
          echo -e "${BRIGHT_BLURPLE}Updated current action reference${NC}"
        fi
        
        migrated_count=$((migrated_count + 1))
      else
        echo -e "${RED}Warning: Target directory $kebab_name already exists, skipping${NC}"
      fi
    fi
  fi
done

if [ $migrated_count -eq 0 ]; then
  echo -e "${GREEN}✓ No PascalCase directories found - all actions already use kebab-case${NC}"
else
  echo ""
  echo -e "${GREEN}✓ Migration complete! Migrated $migrated_count action directories${NC}"
  echo -e "${BRIGHT_BLURPLE}All action directories now use kebab-case naming convention${NC}"
fi
