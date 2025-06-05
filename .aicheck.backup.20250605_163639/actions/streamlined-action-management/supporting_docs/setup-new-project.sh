#!/bin/bash
# Quick setup script for new projects using Enhanced AICheck
# Run this in your new project directory!

set -e

# NEON PURPLE theme! 🟣
NEON_PURPLE='\033[1;35m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${NEON_PURPLE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${NEON_PURPLE}║    🟣 AICheck New Project Setup 🟣       ║${NC}"
echo -e "${NEON_PURPLE}╚═══════════════════════════════════════════╝${NC}"
echo ""

# Check if aicheck is installed
if ! command -v aicheck >/dev/null 2>&1; then
    echo -e "${YELLOW}Enhanced AICheck not found. Installing...${NC}"
    
    # Run the full installer
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL https://raw.githubusercontent.com/your-org/your-repo/main/.aicheck/actions/streamlined-action-management/supporting_docs/install.sh | bash
    else
        echo -e "${RED}Error: curl not found. Please install Enhanced AICheck manually.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Enhanced AICheck already installed${NC}"
fi

# Initialize project structure
echo -e "${NEON_PURPLE}🟣 Initializing project...${NC}"

# Create AICheck directory
mkdir -p .aicheck/actions

# Create project-specific RULES.md
cat > .aicheck/RULES.md << 'EOF'
# AICheck Rules v3.1

## Project Principles
1. All production deployments require verification
2. Critical issues must be resolved before completion
3. Document all dependencies explicitly
4. Maintain comprehensive action history

## Deployment Verification
- Configure test commands for all environments
- Verify actual functionality, not just connectivity
- Block completion without successful verification

## Created with Enhanced AICheck 🟣
EOF

echo -e "${GREEN}✓ Created .aicheck/RULES.md${NC}"

# Initialize git if needed
if [[ ! -d .git ]]; then
    echo -e "${CYAN}Initializing git repository...${NC}"
    git init --quiet
    
    # Create .gitignore with AICheck patterns
    cat > .gitignore << 'EOF'
# AICheck
.aicheck/current_action
.aicheck/actions/*/status
.aicheck/.tmp/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
EOF
    
    echo -e "${GREEN}✓ Git repository initialized${NC}"
    echo -e "${GREEN}✓ Created .gitignore${NC}"
fi

# Install git hooks
if [[ -d .git ]] && [[ -f ~/.aicheck/tools/git-hooks.sh ]]; then
    echo -e "${CYAN}Installing git hooks...${NC}"
    ~/.aicheck/tools/git-hooks.sh install >/dev/null 2>&1
    echo -e "${GREEN}✓ Git hooks installed${NC}"
fi

# Create first action
echo -e "${NEON_PURPLE}🟣 Creating your first action...${NC}"
aicheck action new "project-setup" >/dev/null 2>&1

# Customize the first action for this project
cat >> .aicheck/actions/project-setup/action.yaml << 'EOF'

# Project Setup Action
# This action tracks the initial project configuration

deployment:
  required: false  # Change to true for production projects
  
notes: |
  🟣 Welcome to your Enhanced AICheck project!
  
  Next steps:
  1. Edit this action's plan to define your project goals
  2. Configure deployment verification if needed
  3. Start creating actions for your features
  
  Remember: Actions can't be completed without deployment verification!
EOF

# Set as current action
aicheck action set project-setup >/dev/null 2>&1

# Show status
echo ""
echo -e "${NEON_PURPLE}╔═══════════════════════════════════════════╗${NC}"
echo -e "${NEON_PURPLE}║    🟣 Project Setup Complete! 🟣         ║${NC}"
echo -e "${NEON_PURPLE}╚═══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Your project is ready with Enhanced AICheck!${NC}"
echo ""
echo -e "Try these commands:"
echo -e "  ${YELLOW}aicheck status${NC}          - View current status"
echo -e "  ${YELLOW}aicheck action new${NC}      - Create a new action"
echo -e "  ${YELLOW}aicheck issue report${NC}    - Track an issue"
echo ""
echo -e "${NEON_PURPLE}🟣 Happy coding with deployment verification! 🟣${NC}"