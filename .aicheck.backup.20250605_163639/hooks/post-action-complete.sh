#!/bin/bash
# post-action-complete.sh - Git hook to remind editors about documentation requirements
# This hook is triggered when an action is marked as complete

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the action name from the commit message or aicheck command
ACTION_NAME=""
if [[ "$1" == "action" && "$2" == "complete" ]]; then
    ACTION_NAME="$3"
elif [[ -f ".aicheck/current_action" ]]; then
    ACTION_NAME=$(cat .aicheck/current_action)
fi

if [[ -z "$ACTION_NAME" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Could not determine completed action name${NC}"
    exit 0
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ ACTION COMPLETION CHECKLIST for: ${ACTION_NAME}${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"

# Check if action directory exists
ACTION_DIR=".aicheck/actions/${ACTION_NAME}"
if [[ ! -d "$ACTION_DIR" ]]; then
    ACTION_DIR=".aicheck/actions/completed/${ACTION_NAME}"
fi

CHECKS_PASSED=true

# 1. Check for supporting docs that need migration
echo -e "\n${YELLOW}📚 1. DOCUMENTATION MIGRATION CHECK${NC}"
if [[ -d "$ACTION_DIR/supporting_docs" ]]; then
    echo "   Found supporting_docs directory. Checking for universal documentation..."
    
    # List potential files for migration
    UNIVERSAL_DOCS=()
    for file in "$ACTION_DIR/supporting_docs"/*.md; do
        if [[ -f "$file" ]]; then
            # Check if file contains universal/enduring content (heuristic)
            if grep -q -i "architecture\|api\|deployment\|configuration\|user guide\|system design" "$file" 2>/dev/null; then
                UNIVERSAL_DOCS+=("$file")
            fi
        fi
    done
    
    if [[ ${#UNIVERSAL_DOCS[@]} -gt 0 ]]; then
        echo -e "${RED}   ⚠️  Found documentation that may need migration:${NC}"
        for doc in "${UNIVERSAL_DOCS[@]}"; do
            echo "      - $(basename "$doc")"
        done
        echo -e "${YELLOW}   Please review and migrate to appropriate /documentation/ subdirectory${NC}"
        CHECKS_PASSED=false
    else
        echo -e "${GREEN}   ✓ No universal documentation found requiring migration${NC}"
    fi
else
    echo -e "${GREEN}   ✓ No supporting_docs directory found${NC}"
fi

# 2. Check actions_index.md
echo -e "\n${YELLOW}📋 2. ACTIONS INDEX UPDATE CHECK${NC}"
if grep -q "$ACTION_NAME" .aicheck/actions_index.md; then
    # Check if it's marked as completed
    if grep -q "| $ACTION_NAME.*Completed" .aicheck/actions_index.md || \
       grep -q "| .*$ACTION_NAME.*| - | 2025.* |" .aicheck/actions_index.md; then
        echo -e "${GREEN}   ✓ Action found in completed section of actions_index.md${NC}"
    else
        echo -e "${RED}   ⚠️  Action found but not marked as completed in actions_index.md${NC}"
        echo "   Please update the action status to 'Completed' with completion date"
        CHECKS_PASSED=false
    fi
else
    echo -e "${RED}   ⚠️  Action not found in actions_index.md${NC}"
    echo "   Please add to completed actions section with completion details"
    CHECKS_PASSED=false
fi

# 3. Check ACTION_TIMELINE.md
echo -e "\n${YELLOW}📅 3. ACTION TIMELINE UPDATE CHECK${NC}"
if [[ -f ".aicheck/ACTION_TIMELINE.md" ]]; then
    if grep -q "## $(date +%Y-%m-%d): $ACTION_NAME" .aicheck/ACTION_TIMELINE.md || \
       grep -q "$ACTION_NAME" .aicheck/ACTION_TIMELINE.md | grep -q "✅ COMPLETED"; then
        echo -e "${GREEN}   ✓ Action found in ACTION_TIMELINE.md${NC}"
    else
        echo -e "${RED}   ⚠️  Action completion not recorded in ACTION_TIMELINE.md${NC}"
        echo "   Please add completion entry with:"
        echo "   - Status: ✅ COMPLETED"
        echo "   - Philosophy: Brief description of approach"
        echo "   - Accomplished: What was achieved"
        echo "   - Key Connections: Technical integration points"
        echo "   - Impact: Effect on the system"
        CHECKS_PASSED=false
    fi
else
    echo -e "${RED}   ⚠️  ACTION_TIMELINE.md not found${NC}"
    CHECKS_PASSED=false
fi

# 4. Check for dependencies
echo -e "\n${YELLOW}🔗 4. DEPENDENCY DOCUMENTATION CHECK${NC}"
DEPS_FILE="$ACTION_DIR/dependencies.md"
if [[ -f "$DEPS_FILE" ]] || grep -q "dependency add\|dependency internal" "$ACTION_DIR"/*.md 2>/dev/null; then
    echo -e "${YELLOW}   ℹ️  Action has dependencies - ensure they are documented with:${NC}"
    echo "   - External: ./aicheck dependency add NAME VERSION JUSTIFICATION"
    echo "   - Internal: ./aicheck dependency internal DEP_ACTION ACTION TYPE DESCRIPTION"
else
    echo -e "${GREEN}   ✓ No explicit dependencies found${NC}"
fi

# 5. Check if action needs to be moved to completed
echo -e "\n${YELLOW}📁 5. ACTION DIRECTORY MIGRATION CHECK${NC}"
if [[ -d ".aicheck/actions/$ACTION_NAME" ]]; then
    echo -e "${YELLOW}   ℹ️  Action directory should be moved to .aicheck/actions/completed/${NC}"
    echo "   Run: mv .aicheck/actions/$ACTION_NAME .aicheck/actions/completed/"
    CHECKS_PASSED=false
elif [[ -d ".aicheck/actions/completed/$ACTION_NAME" ]]; then
    echo -e "${GREEN}   ✓ Action directory already in completed folder${NC}"
else
    echo -e "${RED}   ⚠️  Action directory not found${NC}"
fi

# Summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
if [[ "$CHECKS_PASSED" == "true" ]]; then
    echo -e "${GREEN}✅ All completion requirements satisfied!${NC}"
else
    echo -e "${RED}❌ COMPLETION REQUIREMENTS NOT MET${NC}"
    echo -e "${YELLOW}Please address the items above before finalizing action completion${NC}"
    echo -e "\n${YELLOW}Required per RULES.md Section 6.1 (Action Lifecycle):${NC}"
    echo "  8. Completion: ACTION marked complete, documents migrated"
    echo "  9. Timeline Update: Update ACTION_TIMELINE.md with completion details"
    echo "  10. Organization: Move completed actions to /actions/completed/"
    echo "  11. Index Update: Update actions_index.md with enhanced formatting"
    
    # Optionally block the completion
    # exit 1  # Uncomment to enforce requirements
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"

# Create a completion report
REPORT_FILE=".aicheck/actions/completed/${ACTION_NAME}/completion_report.md"
if [[ "$CHECKS_PASSED" == "true" ]] && [[ -d ".aicheck/actions/completed/${ACTION_NAME}" ]]; then
    mkdir -p "$(dirname "$REPORT_FILE")"
    cat > "$REPORT_FILE" << EOF
# Completion Report: ${ACTION_NAME}

Date: $(date +%Y-%m-%d)
Time: $(date +%H:%M:%S)

## Checklist
- [x] Supporting documentation reviewed for migration
- [x] Actions index updated with completion status
- [x] ACTION_TIMELINE.md updated with completion details
- [x] Dependencies documented (if applicable)
- [x] Action directory moved to completed folder

## Migration Summary
- Universal docs migrated: ${#UNIVERSAL_DOCS[@]} files
- Completion recorded in: actions_index.md, ACTION_TIMELINE.md
- Final status: COMPLETED

Generated by: post-action-complete hook
EOF
    echo -e "\n${GREEN}📄 Completion report created at: $REPORT_FILE${NC}"
fi

exit 0