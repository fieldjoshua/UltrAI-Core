#!/bin/bash
# .aicheck/scripts/session.sh
# Session management for AICheck

source .aicheck/scripts/common.sh

# Start a new session
default_session_dir=".aicheck/sessions"
default_current_session_file=".aicheck/current_session"

start_session() {
    mkdir -p "$default_session_dir"
    session_id="session_$(date +%Y%m%d%H%M%S)"
    session_file="$default_session_dir/$session_id.session"
    touch "$session_file"
    echo "$session_id" > "$default_current_session_file"
    echo "Started new session: $session_id"
    echo "Session file: $session_file"

    project_objective_file=".aicheck/docs/project_objective.md"
    if [ ! -f "$project_objective_file" ]; then
        echo "No project objective scope defined. Please enter the project objective scope now:"
        read -r project_scope
        echo "# Project Objective Scope\n\n$project_scope" > "$project_objective_file"
        echo "Project objective scope saved to $project_objective_file."
    else
        echo "Project objective scope is already defined in $project_objective_file."
        echo "Do you want to view or update it? (v = view, u = update, any other key = continue)"
        read -r response
        if [ "$response" = "v" ]; then
            cat "$project_objective_file"
        elif [ "$response" = "u" ]; then
            echo "Enter the new project objective scope:"
            read -r new_scope
            echo "# Project Objective Scope\n\n$new_scope" > "$project_objective_file"
            echo "Project objective scope updated."
        else
            echo "Continuing with existing project objective scope."
        fi
    fi
}

end_session() {
    if [[ ! -f "$default_current_session_file" ]]; then
        log_error "SESSION001" "No active session to end." "Start a session with ./ai start."
        return 1
    fi
    session_id=$(cat "$default_current_session_file")
    echo "Ended session: $session_id"
    rm -f "$default_current_session_file"

    # Auto-generate session summary context file for next chat
    current_action=$(cat .aicheck/current_action 2>/dev/null || echo "None")
    context_dir=".aicheck/cursor"
    mkdir -p "$context_dir"
    context_file="$context_dir/chat_context_${session_id}.md"
    cat > "$context_file" << EOC
# Session Summary Context - $(date +"%Y-%m-%d %H:%M:%S")

## Session ID
$session_id

## Current Action
$current_action

## Action Plan Snapshot

default_plan_file=".aicheck/actions/$current_action/${current_action}-PLAN.md"
if [ "$current_action" != "None" ] && [ -f "$default_plan_file" ]; then
    head -n 20 "$default_plan_file"
    echo "..."
else
    echo "No ActiveAction selected or plan file not found."
fi

## Reference Paths
- RULES.md: Project rules and guidelines (MUST READ)
- .aicheck/actions/: Action-specific directories
- .aicheck/docs/actions_index.md: Action tracking and status
- .aicheck/templates/: Template files
- .aicheck/sessions/: Session data
- .aicheck/current_action: ActiveAction tracking
- .aicheck/current_session: Current active session
EOC

    echo "Session summary context file created: $context_file"
    # Optionally, set this as the default for the next chat (e.g., symlink or copy)
    ln -sf "$context_file" "$context_dir/next_chat_context.md"
    echo "next_chat_context.md now points to the latest session summary."

    # Copy the summary to clipboard for convenience
    if command -v pbcopy &> /dev/null; then
        cat "$context_dir/next_chat_context.md" | pbcopy
        echo "Session summary copied to clipboard."
    elif command -v xclip &> /dev/null; then
        cat "$context_dir/next_chat_context.md" | xclip -selection clipboard
        echo "Session summary copied to clipboard."
    fi

    # Open the summary in the default editor (macOS or Linux)
    if command -v open &> /dev/null; then
        open "$context_dir/next_chat_context.md"
    elif command -v xdg-open &> /dev/null; then
        xdg-open "$context_dir/next_chat_context.md"
    fi
}
