# Vision Guardian Implementation Guide

## Overview

The Vision Guardian system provides **optional, on-demand** IP protection auditing without impeding daily development workflow.

## Implementation Approach

### 🎯 **Practical Integration**
- **NOT mandatory** for every Claude interaction
- **Triggered by specific events** rather than continuous monitoring
- **Preserves development velocity** while protecting critical IP

## Trigger Methods

### 1. **Custom Command** (Manual)
```bash
.aicheck/guardian audit [files/actions]
```

**Usage Examples:**
```bash
# Audit specific files
.aicheck/guardian audit src/core/ultra_pattern_orchestrator.py

# Audit entire action
.aicheck/guardian audit orchestration-integration-fix

# Audit all changes since last commit
.aicheck/guardian audit --staged

# Quick IP protection check
.aicheck/guardian audit --quick
```

### 2. **Git Pre-Push Hook** (Automatic)
```bash
#!/bin/sh
# .git/hooks/pre-push
echo "🛡️ Running Vision Guardian IP protection audit..."
.aicheck/guardian audit --pre-push
if [ $? -ne 0 ]; then
    echo "❌ IP protection concerns detected. Push blocked."
    echo "Run: .aicheck/guardian audit --details for more info"
    exit 1
fi
echo "✅ IP protection audit passed"
```

### 3. **Explicit Request** (Stakeholder)
When patent protection review is specifically requested for:
- Major architectural changes
- Patent-protected feature modifications
- Competitive advantage implementations
- IP-sensitive code reviews

## Guardian Modes

### **ADVISORY** (Default)
- Provides recommendations and warnings
- Does not block development
- Logs concerns for review

### **REVIEW** (Gated)
- Requires explicit approval for flagged changes
- Stakeholder notification on violations
- Temporary development holds for IP issues

### **VETO** (Emergency)
- Blocks problematic changes immediately
- Used only for critical IP protection scenarios
- Requires manual override process

## Implementation Files

### Required Components
1. **Guardian Script**: `.aicheck/guardian` (executable)
2. **Configuration**: `.aicheck/project_vision_config.md`
3. **Vision Rules**: `.aicheck/universal_vision_guardian.md`
4. **Git Hook**: `.git/hooks/pre-push` (optional)

### Example Guardian Command
```bash
#!/bin/bash
# .aicheck/guardian

case "$1" in
    "audit")
        echo "🛡️ Running Vision Guardian audit on: $2"
        # Audit logic here
        ;;
    "status")
        echo "📊 Vision Guardian Status: ADVISORY mode"
        ;;
    "config")
        echo "⚙️ Guardian Configuration:"
        cat .aicheck/project_vision_config.md
        ;;
    *)
        echo "Usage: .aicheck/guardian {audit|status|config} [target]"
        ;;
esac
```

## Benefits of This Approach

### ✅ **Developer-Friendly**
- No interruption to normal Claude Code workflow
- Optional activation when IP protection needed
- Clear, predictable trigger points

### ✅ **IP Protection**
- Automatic scanning before code leaves repository
- Manual audit capability for sensitive changes
- Stakeholder control over protection levels

### ✅ **Flexible Implementation**
- Start with ADVISORY mode
- Upgrade to REVIEW/VETO as needed
- Configurable per project requirements

## Migration from Mandatory Approach

### Before (Mandatory)
```
CRITICAL: All Claude Code interactions MUST be pre-audited by Vision Guardian
```

### After (Optional/Triggered)
```
Vision Guardian consultation available via:
- Custom command for manual audits
- Git pre-push hook for automatic scanning
- Explicit request for IP protection review
```

## Recommendation

**Start with ADVISORY mode + git pre-push hook**:
1. Install git pre-push hook for automatic scanning
2. Use manual `.aicheck/guardian audit` for sensitive changes
3. Upgrade to REVIEW mode only if IP violations occur
4. Keep VETO mode for emergency IP protection only

This provides **IP protection without workflow disruption** while maintaining the ability to strengthen controls if needed.

---

**Status**: Ready for implementation  
**Priority**: Optional - implement when IP protection auditing is specifically needed  
**Complexity**: Low - simple script + git hook integration