#!/bin/bash
echo "=== Worktree Status Overview ==="
echo "Generated: $(date)"
echo ""

for worktree in $(git worktree list --porcelain | grep "worktree" | cut -d' ' -f2); do
    echo "📁 $worktree"
    cd "$worktree" 2>/dev/null || continue
    
    branch=$(git branch --show-current)
    echo "  Branch: $branch"
    echo "  Last commit: $(git log -1 --oneline 2>/dev/null || echo 'No commits')"
    
    # Count uncommitted changes
    changes=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    echo "  Uncommitted changes: $changes"
    
    # Check ahead/behind main
    if git rev-parse --verify origin/main >/dev/null 2>&1; then
        ahead_behind=$(git rev-list --left-right --count origin/main...$branch 2>/dev/null || echo "0	0")
        ahead=$(echo $ahead_behind | cut -f2)
        behind=$(echo $ahead_behind | cut -f1)
        echo "  Status: $ahead ahead, $behind behind main"
    fi
    
    # Check for STATUS.md
    if [ -f "STATUS.md" ]; then
        echo "  Feature Status: $(grep -m1 "Status:" STATUS.md | cut -d: -f2- | tr -d ' ')"
    fi
    echo ""
done