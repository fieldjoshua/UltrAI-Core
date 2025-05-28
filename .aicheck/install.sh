#!/bin/bash

# AICheck Installation Script
# Version: 4.1
# Updated: 2025-05-28

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
AICHECK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$AICHECK_DIR")"
REPO_URL="https://github.com/fieldjoshua/UltrAI-Core.git"

# Parse command line arguments
FRESH_INSTALL=false
REMOTE_INSTALL=false
CONSOLIDATE=false
VERBOSE=false

usage() {
    echo "AICheck Installation Script v4.1"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --fresh             Fresh installation (ignores existing files)"
    echo "  --remote            Install from GitHub repository"
    echo "  --consolidate       Consolidate/cleanup repository"
    echo "  --verbose           Verbose output"
    echo "  --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                  # Standard installation"
    echo "  $0 --remote         # Install from GitHub"
    echo "  $0 --consolidate    # Cleanup and consolidate repository"
    echo "  $0 --fresh --verbose # Fresh install with verbose output"
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --fresh)
            FRESH_INSTALL=true
            shift
            ;;
        --remote)
            REMOTE_INSTALL=true
            shift
            ;;
        --consolidate)
            CONSOLIDATE=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo -e "${RED}Error:${NC} Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Header
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   AICheck Installation v4.1                  ║${NC}"
echo -e "${BLUE}║               Enhanced with Repository Consolidation          ║${NC}"
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
    elif [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}•${NC} Directory exists: $1"
    fi
}

# Function to log verbose messages
log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}•${NC} $1"
    fi
}

# Function to consolidate repository
consolidate_repository() {
    echo -e "${MAGENTA}🧹 Repository Consolidation${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local cleanup_count=0
    
    # Remove .DS_Store files
    echo -e "${YELLOW}Removing .DS_Store files...${NC}"
    find "$PROJECT_ROOT" -name ".DS_Store" -type f -delete 2>/dev/null || true
    ((cleanup_count++))
    
    # Clean up backup directories
    echo -e "${YELLOW}Consolidating backup directories...${NC}"
    if [ -d "$AICHECK_DIR/.aicheck_backup_20250524_095556" ]; then
        if [ ! -d "$AICHECK_DIR/backups" ]; then
            mkdir -p "$AICHECK_DIR/backups"
        fi
        mv "$AICHECK_DIR/.aicheck_backup_20250524_095556" "$AICHECK_DIR/backups/backup-2025-05-24-v1" 2>/dev/null || true
        ((cleanup_count++))
    fi
    
    if [ -d "$AICHECK_DIR/.aicheck_backup_20250524_095601" ]; then
        if [ ! -d "$AICHECK_DIR/backups" ]; then
            mkdir -p "$AICHECK_DIR/backups"
        fi
        mv "$AICHECK_DIR/.aicheck_backup_20250524_095601" "$AICHECK_DIR/backups/backup-2025-05-24-v2" 2>/dev/null || true
        ((cleanup_count++))
    fi
    
    # Clean up old session files (keep last 10)
    echo -e "${YELLOW}Cleaning up old session files...${NC}"
    if [ -d "$AICHECK_DIR/sessions" ]; then
        local session_count=$(find "$AICHECK_DIR/sessions" -name "*.session" | wc -l)
        if [ "$session_count" -gt 10 ]; then
            find "$AICHECK_DIR/sessions" -name "*.session" -type f | head -n -10 | xargs rm -f 2>/dev/null || true
            ((cleanup_count++))
        fi
    fi
    
    # Clean up old cursor context files (keep last 5)
    echo -e "${YELLOW}Cleaning up old context files...${NC}"
    if [ -d "$AICHECK_DIR/cursor" ]; then
        local context_count=$(find "$AICHECK_DIR/cursor" -name "chat_context_*.md" | wc -l)
        if [ "$context_count" -gt 5 ]; then
            find "$AICHECK_DIR/cursor" -name "chat_context_*.md" -type f | head -n -5 | xargs rm -f 2>/dev/null || true
            ((cleanup_count++))
        fi
    fi
    
    # Fix file permissions
    echo -e "${YELLOW}Fixing file permissions...${NC}"
    chmod 755 "$AICHECK_DIR" 2>/dev/null || true
    chmod 644 "$AICHECK_DIR"/*.md 2>/dev/null || true
    chmod 755 "$AICHECK_DIR"/scripts/*.sh 2>/dev/null || true
    chmod 755 "$AICHECK_DIR/aicheck" 2>/dev/null || true
    chmod 755 "$AICHECK_DIR/install.sh" 2>/dev/null || true
    
    # Set secure permissions for sensitive files
    if [ -f "$AICHECK_DIR/current_action" ]; then
        chmod 600 "$AICHECK_DIR/current_action"
    fi
    if [ -f "$AICHECK_DIR/current_session" ]; then
        chmod 600 "$AICHECK_DIR/current_session"
    fi
    if [ -f "$AICHECK_DIR/security.log" ]; then
        chmod 600 "$AICHECK_DIR/security.log"
    fi
    
    # Create .gitignore for AICheck if it doesn't exist
    if [ ! -f "$AICHECK_DIR/.gitignore" ]; then
        cat > "$AICHECK_DIR/.gitignore" << 'EOF'
# AICheck specific ignores
security.log
*.tmp
*.temp
.DS_Store
# Session files (keep recent ones)
sessions/session_*.session
# Context files (keep recent ones)  
cursor/chat_context_session_*.md
EOF
        echo -e "${GREEN}✓${NC} Created AICheck .gitignore"
        ((cleanup_count++))
    fi
    
    echo -e "${GREEN}✓${NC} Repository consolidation complete (${cleanup_count} operations)"
    echo
}

# Function to install from remote repository
install_from_remote() {
    echo -e "${CYAN}📡 Remote Installation${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    local temp_dir=$(mktemp -d)
    echo -e "${YELLOW}Cloning repository...${NC}"
    
    if git clone "$REPO_URL" "$temp_dir" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Repository cloned successfully"
        
        # Copy AICheck files
        if [ -d "$temp_dir/.aicheck" ]; then
            echo -e "${YELLOW}Installing AICheck files...${NC}"
            cp -r "$temp_dir/.aicheck"/* "$AICHECK_DIR/" 2>/dev/null || true
            echo -e "${GREEN}✓${NC} AICheck files installed from remote"
        fi
        
        # Cleanup
        rm -rf "$temp_dir"
    else
        echo -e "${RED}✗${NC} Failed to clone repository"
        echo -e "${YELLOW}Falling back to local installation...${NC}"
    fi
    echo
}

# Step 1: Handle special modes
if [ "$CONSOLIDATE" = true ]; then
    consolidate_repository
fi

if [ "$REMOTE_INSTALL" = true ]; then
    install_from_remote
fi

# Step 2: Check prerequisites
echo -e "${BLUE}1. Checking prerequisites...${NC}"

if ! command_exists git; then
    echo -e "${RED}✗${NC} Git is not installed. Please install git first."
    exit 1
fi

log_verbose "Git found: $(git --version)"

if ! command_exists python3 && ! command_exists python; then
    echo -e "${YELLOW}!${NC} Python not found. Some features may be limited."
else
    log_verbose "Python found: $(python3 --version 2>/dev/null || python --version 2>/dev/null)"
fi

if ! command_exists node; then
    echo -e "${YELLOW}!${NC} Node.js not found. Some features may be limited."
else
    log_verbose "Node.js found: $(node --version)"
fi

echo -e "${GREEN}✓${NC} Prerequisites check complete"
echo

# Step 3: Create core directory structure
echo -e "${BLUE}2. Creating directory structure...${NC}"

ensure_dir "$AICHECK_DIR/actions"
ensure_dir "$AICHECK_DIR/actions/completed"
ensure_dir "$AICHECK_DIR/templates"
ensure_dir "$AICHECK_DIR/templates/action"
ensure_dir "$AICHECK_DIR/templates/claude"
ensure_dir "$AICHECK_DIR/scripts"
ensure_dir "$AICHECK_DIR/config"
ensure_dir "$AICHECK_DIR/docs"
ensure_dir "$AICHECK_DIR/test_reports"
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

# Step 4: Install git hooks
echo -e "${BLUE}3. Installing git hooks...${NC}"

if [ -f "$AICHECK_DIR/hooks/install-hooks.sh" ]; then
    cd "$PROJECT_ROOT"
    if "$AICHECK_DIR/hooks/install-hooks.sh" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Git hooks installed successfully"
    else
        echo -e "${YELLOW}!${NC} Git hooks installation had warnings (this is normal)"
    fi
else
    echo -e "${YELLOW}!${NC} Git hooks installer not found. Skipping..."
fi

echo

# Step 5: Create/update core files
echo -e "${BLUE}4. Creating core files...${NC}"

# Create actions_index.md if it doesn't exist or if fresh install
if [ ! -f "$AICHECK_DIR/actions_index.md" ] || [ "$FRESH_INSTALL" = true ]; then
    cat > "$AICHECK_DIR/actions_index.md" << EOF
# AICheck Actions Index

\`\`\`
╔══════════════════════════════════════════════════════════════════════════════╗
║                            📊 PROJECT ACTIONS DASHBOARD                      ║
║                          All ACTIONS tracked and managed                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
\`\`\`

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
**🔄 Auto-generated from:** \`.aicheck/actions/\` directory structure
EOF
    echo -e "${GREEN}✓${NC} Created actions_index.md"
elif [ "$VERBOSE" = true ]; then
    echo -e "${CYAN}•${NC} actions_index.md already exists"
fi

# Create ACTION_TIMELINE.md if it doesn't exist or if fresh install
if [ ! -f "$AICHECK_DIR/ACTION_TIMELINE.md" ] || [ "$FRESH_INSTALL" = true ]; then
    cat > "$AICHECK_DIR/ACTION_TIMELINE.md" << EOF
# AICheck Action Timeline

## Overview
This document tracks the chronological progression of all ACTIONS in the AICheck system.

## Timeline

### $(date +%Y-%m-%d)
- **System Initialized**: AICheck v4.1 installed and configured

---

*This timeline is updated automatically as actions progress through their lifecycle.*
EOF
    echo -e "${GREEN}✓${NC} Created ACTION_TIMELINE.md"
elif [ "$VERBOSE" = true ]; then
    echo -e "${CYAN}•${NC} ACTION_TIMELINE.md already exists"
fi

# Create current_action file (empty)
touch "$AICHECK_DIR/current_action"
chmod 600 "$AICHECK_DIR/current_action"
echo -e "${GREEN}✓${NC} Created current_action tracker"

echo

# Step 6: Create/update templates
echo -e "${BLUE}5. Creating templates...${NC}"

# Action PLAN template
if [ ! -f "$AICHECK_DIR/templates/action/PLAN.md" ] || [ "$FRESH_INSTALL" = true ]; then
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
elif [ "$VERBOSE" = true ]; then
    echo -e "${CYAN}•${NC} PLAN.md template already exists"
fi

# Todo template
if [ ! -f "$AICHECK_DIR/templates/action/todo.md" ] || [ "$FRESH_INSTALL" = true ]; then
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
elif [ "$VERBOSE" = true ]; then
    echo -e "${CYAN}•${NC} todo.md template already exists"
fi

echo

# Step 7: Verify AICheck CLI
echo -e "${BLUE}6. Verifying AICheck CLI...${NC}"

if [ -f "$AICHECK_DIR/aicheck" ]; then
    chmod +x "$AICHECK_DIR/aicheck"
    echo -e "${GREEN}✓${NC} AICheck CLI verified"
else
    echo -e "${RED}✗${NC} AICheck CLI not found"
    echo -e "${YELLOW}Note:${NC} Some functionality may be limited"
fi

echo

# Step 8: Set up global access
echo -e "${BLUE}7. Setting up global access...${NC}"

# Check if user has a local bin directory
USER_BIN="$HOME/.local/bin"
if [ -d "$USER_BIN" ] && [ -f "$AICHECK_DIR/aicheck" ]; then
    if ln -sf "$AICHECK_DIR/aicheck" "$USER_BIN/aicheck" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Created symlink in $USER_BIN"
        echo -e "${CYAN}•${NC} Make sure $USER_BIN is in your PATH"
    else
        echo -e "${YELLOW}!${NC} Could not create symlink in $USER_BIN"
    fi
else
    echo -e "${YELLOW}!${NC} To use 'aicheck' globally, add this to your shell config:"
    echo -e "    ${BLUE}export PATH=\"$AICHECK_DIR:\$PATH\"${NC}"
fi

echo

# Step 9: Create comprehensive README
echo -e "${BLUE}8. Creating documentation...${NC}"

cat > "$AICHECK_DIR/README.md" << EOF
# AICheck System v4.1

## Overview

AICheck is a documentation-first, test-driven development workflow system that ensures quality through structured processes and clear accountability.

## Quick Start

1. **Create an action**: \`aicheck create-action my-feature\`
2. **Edit the plan**: Edit \`.aicheck/actions/my-feature/PLAN.md\`
3. **Set as active**: \`aicheck set-action my-feature\`
4. **Work on tasks**: Track progress in \`todo.md\`
5. **Complete action**: \`aicheck complete-action my-feature\`

## Key Commands

- \`aicheck create-action <name>\` - Create new action
- \`aicheck status\` - Show current action
- \`aicheck list\` - List all actions
- \`aicheck validate\` - Validate system
- \`aicheck test\` - Run system tests
- \`aicheck security-check\` - Check security
- \`aicheck help\` - Show help

## Directory Structure

\`\`\`
.aicheck/
├── actions/              # All project actions
├── templates/            # Action templates
├── hooks/                # Git hooks
├── scripts/              # Utility scripts
├── RULES.md              # System rules
└── actions_index.md      # Action dashboard
\`\`\`

## Core Principles

1. **Documentation First** - Document before implementing
2. **Test-Driven** - Write tests before code
3. **Single Focus** - One active action per editor
4. **Approval Required** - Plans need human approval
5. **Complete or Cancel** - No abandoned actions

## Installation

### Fresh Installation
\`\`\`bash
.aicheck/install.sh --fresh
\`\`\`

### Remote Installation
\`\`\`bash
.aicheck/install.sh --remote
\`\`\`

### Repository Consolidation
\`\`\`bash
.aicheck/install.sh --consolidate
\`\`\`

## Getting Help

- Read the full rules: \`.aicheck/RULES.md\`
- Check action status: \`.aicheck/actions_index.md\`
- Review timeline: \`.aicheck/ACTION_TIMELINE.md\`
- Quick reference: \`.aicheck/QUICK_REFERENCE.md\`

## Version

AICheck v4.1 (2025-05-28)
- Enhanced installation with repository consolidation
- Advanced automation features
- Comprehensive security validation
- System testing suite
EOF
echo -e "${GREEN}✓${NC} Created comprehensive README.md"

echo

# Step 10: Run system validation
echo -e "${BLUE}9. Running system validation...${NC}"

if [ -f "$AICHECK_DIR/aicheck" ]; then
    if "$AICHECK_DIR/aicheck" validate >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} System validation passed"
    else
        echo -e "${YELLOW}!${NC} System validation had warnings (check with 'aicheck validate')"
    fi
else
    echo -e "${YELLOW}!${NC} Cannot run validation - AICheck CLI not available"
fi

echo

# Final summary
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Installation Complete! 🎉                   ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo

echo -e "${BLUE}Installation Summary:${NC}"
echo -e "• AICheck version: ${MAGENTA}4.1${NC}"
echo -e "• Installation type: ${MAGENTA}$([ "$FRESH_INSTALL" = true ] && echo "Fresh" || echo "Standard")${NC}"
echo -e "• Repository consolidated: ${MAGENTA}$([ "$CONSOLIDATE" = true ] && echo "Yes" || echo "No")${NC}"
echo -e "• Remote install: ${MAGENTA}$([ "$REMOTE_INSTALL" = true ] && echo "Yes" || echo "No")${NC}"

echo
echo -e "${BLUE}Next steps:${NC}"
echo -e "1. Review the rules: ${YELLOW}cat $AICHECK_DIR/RULES.md${NC}"
echo -e "2. Create your first action: ${YELLOW}aicheck create-action my-first-action${NC}"
echo -e "3. Check the dashboard: ${YELLOW}cat $AICHECK_DIR/actions_index.md${NC}"
echo -e "4. Run system tests: ${YELLOW}aicheck test${NC}"

echo
echo -e "${BLUE}Documentation:${NC}"
echo -e "• README: ${CYAN}$AICHECK_DIR/README.md${NC}"
echo -e "• Rules: ${CYAN}$AICHECK_DIR/RULES.md${NC}"
echo -e "• Quick Reference: ${CYAN}$AICHECK_DIR/QUICK_REFERENCE.md${NC}"

echo

# Add PATH reminder if needed
if [ ! -d "$USER_BIN" ] || [ ! -L "$USER_BIN/aicheck" ]; then
    echo -e "${YELLOW}To use 'aicheck' command globally, add to your shell config:${NC}"
    echo -e "    ${CYAN}export PATH=\"$AICHECK_DIR:\$PATH\"${NC}"
    echo
fi

echo -e "${MAGENTA}🚀 AICheck v4.1 is ready for use!${NC}"