#!/bin/bash

# Create a new actions index based on actual directories
cat > .aicheck/docs/actions_index.md << 'EOI'
# UltraAICheck Actions Index

> **Visualizer-Ready**: This file is parsed by the UltraAI Visualizer. Do not change column headers. Maintain consistent formatting to ensure parsing is successful.

This document serves as the central reference for all Actions in the project and is the source of truth for action statuses.

## Core Principle: Every Action Must Have a Plan

The UltraAI Framework operates on the fundamental principle that **every action must have a plan**:

- All substantive work is defined as an action
- Each action requires a formal, documented plan before implementation begins
- All active actions must be listed in this index
- Action plans are stored in the Actions directory with the action name
- No substantive work can proceed without being listed here as an action with a corresponding plan

## Active Actions

| Action | Status | Progress | Owner | Started | Last Updated | Authority | Priority |
|--------|--------|----------|-------|---------|-------------|-----------|----------|
EOI

# Add each action directory to the index
find .aicheck/actions -maxdepth 1 -type d -not -name "actions" | sort | while read -r action_dir; do
    action_name=$(basename "$action_dir")
    
    # Skip the supporting_docs directory if it exists at this level
    if [ "$action_name" = "supporting_docs" ]; then
        continue
    fi
    
    # Check if the action has a plan file
    plan_file="$action_dir/$action_name-PLAN.md"
    if [ -f "$plan_file" ]; then
        # Extract status if possible
        status=$(grep -A 5 "## Status" "$plan_file" | grep "Status:" | sed 's/Status: //')
        if [ -z "$status" ]; then
            status="In Progress"
        fi
        
        # Add to index
        echo "| $action_name | $status | 0% | UltraAI Team | 2025-04-25 | 2025-04-25 | Standard Action | 3 |" >> .aicheck/docs/actions_index.md
    fi
done

# Add the rest of the index template
cat >> .aicheck/docs/actions_index.md << 'EOI'

## Action States

The following status indicators are used throughout the system:
- 🔴 **QUEUED**: Action is scheduled but waiting to start
- 🟡 **WORKING**: Action is currently in progress
- 🟡 **REVIEW**: Action is complete and awaiting review
- ✅ **ACCEPTED**: Action has been completed and accepted
- ⏸️ **PAUSED**: Action is temporarily on hold
- ❌ **ABANDONED**: Action has been discontinued

## Priority Reference

| Priority | Action Type | Description |
|----------|-------------|-------------|
| 1 | Core Architecture | Foundation for all components |
| 2 | Essential Features | Core functionality requirements |
| 3 | Standard Features | Normal priority work |
| 4 | Enhancement | Nice-to-have improvements |
| 5 | Experimental | Exploratory or research work |

## Recent Activity Log

| Date | Action | Activity | Author |
|------|--------|----------|--------|
| 2025-04-25 | Initial | UltraAICheck system installation | UltraAI Team |

## How to Update This Index

This index can be updated using the UltraAICheck commands:
```bash
./ai update-status ActionName "Status"
./ai update-progress ActionName "50%"
./ai statusYou can also manually update it by editing this file directly.
Action Paths
All action documents are stored in .aicheck/actions/[ACTION_NAME]/[ACTION_NAME]-PLAN.md where each action has its own directory containing the plan and all supporting documents.
Last Updated: 2025-04-25
EOI
echo "Actions index rebuilt based on actual directories"
echo "Run ./list_actions.sh to see the updated list"
