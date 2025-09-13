#!/bin/bash
WORKTREE=$1
AI_NAME=$2
PROGRESS=$3

if [ -z "$WORKTREE" ] || [ -z "$AI_NAME" ]; then
    echo "Usage: $0 <worktree-name> <ai-name> [progress%]"
    echo ""
    echo "Examples:"
    echo "  $0 billing-system Claude-1 25%"
    echo "  $0 ux-ui-improvements Cursor-2 60%"
    echo ""
    echo "Available worktrees:"
    echo "  billing-system, ci-cd, documentation, performance-optimization,"
    echo "  recovery-system, service-interfaces, test-e2e-enhancement,"
    echo "  test-integration-enhancement, test-live-performance,"
    echo "  test-unit-enhancement, ux-ui-improvements"
    exit 1
fi

# Navigate to worktree
if [ -d "../Ultra-worktrees/$WORKTREE" ]; then
    cd "../Ultra-worktrees/$WORKTREE" || exit 1
elif [ -d "/Users/joshuafield/Documents/Ultra-worktrees/$WORKTREE" ]; then
    cd "/Users/joshuafield/Documents/Ultra-worktrees/$WORKTREE" || exit 1
else
    echo "Error: Worktree '$WORKTREE' not found"
    exit 1
fi

# Create STATUS.md if it doesn't exist
if [ ! -f "STATUS.md" ]; then
    echo "Creating STATUS.md from template..."
    cp /Users/joshuafield/Documents/Ultra/scripts/STATUS_TEMPLATE.md STATUS.md
fi

# Update AI assignment
sed -i '' "s/Current AI:.*/Current AI: $AI_NAME/" STATUS.md

# Update progress if provided
if [ ! -z "$PROGRESS" ]; then
    sed -i '' "s/Status:.*% Complete/Status: $PROGRESS Complete/" STATUS.md
fi

# Update last updated timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M")
sed -i '' "s/Last Updated:.*/Last Updated: $TIMESTAMP/" STATUS.md

echo "✅ Updated $WORKTREE:"
echo "   AI: $AI_NAME"
if [ ! -z "$PROGRESS" ]; then
    echo "   Progress: $PROGRESS"
fi
echo "   Timestamp: $TIMESTAMP"
echo ""
echo "Don't forget to commit the STATUS.md changes!"