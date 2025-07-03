#!/bin/bash
PROMPT="I'm working on a project with AICheck governance. Please acknowledge that you understand the AICheck system and are ready to follow the rules in .aicheck/RULES.md. Check the current action with ./aicheck status and help me implement according to the active action plan."

echo "$PROMPT"
echo ""
echo "Copy the text above and paste it into Claude Code to activate AICheck."

# Try to copy to clipboard
if command -v pbcopy >/dev/null 2>&1; then
    echo "$PROMPT" | pbcopy
    echo "✓ Copied to clipboard"
elif command -v xclip >/dev/null 2>&1; then
    echo "$PROMPT" | xclip -selection clipboard
    echo "✓ Copied to clipboard"
fi
