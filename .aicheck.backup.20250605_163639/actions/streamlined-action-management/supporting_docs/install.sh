#!/bin/bash
# Automated installation script for Enhanced AICheck
# This script installs the enhanced AICheck system with all components

set -e

# Colors for output - with NEON PURPLE! 🟣
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NEON_PURPLE='\033[1;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
INSTALL_DIR="/usr/local/bin"
TOOLS_DIR="$HOME/.aicheck/tools"
REPO_URL="${AICHECK_REPO_URL:-https://raw.githubusercontent.com/your-org/your-repo/main}"
SCRIPTS_PATH=".aicheck/actions/streamlined-action-management/supporting_docs"

echo -e "${NEON_PURPLE}╔════════════════════════════════════════╗${NC}"
echo -e "${NEON_PURPLE}║   Enhanced AICheck Installation 🟣     ║${NC}"
echo -e "${NEON_PURPLE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if running with sudo when needed
check_permissions() {
    if [[ -w "$INSTALL_DIR" ]]; then
        SUDO=""
    else
        SUDO="sudo"
        echo -e "${YELLOW}Note: Installation to $INSTALL_DIR requires sudo privileges${NC}"
    fi
}

# Download a file
download_file() {
    local url="$1"
    local dest="$2"
    
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$url" -o "$dest"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$url" -O "$dest"
    else
        echo -e "${RED}Error: Neither curl nor wget found. Please install one.${NC}"
        exit 1
    fi
}

# Install main aicheck script
install_main_script() {
    echo -e "${NEON_PURPLE}🟣 Installing enhanced aicheck command...${NC}"
    
    local temp_file=$(mktemp)
    download_file "$REPO_URL/$SCRIPTS_PATH/aicheck-enhanced.sh" "$temp_file"
    
    $SUDO mv "$temp_file" "$INSTALL_DIR/aicheck"
    $SUDO chmod +x "$INSTALL_DIR/aicheck"
    
    echo -e "${GREEN}✓ Enhanced aicheck installed to $INSTALL_DIR/aicheck${NC}"
}

# Install supporting scripts
install_supporting_scripts() {
    echo -e "${BLUE}Installing supporting scripts...${NC}"
    
    mkdir -p "$TOOLS_DIR"
    
    local scripts=(
        "yaml-utils.sh"
        "deployment-verification-framework.sh"
        "issue-tracking-system.sh"
        "dependency-management-enhanced.sh"
        "migration-tools.sh"
        "git-hooks.sh"
        "test-enhanced-commands.sh"
        "test-migration.sh"
    )
    
    for script in "${scripts[@]}"; do
        echo -n "  Installing $script..."
        download_file "$REPO_URL/$SCRIPTS_PATH/$script" "$TOOLS_DIR/$script"
        chmod +x "$TOOLS_DIR/$script"
        echo -e " ${GREEN}✓${NC}"
    done
    
    echo -e "${GREEN}✓ Supporting scripts installed to $TOOLS_DIR${NC}"
}

# Install documentation
install_documentation() {
    echo -e "${BLUE}Installing documentation...${NC}"
    
    local docs_dir="$HOME/.aicheck/docs"
    mkdir -p "$docs_dir"
    
    local docs=(
        "ENHANCED_AICHECK_DOCUMENTATION.md"
        "QUICK_REFERENCE.md"
        "TRAINING_GUIDE.md"
        "INSTALLATION_INSTRUCTIONS.md"
    )
    
    for doc in "${docs[@]}"; do
        echo -n "  Installing $doc..."
        download_file "$REPO_URL/$SCRIPTS_PATH/$doc" "$docs_dir/$doc"
        echo -e " ${GREEN}✓${NC}"
    done
    
    echo -e "${GREEN}✓ Documentation installed to $docs_dir${NC}"
}

# Check for optional dependencies
check_dependencies() {
    echo -e "${BLUE}Checking optional dependencies...${NC}"
    
    if command -v yq >/dev/null 2>&1; then
        echo -e "${GREEN}✓ yq is installed (better YAML performance)${NC}"
    else
        echo -e "${YELLOW}⚠ yq not found (aicheck will use fallback parser)${NC}"
        echo "  To install: brew install yq (macOS) or snap install yq (Linux)"
    fi
    
    if command -v git >/dev/null 2>&1; then
        echo -e "${GREEN}✓ git is installed${NC}"
    else
        echo -e "${RED}✗ git not found (required for git integration)${NC}"
    fi
}

# Offer to install git hooks
install_git_hooks() {
    if [[ -d .git ]]; then
        echo ""
        echo -e "${BLUE}Git repository detected${NC}"
        read -p "Install git hooks for automatic tracking? (y/N) " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            "$TOOLS_DIR/git-hooks.sh" install
            echo -e "${GREEN}✓ Git hooks installed${NC}"
        fi
    fi
}

# Offer to migrate existing actions
migrate_existing_actions() {
    if [[ -d .aicheck/actions ]] && [[ -n "$(ls -A .aicheck/actions 2>/dev/null)" ]]; then
        echo ""
        echo -e "${BLUE}Existing actions detected${NC}"
        read -p "Migrate existing actions to enhanced format? (y/N) " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            "$TOOLS_DIR/migration-tools.sh" migrate-all
            echo -e "${GREEN}✓ Actions migrated${NC}"
        fi
    fi
}

# Initialize project if needed
initialize_project() {
    echo ""
    echo -e "${NEON_PURPLE}🟣 Project Setup${NC}"
    
    if [[ ! -d .aicheck ]]; then
        echo -e "${CYAN}Initializing AICheck for this project...${NC}"
        
        # Create directory structure
        mkdir -p .aicheck/actions
        
        # Create initial RULES.md
        cat > .aicheck/RULES.md << 'EOF'
# AICheck Rules v3.1

## Core Principles
1. Documentation-first development
2. Test-driven implementation
3. Deployment verification required
4. Critical issues block completion

## Workflow
1. Create action with clear plan
2. Document dependencies
3. Verify deployment before completion
4. Maintain audit trail

Generated by Enhanced AICheck 🟣
EOF
        
        # Create a welcome action
        echo -e "${NEON_PURPLE}Creating your first action...${NC}"
        aicheck action new "welcome-to-aicheck" >/dev/null 2>&1
        
        # Add a custom welcome message to the action
        cat >> .aicheck/actions/welcome-to-aicheck/action.yaml << 'EOF'

# 🟣 Welcome to Enhanced AICheck!
# This action was created to help you get started.
# Feel free to explore the structure and delete when ready.

notes: |
  Enhanced AICheck prevents false completion claims by:
  - Requiring deployment verification
  - Tracking critical issues
  - Maintaining comprehensive audit trails
  
  Try: aicheck status
EOF
        
        echo -e "${GREEN}✓ Project initialized with AICheck${NC}"
        echo -e "${NEON_PURPLE}✓ Created welcome action${NC}"
        
        # Initialize git if not already
        if [[ ! -d .git ]]; then
            echo ""
            read -p "Initialize git repository? (recommended) (Y/n) " -n 1 -r
            echo ""
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                git init --quiet
                echo -e "${GREEN}✓ Git repository initialized${NC}"
                
                # Add .aicheck to gitignore selectively
                echo "# AICheck - track most files but ignore some" >> .gitignore
                echo ".aicheck/current_action" >> .gitignore
                echo ".aicheck/actions/*/status" >> .gitignore
                echo -e "${GREEN}✓ Updated .gitignore${NC}"
            fi
        fi
    else
        echo -e "${CYAN}Project already initialized with AICheck${NC}"
    fi
}

# Verify installation
verify_installation() {
    echo ""
    echo -e "${NEON_PURPLE}🟣 Verifying installation...${NC}"
    
    if command -v aicheck >/dev/null 2>&1; then
        echo -e "${GREEN}✓ aicheck command is available${NC}"
        
        # Test creating an action
        local test_action="test-install-$$"
        if aicheck action new "$test_action" >/dev/null 2>&1; then
            if [[ -f ".aicheck/actions/$test_action/action.yaml" ]]; then
                echo -e "${GREEN}✓ YAML creation working${NC}"
                rm -rf ".aicheck/actions/$test_action"
            else
                echo -e "${RED}✗ YAML creation failed${NC}"
            fi
        else
            echo -e "${RED}✗ Action creation failed${NC}"
        fi
    else
        echo -e "${RED}✗ aicheck command not found${NC}"
        echo "  You may need to reload your shell or add $INSTALL_DIR to PATH"
    fi
}

# Main installation flow
main() {
    check_permissions
    
    # Create directories
    mkdir -p "$TOOLS_DIR"
    
    # Install components
    install_main_script
    install_supporting_scripts
    install_documentation
    
    # Check environment
    check_dependencies
    
    # Initialize project if needed
    initialize_project
    
    # Optional installations
    install_git_hooks
    migrate_existing_actions
    
    # Verify
    verify_installation
    
    # Success message
    echo ""
    echo -e "${NEON_PURPLE}╔════════════════════════════════════════════════╗${NC}"
    echo -e "${NEON_PURPLE}║  🟣 Enhanced AICheck Installation Complete! 🟣 ║${NC}"
    echo -e "${NEON_PURPLE}╚════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "${PURPLE}1.${NC} Reload your shell: ${YELLOW}source ~/.bashrc${NC} (or ~/.zshrc)"
    echo -e "${PURPLE}2.${NC} Try it out: ${YELLOW}aicheck status${NC}"
    echo -e "${PURPLE}3.${NC} Create an action: ${YELLOW}aicheck action new my-feature${NC}"
    echo -e "${PURPLE}4.${NC} Quick reference: ${YELLOW}less $HOME/.aicheck/docs/QUICK_REFERENCE.md${NC}"
    echo ""
    echo -e "${NEON_PURPLE}🟣 Welcome to deployment verification! 🟣${NC}"
}

# Handle errors
trap 'echo -e "\n${RED}Installation failed!${NC}"; exit 1' ERR

# Run installation
main "$@"