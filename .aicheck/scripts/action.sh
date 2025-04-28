#!/bin/bash
# .aicheck/scripts/action.sh
# RULES.md-compliant action management functions

actions_dir=".aicheck/actions"
index_file=".aicheck/docs/actions_index.md"

# Create a new action
action_create() {
    local action_name="$1"
    local action_dir="$actions_dir/$action_name"
    local plan_file="$action_dir/${action_name}-PLAN.md"
    local status_file="$action_dir/status.md"
    local progress_file="$action_dir/progress.md"
    local docs_dir="$action_dir/supporting_docs"

    if [[ -z "$action_name" ]]; then
        echo "[action_create] Error: Action name required." >&2
        return 1
    fi
    if [[ ! "$action_name" =~ ^[A-Z][a-zA-Z0-9]+$ ]]; then
        echo "[action_create] Error: Action name must be PascalCase (e.g., MyAction)." >&2
        return 1
    fi
    if [[ -d "$action_dir" ]]; then
        echo "[action_create] Error: Action '$action_name' already exists." >&2
        return 1
    fi
    mkdir -p "$docs_dir"
    cat > "$plan_file" <<EOL
# $action_name Action Plan

## Purpose
[Describe the purpose of this action.]

## Value
[Briefly explain the value or benefit of this action to the project.]

## Steps
- [ ] Step 1
- [ ] Step 2

## Notes
EOL
    echo "Not Started" > "$status_file"
    echo "0%" > "$progress_file"
    echo "[action_create] Created action '$action_name' at $action_dir."
}

# Switch to an action
action_switch() {
    local action_name="$1"
    local action_dir="$actions_dir/$action_name"
    local current_action_file=".aicheck/current_action"
    if [[ -z "$action_name" ]]; then
        echo "[action_switch] Error: Action name required." >&2
        return 1
    fi
    if [[ ! -d "$action_dir" ]]; then
        echo "[action_switch] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    echo "$action_name" > "$current_action_file"
    echo "[action_switch] Switched to action '$action_name'."
}

# Show action status
action_status() {
    local action_name="$1"
    local action_dir="$actions_dir/$action_name"
    local plan_file="$action_dir/${action_name}-PLAN.md"
    local status_file="$action_dir/status.md"
    local progress_file="$action_dir/progress.md"
    if [[ -z "$action_name" ]]; then
        echo "[action_status] Error: Action name required." >&2
        return 1
    fi
    if [[ ! -d "$action_dir" ]]; then
        echo "[action_status] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    echo "[action_status] Action: $action_name"
    [[ -f "$status_file" ]] && echo "Status: $(cat "$status_file")"
    [[ -f "$progress_file" ]] && echo "Progress: $(cat "$progress_file")"
    if [[ -f "$plan_file" ]]; then
        echo "Plan file: $plan_file"
        cat "$plan_file"
    else
        echo "No plan file found for action '$action_name'."
    fi
}

# Show system status
system_status() {
    local current_action_file=".aicheck/current_action"
    local current_session_file=".aicheck/current_session"

    echo "=== AICheck System Status ==="

    # Current action
    if [[ -f "$current_action_file" ]]; then
        local current_action=$(cat "$current_action_file")
        echo "Current Action: $current_action"

        # Check action status and progress
        local action_dir="$actions_dir/$current_action"
        local status_file="$action_dir/status.md"
        local progress_file="$action_dir/progress.md"

        if [[ -f "$status_file" ]]; then
            echo "Action Status: $(cat "$status_file")"
        else
            echo "Action Status: Unknown"
        fi

        if [[ -f "$progress_file" ]]; then
            echo "Action Progress: $(cat "$progress_file")"
        else
            echo "Action Progress: Unknown"
        fi
    else
        echo "Current Action: None"
    fi

    # Current session
    if [[ -f "$current_session_file" ]]; then
        local current_session=$(cat "$current_session_file")
        echo "Current Session: $current_session"
    else
        echo "Current Session: None"
    fi

    # Available actions
    echo ""
    echo "Available Actions:"
    if [[ -d "$actions_dir" ]]; then
        for action_dir in "$actions_dir"/*; do
            if [[ -d "$action_dir" ]]; then
                local action_name=$(basename "$action_dir")
                local status="Unknown"
                local progress="Unknown"

                if [[ -f "$action_dir/status.md" ]]; then
                    status=$(cat "$action_dir/status.md")
                fi

                if [[ -f "$action_dir/progress.md" ]]; then
                    progress=$(cat "$action_dir/progress.md")
                fi

                echo "- $action_name (Status: $status, Progress: $progress)"
            fi
        done
    else
        echo "No actions available."
    fi
}

# Delete an action
action_delete() {
    local action_name="$1"
    local action_dir="$actions_dir/$action_name"
    if [[ -z "$action_name" ]]; then
        echo "[action_delete] Error: Action name required." >&2
        return 1
    fi
    if [[ ! -d "$action_dir" ]]; then
        echo "[action_delete] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    rm -rf "$action_dir"
    echo "[action_delete] Deleted action '$action_name'."
}

# Update action status
action_update_status() {
    local action_name="$1"
    local status="$2"
    local status_file="$actions_dir/$action_name/status.md"
    if [[ -z "$action_name" || -z "$status" ]]; then
        echo "[action_update_status] Error: Action name and status required." >&2
        return 1
    fi
    if [[ ! -d "$actions_dir/$action_name" ]]; then
        echo "[action_update_status] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    echo "$status" > "$status_file"
    echo "[action_update_status] Updated status for '$action_name' to '$status'."
}

# Update action progress
action_update_progress() {
    local action_name="$1"
    local progress="$2"
    local progress_file="$actions_dir/$action_name/progress.md"
    if [[ -z "$action_name" || -z "$progress" ]]; then
        echo "[action_update_progress] Error: Action name and progress required." >&2
        return 1
    fi
    if [[ ! -d "$actions_dir/$action_name" ]]; then
        echo "[action_update_progress] Error: Action '$action_name' does not exist." >&2
        return 1
    fi
    echo "$progress" > "$progress_file"
    echo "[action_update_progress] Updated progress for '$action_name' to '$progress'."
}
