#!/bin/bash

# Script to activate AICheck in a Claude Code session

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BRIGHT_BLURPLE}Activating AICheck in Claude Code...${NC}"

# Check if the prompt file exists
if [ ! -f ".aicheck/claude_aicheck_prompt.md" ]; then
  echo -e "${YELLOW}Warning: Activation prompt not found.${NC}"
  echo -e "Creating default activation prompt..."
  
  mkdir -p .aicheck
  
  # Create activation text
  cat > .aicheck/claude_aicheck_prompt.md << 'PROMPT'
# AICheck System Integration

I notice this project is using the AICheck Multimodal Control Protocol. Let me check the current action status.

I'll follow the AICheck workflow and adhere to the rules in `.aicheck/RULES.md`. This includes:

1. Using the command line tools: 
   - `./aicheck status` to check current action
   - `./aicheck action new/set/complete` to manage actions
   - `./aicheck dependency add/internal` to document dependencies
   - `./aicheck exec` for maintenance mode

2. Following the documentation-first approach:
   - Writing tests before implementation
   - Documenting all Claude interactions
   - Adhering to the ACTION plan
   - Focusing only on the active action's scope
   - Documenting all dependencies

3. Dependency Management:
   - Documenting all external dependencies
   - Recording all internal dependencies between actions
   - Verifying dependencies before completing actions

4. Git Hook Compliance:
   - Immediately respond to git hook suggestions
   - Address issues before continuing with new work
   - Follow commit message format guidelines
   - Document dependency changes promptly
   - Ensure test-driven development compliance

Let me check the current action status now with `./aicheck status` and proceed accordingly.
PROMPT
fi

# Copy the prompt template to clipboard
if command -v pbcopy > /dev/null; then
  # macOS
  cat .aicheck/claude_aicheck_prompt.md | pbcopy
  echo -e "${GREEN}✓ AICheck activation prompt copied to clipboard${NC}"
elif command -v xclip > /dev/null; then
  # Linux with xclip
  cat .aicheck/claude_aicheck_prompt.md | xclip -selection clipboard
  echo -e "${GREEN}✓ AICheck activation prompt copied to clipboard${NC}"
elif command -v clip.exe > /dev/null; then
  # Windows with clip.exe (WSL)
  cat .aicheck/claude_aicheck_prompt.md | clip.exe
  echo -e "${GREEN}✓ AICheck activation prompt copied to clipboard${NC}"
else
  # Fallback to temp file
  cp .aicheck/claude_aicheck_prompt.md /tmp/aicheck_prompt.md
  echo -e "${YELLOW}Copied prompt to /tmp/aicheck_prompt.md${NC}"
  
  # Try to open the file
  if command -v open > /dev/null; then
    open /tmp/aicheck_prompt.md
  elif command -v xdg-open > /dev/null; then
    xdg-open /tmp/aicheck_prompt.md
  elif command -v wslview > /dev/null; then
    wslview /tmp/aicheck_prompt.md
  else
    echo -e "${YELLOW}Unable to open file automatically.${NC}"
  fi
fi

# Instructions
echo -e "\n${BRIGHT_BLURPLE}To activate AICheck in Claude Code:${NC}"
echo -e "1. Start a new Claude Code conversation"
echo -e "2. Paste the activation text from your clipboard"
echo -e "3. Claude will automatically recognize AICheck and use the system\n"
echo -e "${GREEN}✓ AICheck activation ready${NC}"
