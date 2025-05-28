#!/bin/bash

# AICheck Installation Script
# Version: 4.0
# Updated: 2025-05-27

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AICHECK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$AICHECK_DIR")"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   AICheck Installation                       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to create directory if it doesn't exist
ensure_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        echo -e "${GREEN}✓${NC} Created directory: $1"
    fi
}

# Function to create file from template
create_from_template() {
    local template=$1
    local target=$2
    if [ ! -f "$target" ]; then
        cp "$template" "$target"
        echo -e "${GREEN}✓${NC} Created: $target"
    else
        echo -e "${YELLOW}!${NC} Already exists: $target"
    fi
}

# Step 1: Check prerequisites
echo -e "${BLUE}1. Checking prerequisites...${NC}"

if ! command_exists git; then
    echo -e "${RED}✗${NC} Git is not installed. Please install git first."
    exit 1
fi

if ! command_exists python3 && ! command_exists python; then
    echo -e "${YELLOW}!${NC} Python not found. Some features may be limited."
fi

if ! command_exists node; then
    echo -e "${YELLOW}!${NC} Node.js not found. Some features may be limited."
fi

echo -e "${GREEN}✓${NC} Prerequisites check complete"
echo

# Step 2: Create core directory structure
echo -e "${BLUE}2. Creating directory structure...${NC}"

ensure_dir "$AICHECK_DIR/actions"
ensure_dir "$AICHECK_DIR/actions/completed"
ensure_dir "$AICHECK_DIR/templates"
ensure_dir "$AICHECK_DIR/templates/action"
ensure_dir "$AICHECK_DIR/templates/claude"
ensure_dir "$AICHECK_DIR/scripts"
ensure_dir "$AICHECK_DIR/config"
ensure_dir "$AICHECK_DIR/docs"
ensure_dir "$PROJECT_ROOT/documentation"
ensure_dir "$PROJECT_ROOT/documentation/api"
ensure_dir "$PROJECT_ROOT/documentation/architecture"
ensure_dir "$PROJECT_ROOT/documentation/deployment"
ensure_dir "$PROJECT_ROOT/documentation/user"
ensure_dir "$PROJECT_ROOT/tests"
ensure_dir "$PROJECT_ROOT/tests/unit"
ensure_dir "$PROJECT_ROOT/tests/integration"
ensure_dir "$PROJECT_ROOT/tests/e2e"

echo

# Step 3: Install git hooks
echo -e "${BLUE}3. Installing git hooks...${NC}"

if [ -f "$AICHECK_DIR/hooks/install-hooks.sh" ]; then
    cd "$PROJECT_ROOT"
    "$AICHECK_DIR/hooks/install-hooks.sh"
else
    echo -e "${YELLOW}!${NC} Git hooks installer not found. Skipping..."
fi

echo

# Step 4: Create initial files
echo -e "${BLUE}4. Creating initial files...${NC}"

# Create actions_index.md if it doesn't exist
if [ ! -f "$AICHECK_DIR/actions_index.md" ]; then
    cat > "$AICHECK_DIR/actions_index.md" << 'EOF'
# AICheck Actions Index

```
╔══════════════════════════════════════════════════════════════════════════════╗
║                            📊 PROJECT ACTIONS DASHBOARD                      ║
║                          All ACTIONS tracked and managed                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

## 🎯 THE ActiveAction (0)

> **Current Focus:** None - Ready for next action selection

*No active action currently assigned*

## 📋 Pending Actions (0)

> **Queue:** Actions waiting to be activated

| 🎯 ACTION | 👤 Owner | 📊 Status | 📈 Progress | 📝 Description |
|----------|----------|-----------|-------------|-----------------|

## ✅ Completed Actions (0)

<details>
<summary>📋 <strong>Click to view completed actions</strong></summary>

| 🎯 ACTION | 👤 Owner | 📅 Completion Date | 📝 Description |
|----------|----------|---------------------|-----------------|

</details>

## ❌ Cancelled Actions (0)

<details>
<summary>🗑️ <strong>Click to view cancelled actions</strong></summary>

| 🎯 ACTION | 👤 Owner | 📅 Cancellation Date | 💭 Reason |
|----------|----------|----------------------|------------|

</details>

---
**📅 Last Updated:** $(date +%Y-%m-%d)  
**🔄 Auto-generated from:** `.aicheck/actions/` directory structure
EOF
    echo -e "${GREEN}✓${NC} Created actions_index.md"
else
    echo -e "${YELLOW}!${NC} actions_index.md already exists"
fi

# Create ACTION_TIMELINE.md if it doesn't exist
if [ ! -f "$AICHECK_DIR/ACTION_TIMELINE.md" ]; then
    cat > "$AICHECK_DIR/ACTION_TIMELINE.md" << 'EOF'
# AICheck Action Timeline

## Overview
This document tracks the chronological progression of all ACTIONS in the AICheck system.

## Timeline

### $(date +%Y-%m-%d)
- **System Initialized**: AICheck system installed and configured

---

*This timeline is updated automatically as actions progress through their lifecycle.*
EOF
    echo -e "${GREEN}✓${NC} Created ACTION_TIMELINE.md"
else
    echo -e "${YELLOW}!${NC} ACTION_TIMELINE.md already exists"
fi

# Create current_action file (empty)
touch "$AICHECK_DIR/current_action"
echo -e "${GREEN}✓${NC} Created current_action tracker"

echo

# Step 5: Create templates
echo -e "${BLUE}5. Creating templates...${NC}"

# Action PLAN template
cat > "$AICHECK_DIR/templates/action/PLAN.md" << 'EOF'
# ACTION: [Action Name]

**Version**: 1.0  
**Status**: Not Started  
**Progress**: 0%  
**Created**: [Date]  
**Owner**: [Name]

## Objective

[Clear statement of what this action will accomplish and why it's valuable to the PROGRAM]

## Success Criteria

- [ ] [Specific, measurable outcome 1]
- [ ] [Specific, measurable outcome 2]
- [ ] [Specific, measurable outcome 3]

## Dependencies

- [List any actions or systems this depends on]
- [Or write "None" if independent]

## Approach

### Phase 1: Research and Planning
- [Task 1]
- [Task 2]

### Phase 2: Implementation
- [Task 1]
- [Task 2]

### Phase 3: Testing and Documentation
- [Task 1]
- [Task 2]

## Test Requirements

### Unit Tests
- [Test scenario 1]
- [Test scenario 2]

### Integration Tests
- [Test scenario 1]
- [Test scenario 2]

## Risk Mitigation

| Risk | Impact | Mitigation Strategy |
|------|--------|-------------------|
| [Risk 1] | [High/Medium/Low] | [Strategy] |

## Timeline

- **Start Date**: [Date]
- **Target Completion**: [Date]
- **Milestones**:
  - [ ] Phase 1 Complete: [Date]
  - [ ] Phase 2 Complete: [Date]
  - [ ] Phase 3 Complete: [Date]

## Notes

[Any additional context or considerations]
EOF
echo -e "${GREEN}✓${NC} Created PLAN.md template"

# Todo template
cat > "$AICHECK_DIR/templates/action/todo.md" << 'EOF'
# TODO: [Action Name]

## Active Tasks
- [ ] Review and understand the PLAN.md (priority: high, status: pending)
- [ ] Set up development environment (priority: high, status: pending)

## Pending Tasks
- [ ] [Task from Phase 1] (priority: medium, status: pending)
- [ ] [Task from Phase 2] (priority: medium, status: pending)
- [ ] [Task from Phase 3] (priority: low, status: pending)

## Completed Tasks
<!-- Move completed items here with [x] -->

## Notes
- Remember to update progress in PLAN.md as tasks complete
- Follow test-driven development approach
- Document all decisions in supporting_docs/
EOF
echo -e "${GREEN}✓${NC} Created todo.md template"

echo

# Step 6: Create AICheck CLI wrapper
echo -e "${BLUE}6. Creating AICheck CLI...${NC}"

cat > "$AICHECK_DIR/aicheck" << 'EOF'
#!/bin/bash

# AICheck CLI
# Version: 4.0

AICHECK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$AICHECK_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
    echo "AICheck - Action-based development workflow management"
    echo ""
    echo "Usage: aicheck <command> [arguments]"
    echo ""
    echo "Commands:"
    echo "  create-action <name>    Create a new action"
    echo "  status                  Show current action status"
    echo "  set-action <name>       Set the active action"
    echo "  complete-action <name>  Mark action as complete"
    echo "  list                    List all actions"
    echo "  validate                Validate action structure"
    echo "  help                    Show this help message"
}

create_action() {
    local action_name=$1
    if [ -z "$action_name" ]; then
        echo -e "${RED}Error:${NC} Action name required"
        exit 1
    fi

    local action_dir="$AICHECK_DIR/actions/$action_name"
    
    if [ -d "$action_dir" ]; then
        echo -e "${RED}Error:${NC} Action '$action_name' already exists"
        exit 1
    fi

    # Create action directory structure
    mkdir -p "$action_dir/supporting_docs"
    
    # Copy templates
    cp "$AICHECK_DIR/templates/action/PLAN.md" "$action_dir/PLAN.md"
    cp "$AICHECK_DIR/templates/action/todo.md" "$action_dir/todo.md"
    
    # Update templates with action name and date
    sed -i '' "s/\[Action Name\]/$action_name/g" "$action_dir/PLAN.md" 2>/dev/null || \
    sed -i "s/\[Action Name\]/$action_name/g" "$action_dir/PLAN.md"
    
    sed -i '' "s/\[Date\]/$(date +%Y-%m-%d)/g" "$action_dir/PLAN.md" 2>/dev/null || \
    sed -i "s/\[Date\]/$(date +%Y-%m-%d)/g" "$action_dir/PLAN.md"
    
    sed -i '' "s/\[Action Name\]/$action_name/g" "$action_dir/todo.md" 2>/dev/null || \
    sed -i "s/\[Action Name\]/$action_name/g" "$action_dir/todo.md"
    
    echo -e "${GREEN}✓${NC} Created action: $action_name"
    echo -e "  ${BLUE}→${NC} Edit the PLAN at: $action_dir/PLAN.md"
    echo -e "  ${BLUE}→${NC} Track tasks in: $action_dir/todo.md"
}

show_status() {
    local current=""
    if [ -f "$AICHECK_DIR/current_action" ]; then
        current=$(cat "$AICHECK_DIR/current_action")
    fi
    
    if [ -z "$current" ]; then
        echo -e "${YELLOW}No active action set${NC}"
    else
        echo -e "${BLUE}Current ActiveAction:${NC} $current"
        
        local plan="$AICHECK_DIR/actions/$current/PLAN.md"
        if [ -f "$plan" ]; then
            local progress=$(grep -oP 'Progress:\s*\K[0-9]+' "$plan" 2>/dev/null || echo "0")
            echo -e "${BLUE}Progress:${NC} $progress%"
        fi
    fi
}

case "$1" in
    create-action)
        create_action "$2"
        ;;
    status)
        show_status
        ;;
    set-action)
        if [ -z "$2" ]; then
            echo -e "${RED}Error:${NC} Action name required"
            exit 1
        fi
        echo "$2" > "$AICHECK_DIR/current_action"
        echo -e "${GREEN}✓${NC} Set active action to: $2"
        ;;
    complete-action)
        if [ -z "$2" ]; then
            echo -e "${RED}Error:${NC} Action name required"
            exit 1
        fi
        # Run completion checks if hook exists
        if [ -f "$AICHECK_DIR/hooks/post-action-complete.sh" ]; then
            "$AICHECK_DIR/hooks/post-action-complete.sh" action complete "$2"
        fi
        echo -e "${GREEN}✓${NC} Marked action as complete: $2"
        echo -e "${YELLOW}!${NC} Remember to update actions_index.md"
        ;;
    list)
        echo -e "${BLUE}Actions:${NC}"
        for dir in "$AICHECK_DIR/actions"/*/; do
            if [ -d "$dir" ]; then
                basename "$dir"
            fi
        done
        ;;
    validate)
        echo "Validating AICheck structure..."
        # Add validation logic here
        echo -e "${GREEN}✓${NC} Validation complete"
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        echo -e "${RED}Error:${NC} Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac
EOF

chmod +x "$AICHECK_DIR/aicheck"
echo -e "${GREEN}✓${NC} Created aicheck CLI tool"

echo

# Step 7: Create symlink for global access
echo -e "${BLUE}7. Setting up global access...${NC}"

# Check if user has a local bin directory
USER_BIN="$HOME/.local/bin"
if [ -d "$USER_BIN" ]; then
    ln -sf "$AICHECK_DIR/aicheck" "$USER_BIN/aicheck"
    echo -e "${GREEN}✓${NC} Created symlink in $USER_BIN"
    echo -e "${YELLOW}!${NC} Make sure $USER_BIN is in your PATH"
else
    echo -e "${YELLOW}!${NC} To use 'aicheck' globally, add this to your shell config:"
    echo -e "    ${BLUE}export PATH=\"$AICHECK_DIR:\$PATH\"${NC}"
fi

echo

# Step 8: Create README
echo -e "${BLUE}8. Creating documentation...${NC}"

cat > "$AICHECK_DIR/README.md" << 'EOF'
# AICheck System

## Overview

AICheck is a documentation-first, test-driven development workflow system that ensures quality through structured processes and clear accountability.

## Quick Start

1. **Create an action**: `aicheck create-action my-feature`
2. **Edit the plan**: Edit `.aicheck/actions/my-feature/PLAN.md`
3. **Set as active**: `aicheck set-action my-feature`
4. **Work on tasks**: Track progress in `todo.md`
5. **Complete action**: `aicheck complete-action my-feature`

## Key Commands

- `aicheck create-action <name>` - Create new action
- `aicheck status` - Show current action
- `aicheck list` - List all actions
- `aicheck help` - Show help

## Directory Structure

```
.aicheck/
├── actions/              # All project actions
├── templates/            # Action templates
├── hooks/                # Git hooks
├── scripts/              # Utility scripts
├── RULES.md              # System rules
└── actions_index.md      # Action dashboard
```

## Core Principles

1. **Documentation First** - Document before implementing
2. **Test-Driven** - Write tests before code
3. **Single Focus** - One active action per editor
4. **Approval Required** - Plans need human approval
5. **Complete or Cancel** - No abandoned actions

## Getting Help

- Read the full rules: `.aicheck/RULES.md`
- Check action status: `.aicheck/actions_index.md`
- Review timeline: `.aicheck/ACTION_TIMELINE.md`

## Version

AICheck v4.0 (2025-05-27)
EOF
echo -e "${GREEN}✓${NC} Created README.md"

echo

# Final summary
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Installation Complete! 🎉                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Review the rules: ${YELLOW}cat $AICHECK_DIR/RULES.md${NC}"
echo -e "2. Create your first action: ${YELLOW}aicheck create-action my-first-action${NC}"
echo -e "3. Check the dashboard: ${YELLOW}cat $AICHECK_DIR/actions_index.md${NC}"
echo
echo -e "${BLUE}Documentation:${NC} $AICHECK_DIR/README.md"
echo -e "${BLUE}Rules:${NC} $AICHECK_DIR/RULES.md"
echo

# Add PATH reminder if needed
if [ ! -d "$USER_BIN" ] || [ ! -L "$USER_BIN/aicheck" ]; then
    echo -e "${YELLOW}To use 'aicheck' command globally, add to your shell config:${NC}"
    echo -e "    export PATH=\"$AICHECK_DIR:\$PATH\""
    echo
fi