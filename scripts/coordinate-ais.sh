#!/bin/bash

# AI Coordination Dashboard
# This script helps coordinate multiple AI editors across worktrees

echo "═══════════════════════════════════════════════════════════════"
echo "🤖 AI Editor Coordination Dashboard"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Function to check if STATUS.md exists and show current AI
check_status() {
    local worktree=$1
    local name=$2
    if [ -f "$worktree/STATUS.md" ]; then
        local current_ai=$(grep -i "current ai:" "$worktree/STATUS.md" 2>/dev/null | cut -d: -f2- | tr -d ' ' || echo "Unassigned")
        local status=$(grep -m1 "Status:" "$worktree/STATUS.md" 2>/dev/null | cut -d: -f2- | tr -d ' ' || echo "Unknown")
        echo "  Current AI: $current_ai | Progress: $status"
    else
        echo "  ⚠️  No STATUS.md found"
    fi
}

echo "📋 Worktree Assignments:"
echo ""

# Main repository
echo "1️⃣ Main Repository (Config/Auth)"
echo "  Path: /Users/joshuafield/Documents/Ultra"
echo "  Branch: chore/config-auth-consolidation"
echo "  Suggested AI: Claude (Primary Session)"
check_status "/Users/joshuafield/Documents/Ultra" "Main"
echo ""

# Testing worktrees
echo "🧪 Testing Worktrees:"
echo ""

echo "2️⃣ Unit Tests"
echo "  Path: ../Ultra-worktrees/test-unit-enhancement"
echo "  Suggested AI: Cursor Window #1"
check_status "../Ultra-worktrees/test-unit-enhancement" "Unit Tests"
echo ""

echo "3️⃣ Integration Tests"
echo "  Path: ../Ultra-worktrees/test-integration-enhancement"
echo "  Suggested AI: Cursor Window #2"
check_status "../Ultra-worktrees/test-integration-enhancement" "Integration Tests"
echo ""

echo "4️⃣ E2E Tests"
echo "  Path: ../Ultra-worktrees/test-e2e-enhancement"
echo "  Suggested AI: ChatGPT/Claude Tab"
check_status "../Ultra-worktrees/test-e2e-enhancement" "E2E Tests"
echo ""

echo "5️⃣ Live/Performance Tests"
echo "  Path: ../Ultra-worktrees/test-live-performance"
echo "  Suggested AI: Specialized (needs API keys)"
check_status "../Ultra-worktrees/test-live-performance" "Live Tests"
echo ""

# Feature worktrees
echo "✨ Feature Worktrees:"
echo ""

echo "6️⃣ UI/UX Improvements"
echo "  Path: ../Ultra-worktrees/ux-ui-improvements"
echo "  Suggested AI: Claude (Tab #2)"
check_status "../Ultra-worktrees/ux-ui-improvements" "UI/UX"
echo ""

echo "7️⃣ Billing System"
echo "  Path: ../Ultra-worktrees/billing-system"
echo "  Suggested AI: GPT-4 or Cursor"
check_status "../Ultra-worktrees/billing-system" "Billing"
echo ""

echo "8️⃣ Service Interfaces"
echo "  Path: ../Ultra-worktrees/service-interfaces"
echo "  Suggested AI: Claude (Tab #3)"
check_status "../Ultra-worktrees/service-interfaces" "Services"
echo ""

echo "9️⃣ Documentation"
echo "  Path: ../Ultra-worktrees/documentation"
echo "  Suggested AI: ChatGPT or Claude"
check_status "../Ultra-worktrees/documentation" "Docs"
echo ""

echo "🔟 CI/CD Pipeline"
echo "  Path: ../Ultra-worktrees/ci-cd"
echo "  Suggested AI: Cursor or GitHub Copilot"
check_status "../Ultra-worktrees/ci-cd" "CI/CD"
echo ""

echo "1️⃣1️⃣ Recovery System"
echo "  Path: ../Ultra-worktrees/recovery-system"
echo "  Suggested AI: Any available"
check_status "../Ultra-worktrees/recovery-system" "Recovery"
echo ""

echo "1️⃣2️⃣ Performance Optimization"
echo "  Path: ../Ultra-worktrees/performance-optimization"
echo "  Suggested AI: Specialized analysis"
check_status "../Ultra-worktrees/performance-optimization" "Performance"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "📊 Quick Commands:"
echo ""
echo "  Update status:    ./scripts/update-worktree-status.sh <worktree> <ai-name>"
echo "  Check all:        ./scripts/check-worktree-status.sh"
echo "  Switch context:   cd ../Ultra-worktrees/<name>"
echo "  Sync status:      git add STATUS.md && git commit -m 'Update AI assignment'"
echo ""
echo "💡 Tips:"
echo "  - Keep STATUS.md updated in each worktree"
echo "  - Commit STATUS.md changes before switching AIs"
echo "  - Use consistent AI names (Claude-1, Cursor-1, etc.)"
echo "═══════════════════════════════════════════════════════════════"