#!/bin/bash

# UltraAICheck Common Functions
# Shared functions used by multiple scripts

# Function to check if a session is active
check_session() {
    current_session=$(cat .aicheck/current_session 2>/dev/null || echo "")
    if [ -z "$current_session" ]; then
        return 1
    fi
    return 0
}

# Function to check if an action is active
check_action() {
    current_action=$(cat .aicheck/current_action 2>/dev/null || echo "")
    if [ -z "$current_action" ]; then
        return 1
    fi
    return 0
}

# Function to get action status from index
get_action_status() {
    action_name=$1
    default_status=${2:-Unknown}
    
    if [ -f ".aicheck/docs/actions_index.md" ]; then
        action_line=$(grep -E "^\| $action_name \|" .aicheck/docs/actions_index.md)
        if [ -n "$action_line" ]; then
            status=$(echo "$action_line" | awk -F'|' '{print $3}' | xargs)
            if [ -n "$status" ]; then
                echo "$status"
                return 0
            fi
        fi
    fi
    
    # Fallback to checking action file
    if [ -f ".aicheck/actions/$action_name/$action_name-PLAN.md" ]; then
        status=$(grep -A 5 "## Status" ".aicheck/actions/$action_name/$action_name-PLAN.md" | grep "Status:" | sed 's/Status: //')
        if [ -n "$status" ]; then
            echo "$status"
            return 0
        fi
    fi
    
    echo "$default_status"
    return 1
}

# Function to get action progress from index
get_action_progress() {
    action_name=$1
    default_progress=${2:-0%}
    
    if [ -f ".aicheck/docs/actions_index.md" ] && grep -q "Progress" ".aicheck/docs/actions_index.md"; then
        action_line=$(grep -E "^\| $action_name \|" .aicheck/docs/actions_index.md)
        if [ -n "$action_line" ]; then
            progress=$(echo "$action_line" | awk -F'|' '{print $4}' | xargs)
            if [ -n "$progress" ]; then
                echo "$progress"
                return 0
            fi
        fi
    fi
    
    echo "$default_progress"
    return 1
}

# Function to list supporting documents for an action
list_supporting_docs() {
    action_name=$1
    
    if [ -d ".aicheck/actions/$action_name/supporting_docs" ]; then
        find ".aicheck/actions/$action_name/supporting_docs" -type f | while read -r doc; do
            basename "$doc"
        done
        return 0
    fi
    
    return 1
}

# Function to generate a documentation index
generate_doc_index() {
    output_file=".aicheck/docs/doc_index.md"
    
    echo "# UltraAICheck Documentation Index" > "$output_file"
    echo "Generated: $(date +"%Y-%m-%d %H:%M:%S")" >> "$output_file"
    echo "" >> "$output_file"
    
    echo "## Action Plans" >> "$output_file"
    find .aicheck/actions -type d -maxdepth 1 -mindepth 1 | sort | while read action_dir; do
        action_name=$(basename "$action_dir")
        if [ -f "$action_dir/$action_name-PLAN.md" ]; then
            action_title=$(head -n 1 "$action_dir/$action_name-PLAN.md" | sed 's/^# //')
            echo "- [$action_name]($action_dir/$action_name-PLAN.md) - $action_title" >> "$output_file"
        fi
    done
    
    echo "" >> "$output_file"
    echo "## Supporting Documents" >> "$output_file"
    find .aicheck/actions -path "*/supporting_docs/*" -type f | sort | while read doc_file; do
        doc_name=$(basename "$doc_file")
        action_name=$(echo "$doc_file" | awk -F'/' '{print $(NF-2)}')
        doc_title=$(head -n 1 "$doc_file" | sed 's/^# //')
        echo "- [$action_name: $doc_name]($doc_file) - $doc_title" >> "$output_file"
    done
    
    echo "" >> "$output_file"
    echo "## Sessions" >> "$output_file"
    find .aicheck/sessions -maxdepth 1 -type d | sort | tail -n +2 | while read session_dir; do
        session_id=$(basename "$session_dir")
        summary_file="$session_dir/summary.md"
        if [ -f "$summary_file" ]; then
            summary=$(grep "Summary:" "$summary_file" | sed 's/- Summary: //')
            echo "- [$session_id]($session_dir) - $summary" >> "$output_file"
        else
            echo "- [$session_id]($session_dir)" >> "$output_file"
        fi
    done
    
    echo "Documentation index generated at $output_file"
}
