#!/bin/bash
# AICheck Quick Setup - One file, no dependencies!

# NEON PURPLE! 🟣
P='\033[1;35m'
G='\033[0;32m'
N='\033[0m'

# Create everything in one go
mkdir -p .aicheck/actions

# Create the aicheck command RIGHT HERE in the project
cat > .aicheck/aicheck << 'AICHECK_SCRIPT'
#!/bin/bash
# Enhanced AICheck - All-in-one

AICHECK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACTION_DIR="$AICHECK_DIR/actions"
CURRENT="$AICHECK_DIR/current_action"

case "$1" in
    new|action)
        [[ "$2" == "new" ]] && shift
        name="${2:-unnamed-action}"
        mkdir -p "$ACTION_DIR/$name"
        echo "pending" > "$ACTION_DIR/$name/status"
        cat > "$ACTION_DIR/$name/action.yaml" << EOF
name: $name
status: pending
created: $(date +%Y-%m-%d)
deployment:
  required: false
EOF
        echo "✅ Created action: $name"
        ;;
    
    status|s)
        if [[ -f "$CURRENT" ]]; then
            action=$(cat "$CURRENT")
            echo "🟣 Current: $action"
            [[ -f "$ACTION_DIR/$action/status" ]] && echo "Status: $(cat "$ACTION_DIR/$action/status")"
        else
            echo "No active action. Use: aicheck new <name>"
        fi
        ;;
    
    set)
        echo "$2" > "$CURRENT"
        echo "✅ Set current action: $2"
        ;;
    
    complete)
        action="${2:-$(cat "$CURRENT" 2>/dev/null)}"
        if [[ -z "$action" ]]; then
            echo "❌ No action specified"
            exit 1
        fi
        # Check deployment if required
        if grep -q "required: true" "$ACTION_DIR/$action/action.yaml" 2>/dev/null; then
            echo "❌ Deployment verification required!"
            echo "This prevents false completion claims."
            exit 1
        fi
        echo "completed" > "$ACTION_DIR/$action/status"
        echo "✅ Completed: $action"
        ;;
    
    *)
        echo "🟣 AICheck - Deployment Verification System"
        echo "Commands:"
        echo "  aicheck new <name>     - Create action"
        echo "  aicheck status         - Show status"
        echo "  aicheck set <name>     - Set current"
        echo "  aicheck complete       - Mark complete"
        ;;
esac
AICHECK_SCRIPT

chmod +x .aicheck/aicheck

# Create first action
.aicheck/aicheck new "welcome" >/dev/null

# Setup git
if [[ ! -d .git ]]; then
    git init -q
    echo ".aicheck/current_action" >> .gitignore
fi

echo -e "${P}🟣 AICheck installed!${N}"
echo -e "${G}✅ Ready to use${N}"
echo ""
echo "Add to PATH:"
echo -e "  ${P}export PATH=\"\$PWD/.aicheck:\$PATH\"${N}"
echo ""
echo "Or use directly:"
echo -e "  ${P}.aicheck/aicheck status${N}"