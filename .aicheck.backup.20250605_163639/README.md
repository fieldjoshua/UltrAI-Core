# AICheck System

## Overview

AICheck is a documentation-first, test-driven development workflow system that ensures quality through structured processes and clear accountability.

## Quick Start

1. **Create an action**: `aicheck create-action my-feature`
2. **Edit the plan**: Edit `.aicheck/actions/my-feature/PLAN.md`
3. **Set as active**: `aicheck set-action my-feature`
4. **Work on tasks**: Track progress in `todo.md`
5. **Complete action**: `aicheck complete-action my-feature`

## Key Commands

- `aicheck create-action <name>` - Create new action
- `aicheck status` - Show current action
- `aicheck list` - List all actions
- `aicheck help` - Show help

## Directory Structure

```
.aicheck/
├── actions/              # All project actions
├── templates/            # Action templates
├── hooks/                # Git hooks
├── scripts/              # Utility scripts
├── RULES.md              # System rules
└── actions_index.md      # Action dashboard
```

## Core Principles

1. **Documentation First** - Document before implementing
2. **Test-Driven** - Write tests before code
3. **Single Focus** - One active action per editor
4. **Approval Required** - Plans need human approval
5. **Complete or Cancel** - No abandoned actions

## Getting Help

- Read the full rules: `.aicheck/RULES.md`
- Check action status: `.aicheck/actions_index.md`
- Review timeline: `.aicheck/ACTION_TIMELINE.md`

## Version

AICheck v4.0 (2025-05-27)
