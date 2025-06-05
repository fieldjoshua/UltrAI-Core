#!/bin/bash
# .aicheck/scripts/common.sh
# Placeholder stub for compatibility with ai script.

# Generate a prompt based on current action and session
generate_prompt() {
    current_action=$(cat .aicheck/current_action 2>/dev/null || echo "None")
    current_session=$(cat .aicheck/current_session 2>/dev/null || echo "None")
    plan_file=".aicheck/actions/$current_action/${current_action}-PLAN.md"
    prompt="Prompt: Current Action: $current_action | Current Session: $current_session"

    if [ -f "$plan_file" ]; then
        # Extract Purpose
        purpose=$(awk '/^## Purpose/{getline; print; exit}' "$plan_file")
        # Extract Value
        value=$(awk '/^## Value/{getline; print; exit}' "$plan_file")
        # Extract Steps (all checklist items)
        steps=$(awk '/^## Steps/{flag=1; next} /^## /{flag=0} flag && /^- \[ \]/ {print}' "$plan_file")

        # Check for missing sections
        missing=""
        grep -q '^## Purpose' "$plan_file" || missing="Purpose"
        grep -q '^## Value' "$plan_file" || missing="$missing Value"
        grep -q '^## Steps' "$plan_file" || missing="$missing Steps"

        [ -n "$purpose" ] && prompt="$prompt\nPurpose: $purpose"
        [ -n "$value" ] && prompt="$prompt\nValue: $value"
        [ -n "$steps" ] && prompt="$prompt\nNext Steps:\n$steps"
        [ -n "$missing" ] && prompt="$prompt\nWARNING: Missing sections:$missing"
    else
        prompt="$prompt\nWARNING: No plan file found for current action."
    fi
    echo -e "$prompt"
}

# Check action status
check_action_status() {
    current_action=$(cat .aicheck/current_action 2>/dev/null || echo "None")
    if [ "$current_action" = "None" ]; then
        echo "No active action."
        return 1
    fi
    plan_file=".aicheck/actions/$current_action/${current_action}-PLAN.md"
    if [ -f "$plan_file" ]; then
        echo "Status for $current_action:"
        grep -i '^Status:' "$plan_file" || echo "No status found."
    else
        echo "Plan file not found for $current_action."
    fi
}

# Update action status
update_action_status() {
    action="$1"
    status="$2"
    plan_file=".aicheck/actions/$action/${action}-PLAN.md"
    if [ ! -f "$plan_file" ]; then
        echo "Plan file not found for $action."
        return 1
    fi
    if grep -q '^Status:' "$plan_file"; then
        sed -i '' "s/^Status:.*/Status: $status/" "$plan_file"
    else
        echo "Status: $status" >> "$plan_file"
    fi
    echo "Updated status for $action to: $status"
}

# Update action progress
update_action_progress() {
    action="$1"
    progress="$2"
    plan_file=".aicheck/actions/$action/${action}-PLAN.md"
    if [ ! -f "$plan_file" ]; then
        echo "Plan file not found for $action."
        return 1
    fi
    if grep -q '^Progress:' "$plan_file"; then
        sed -i '' "s/^Progress:.*/Progress: $progress/" "$plan_file"
    else
        echo "Progress: $progress" >> "$plan_file"
    fi
    echo "Updated progress for $action to: $progress"
}

# Commit changes
git_root=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
commit_changes() {
    msg="$1"
    git -C "$git_root" add .
    git -C "$git_root" commit -m "$msg"
    echo "Committed changes with message: $msg"
}

# Create new action
create_new_action() {
    action="$1"
    action_dir=".aicheck/actions/$action"
    plan_file="$action_dir/${action}-PLAN.md"
    mkdir -p "$action_dir"
    if [ ! -f "$plan_file" ]; then
        echo "# $action Action Plan" > "$plan_file"
        echo "Status: New" >> "$plan_file"
        echo "Progress: 0%" >> "$plan_file"
        echo "Created new action: $action"
    else
        echo "Action $action already exists."
    fi
    echo "$action" > .aicheck/current_action
}

# Switch to action
switch_to_action() {
    action="$1"
    action_dir=".aicheck/actions/$action"
    if [ -d "$action_dir" ]; then
        echo "$action" > .aicheck/current_action
        echo "Switched to action: $action"
    else
        echo "Action $action does not exist."
        return 1
    fi
}

# Validate PascalCase (for Action names)
is_pascal_case() {
    [[ "$1" =~ ^[A-Z][a-zA-Z0-9]+$ ]]
}

# Convert PascalCase to kebab-case (for file names)
pascal_to_kebab() {
    echo "$1" | sed -E 's/([A-Z])/-\L\1/g' | sed 's/^-//'
}

# Log error with code and resolution
log_error() {
    local code="$1"
    local message="$2"
    local resolution="$3"
    echo "[ERROR] $code: $message"
    [[ -n "$resolution" ]] && echo "Resolution: $resolution"
}

# Compliance check for action plans
check_action_plan_compliance() {
    actions_dir=".aicheck/actions"
    compliant=0
    noncompliant=0
    for plan_file in $actions_dir/*/*-PLAN.md; do
        [ -e "$plan_file" ] || continue
        missing=""
        grep -q '^## Purpose' "$plan_file" || missing="Purpose"
        grep -q '^## Value' "$plan_file" || missing="$missing Value"
        grep -q '^## Steps' "$plan_file" || missing="$missing Steps"
        grep -q '^## Notes' "$plan_file" || missing="$missing Notes"
        if [ -z "$missing" ]; then
            echo "[COMPLIANT] $plan_file"
            compliant=$((compliant+1))
        else
            echo "[NONCOMPLIANT] $plan_file -- Missing sections:$missing"
            noncompliant=$((noncompliant+1))
        fi
    done
    echo "\nCompliance summary: $compliant compliant, $noncompliant noncompliant."
}
