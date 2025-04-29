#!/bin/bash
# .aicheck/scripts/session.sh
# Session management for AICheck

# Get the absolute path to the script directory if not already defined
if [ -z "$AICHECK_DIR" ]; then
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    AICHECK_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"
fi

source "$AICHECK_DIR/scripts/common.sh"

# Start a new session
default_session_dir="$AICHECK_DIR/sessions"
default_current_session_file="$AICHECK_DIR/current_session"
initialization_file="$AICHECK_DIR/initialization_completed"

start_session() {
    mkdir -p "$default_session_dir"
    session_id="session_$(date +%Y%m%d%H%M%S)"
    session_file="$default_session_dir/$session_id.session"
    touch "$session_file"
    echo "$session_id" > "$default_current_session_file"
    echo "Started new session: $session_id"
    echo "Session file: $session_file"

    # Check if this is the first time running AICheck
    if [ ! -f "$initialization_file" ]; then
        echo "====================================================================="
        echo "                    WELCOME TO AICHECK INITIAL SETUP                 "
        echo "====================================================================="
        echo ""
        echo "This appears to be your first time using AICheck with this project."
        echo "Let's set up your initial configuration and product vision."
        echo ""
        
        # Create initialization-specific ProductVision action
        action_name="ProductVision"
        action_dir="$AICHECK_DIR/actions/$action_name"
        
        if [ ! -d "$action_dir" ]; then
            mkdir -p "$action_dir"
            echo "Creating ProductVision action for initial setup..."
            
            # Use the product vision template for the plan
            if [ -f "$AICHECK_DIR/templates/product_vision_template.md" ]; then
                cat "$AICHECK_DIR/templates/product_vision_template.md" > "$action_dir/$action_name-PLAN.md"
                echo "Product vision template loaded. Please edit it to define your project."
            else
                # Fallback to standard action plan template
                if [ -f "$AICHECK_DIR/templates/action_plan_template.md" ]; then
                    cat "$AICHECK_DIR/templates/action_plan_template.md" > "$action_dir/$action_name-PLAN.md"
                    sed -i '' "s/{{ACTION_NAME}}/$action_name/g" "$action_dir/$action_name-PLAN.md"
                else
                    echo "# $action_name Action Plan" > "$action_dir/$action_name-PLAN.md"
                    echo "" >> "$action_dir/$action_name-PLAN.md"
                    echo "## Purpose" >> "$action_dir/$action_name-PLAN.md"
                    echo "" >> "$action_dir/$action_name-PLAN.md"
                    echo "Define the product vision, scope, and goals." >> "$action_dir/$action_name-PLAN.md"
                fi
            fi
            
            # Set initial status and progress
            echo "Not Started" > "$action_dir/status.md"
            echo "0%" > "$action_dir/progress.md"
            
            # Set as current action
            echo "$action_name" > "$AICHECK_DIR/current_action"
            
            # Create supporting docs directory
            mkdir -p "$action_dir/supporting_docs"
            
            # Copy initialization template to supporting docs
            if [ -f "$AICHECK_DIR/templates/initialization_template.md" ]; then
                cp "$AICHECK_DIR/templates/initialization_template.md" "$action_dir/supporting_docs/AICheckSetup.md"
                echo "Initialization template copied to $action_dir/supporting_docs/AICheckSetup.md"
            fi
            
            echo ""
            echo "Initial ProductVision action created and set as ActiveAction."
            echo "Next steps:"
            echo "1. Edit the ProductVision plan at $action_dir/$action_name-PLAN.md"
            echo "2. Review the AICheck setup guide at $action_dir/supporting_docs/AICheckSetup.md"
            echo ""
            echo "Would you like to open these files now? (y/n)"
            read -r open_files
            
            if [ "$open_files" = "y" ]; then
                if command -v open &> /dev/null; then
                    open "$action_dir/$action_name-PLAN.md"
                    open "$action_dir/supporting_docs/AICheckSetup.md"
                elif command -v xdg-open &> /dev/null; then
                    xdg-open "$action_dir/$action_name-PLAN.md"
                    xdg-open "$action_dir/supporting_docs/AICheckSetup.md"
                else
                    echo "Unable to open files automatically. Please open them manually."
                fi
            fi
            
            # Mark initialization as completed
            touch "$initialization_file"
        fi
    else
        project_objective_file="$AICHECK_DIR/docs/project_objective.md"
        if [ ! -f "$project_objective_file" ]; then
            echo "No project objective scope defined. Please enter the project objective scope now:"
            read -r project_scope
            mkdir -p "$(dirname "$project_objective_file")"
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
    current_action=$(cat "$AICHECK_DIR/current_action" 2>/dev/null || echo "None")
    context_dir="$AICHECK_DIR/cursor"
    mkdir -p "$context_dir"
    context_file="$context_dir/chat_context_${session_id}.md"
    cat > "$context_file" << EOC
# Session Summary Context - $(date +"%Y-%m-%d %H:%M:%S")

## Session ID
$session_id

## Current Action
$current_action

## Action Plan Snapshot

default_plan_file="$AICHECK_DIR/actions/$current_action/${current_action}-PLAN.md"
if [ "$current_action" != "None" ] && [ -f "$default_plan_file" ]; then
    head -n 20 "$default_plan_file"
    echo "..."
else
    echo "No ActiveAction selected or plan file not found."
fi

## Reference Paths
- RULES.md: Project rules and guidelines (MUST READ)
- $AICHECK_DIR/actions/: Action-specific directories
- $AICHECK_DIR/docs/actions_index.md: Action tracking and status
- $AICHECK_DIR/templates/: Template files
- $AICHECK_DIR/sessions/: Session data
- $AICHECK_DIR/current_action: ActiveAction tracking
- $AICHECK_DIR/current_session: Current active session
EOC

    echo "Session summary context file created: $context_file"
    # Create a symlink to the latest session summary with absolute paths
    context_file_abs=$(realpath "$context_file")
    next_context_file_abs=$(realpath "$context_dir/next_chat_context.md" 2>/dev/null || echo "$context_dir/next_chat_context.md")
    rm -f "$context_dir/next_chat_context.md"  # Remove old symlink if it exists
    ln -sf "$context_file_abs" "$next_context_file_abs"
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