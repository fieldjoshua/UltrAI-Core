#!/bin/bash
# Documentation detection hook
# Detects newly added documentation files and alerts the user to decide if they should be added to the documentation index

# Colors for output
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Documentation backup directory - this folder won't be touched by editors
DOCS_BACKUP_DIR=".aicheck/docs/backup"

# Ensure backup directory exists
ensure_backup_dir() {
    if [ ! -d "$DOCS_BACKUP_DIR" ]; then
        mkdir -p "$DOCS_BACKUP_DIR"
    fi
}

# Copy documentation file to backup directory
backup_documentation() {
    local file="$1"
    local action_name="$2"
    
    # Create action subdirectory in backup if it doesn't exist
    local backup_action_dir="$DOCS_BACKUP_DIR/$action_name"
    if [ ! -d "$backup_action_dir" ]; then
        mkdir -p "$backup_action_dir"
    fi
    
    # Get the filename
    local filename=$(basename "$file")
    
    # Copy the file to backup directory
    cp "$file" "$backup_action_dir/$filename"
    echo -e "${GREEN}Backed up documentation to ${BLUE}$backup_action_dir/$filename${NC}"
}

# Check for new documentation files
detect_documentation() {
    # Ensure backup directory exists
    ensure_backup_dir
    
    # Get files being committed
    local files=$(git diff --cached --name-only)
    local new_docs=()
    
    # Look for documentation files in action directories
    for file in $files; do
        # Check if it's a markdown file in an action supporting_docs directory
        if [[ "$file" == .aicheck/actions/*/supporting_docs/*.md ]]; then
            # Extract action name from path
            action_name=$(echo "$file" | sed -n 's|.aicheck/actions/\([^/]*\)/.*|\1|p')
            
            # Skip if it's a plan file
            if [[ "$file" == *"$action_name-PLAN.md" ]]; then
                continue
            fi
            
            # Get file name for the document title
            doc_title=$(basename "$file" .md)
            # Convert kebab-case to Title Case
            doc_title=$(echo "$doc_title" | sed -E 's/(^|-)([a-z])/\U\2/g' | sed 's/-/ /g')
            
            # Backup the documentation file
            backup_documentation "$file" "$action_name"
            
            new_docs+=("$action_name:$doc_title:$file")
        fi
    done
    
    # If we found new documentation files, display a mandatory alert but make indexing optional
    if [ ${#new_docs[@]} -gt 0 ]; then
        echo -e "${BOLD}${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}${YELLOW}║                 !!! DOCUMENTATION ALERT !!!                    ║${NC}"
        echo -e "${BOLD}${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo -e "${YELLOW}Found ${#new_docs[@]} new documentation file(s) in action directories:${NC}"
        for i in "${!new_docs[@]}"; do
            IFS=':' read -ra DOC_INFO <<< "${new_docs[$i]}"
            action_name="${DOC_INFO[0]}"
            doc_title="${DOC_INFO[1]}"
            file_path="${DOC_INFO[2]}"
            echo -e "${YELLOW}$((i+1)). ${BOLD}$doc_title${NC} ${YELLOW}(Action: $action_name)${NC}"
        done
        
        echo -e "\n${BLUE}About Documentation Indexing:${NC}"
        echo -e "${BLUE}• Documentation indexes improve discoverability of important documents${NC}"
        echo -e "${BLUE}• Adding documents to the index makes them easier to find for all team members${NC}"
        echo -e "${BLUE}• Without indexing, documents may be forgotten or difficult to locate later${NC}"
        echo -e "${BLUE}• The documentation index is maintained at .aicheck/docs/documentation_index.md${NC}"
        echo -e "${BLUE}• A backup copy of all documentation is stored in ${DOCS_BACKUP_DIR}${NC}"
        
        echo -e "\n${BOLD}${YELLOW}Would you like to add these documents to the documentation index? (y/n)${NC}"
        read -r add_to_index
        
        if [ "$add_to_index" = "y" ]; then
            for doc_info in "${new_docs[@]}"; do
                IFS=':' read -ra DOC_INFO <<< "$doc_info"
                action_name="${DOC_INFO[0]}"
                doc_title="${DOC_INFO[1]}"
                file_path="${DOC_INFO[2]}"
                
                echo -e "Adding '${BOLD}$doc_title${NC}' to documentation index..."
                
                # Use default description without prompting
                doc_desc="Supporting documentation for $action_name"
                
                # Add to documentation index
                ./ai docs add "$action_name" "$doc_title" "$file_path" "$doc_desc"
            done
            
            echo -e "${GREEN}Documents added to documentation index.${NC}"
            echo -e "${YELLOW}Note: Changes to the documentation index will be included in your commit.${NC}"
            git add .aicheck/docs/documentation_index.md
            # Also add the backup directory to git
            git add "$DOCS_BACKUP_DIR"
        else
            echo -e "${YELLOW}Documents not added to index. You can add them later with './ai docs add'.${NC}"
            echo -e "${YELLOW}Remember: Undocumented files may be difficult to find in the future.${NC}"
            echo -e "${GREEN}All documentation has been backed up to ${BLUE}${DOCS_BACKUP_DIR}${NC}"
            # Add the backup directory to git even if not indexed
            git add "$DOCS_BACKUP_DIR"
        fi
    fi
    
    return 0
}

# Function to scan for all markdown files in action directories
scan_all_documentation() {
    echo -e "${BLUE}Scanning for all documentation files in action directories...${NC}"
    
    # Ensure backup directory exists
    ensure_backup_dir
    
    # Find all markdown files in supporting_docs directories
    local all_docs=()
    local documentation_index=".aicheck/docs/documentation_index.md"
    
    # Skip if documentation index doesn't exist
    if [ ! -f "$documentation_index" ]; then
        echo -e "${YELLOW}Documentation index not found. Creating it now...${NC}"
        ./ai docs list > /dev/null
    fi
    
    # Find all markdown files in action supporting_docs directories
    while IFS= read -r file; do
        # Extract action name from path
        action_name=$(echo "$file" | sed -n 's|.aicheck/actions/\([^/]*\)/.*|\1|p')
        
        # Skip if it's a plan file
        if [[ "$file" == *"$action_name-PLAN.md" ]]; then
            continue
        fi
        
        # Backup the documentation file
        backup_documentation "$file" "$action_name"
        
        # Get file name for the document title
        doc_title=$(basename "$file" .md)
        # Convert kebab-case to Title Case
        doc_title=$(echo "$doc_title" | sed -E 's/(^|-)([a-z])/\U\2/g' | sed 's/-/ /g')
        
        # Check if the file is already in the documentation index
        if ! grep -q "$file" "$documentation_index"; then
            all_docs+=("$action_name:$doc_title:$file")
        fi
    done < <(find .aicheck/actions -path "*/supporting_docs/*.md" -type f)
    
    # Stage backup directory changes
    git add "$DOCS_BACKUP_DIR"
    
    # If we found documentation files not in the index, display a mandatory alert
    if [ ${#all_docs[@]} -gt 0 ]; then
        echo -e "${BOLD}${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${BOLD}${YELLOW}║              !!! UNDOCUMENTED FILES ALERT !!!                  ║${NC}"
        echo -e "${BOLD}${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
        echo -e "${YELLOW}Found ${#all_docs[@]} documentation file(s) not in the documentation index:${NC}"
        for i in "${!all_docs[@]}"; do
            IFS=':' read -ra DOC_INFO <<< "${all_docs[$i]}"
            action_name="${DOC_INFO[0]}"
            doc_title="${DOC_INFO[1]}"
            file_path="${DOC_INFO[2]}"
            echo -e "${YELLOW}$((i+1)). ${BOLD}$doc_title${NC} ${YELLOW}(Action: $action_name)${NC}"
        done
        
        echo -e "\n${BLUE}About Documentation Indexing:${NC}"
        echo -e "${BLUE}• Documentation indexes improve discoverability of important documents${NC}"
        echo -e "${BLUE}• Adding documents to the index makes them easier to find for all team members${NC}"
        echo -e "${BLUE}• Without indexing, documents may be forgotten or difficult to locate later${NC}"
        echo -e "${BLUE}• The documentation index is maintained at .aicheck/docs/documentation_index.md${NC}"
        echo -e "${BLUE}• A backup copy of all documentation is stored in ${DOCS_BACKUP_DIR}${NC}"
        
        echo -e "\n${BOLD}${YELLOW}Would you like to add these documents to the documentation index? (y/n)${NC}"
        read -r add_to_index
        
        if [ "$add_to_index" = "y" ]; then
            for doc_info in "${all_docs[@]}"; do
                IFS=':' read -ra DOC_INFO <<< "$doc_info"
                action_name="${DOC_INFO[0]}"
                doc_title="${DOC_INFO[1]}"
                file_path="${DOC_INFO[2]}"
                
                echo -e "Adding '${BOLD}$doc_title${NC}' to documentation index..."
                
                # Use default description without prompting
                doc_desc="Supporting documentation for $action_name"
                
                # Add to documentation index
                ./ai docs add "$action_name" "$doc_title" "$file_path" "$doc_desc"
            done
            
            echo -e "${GREEN}Documents added to documentation index.${NC}"
            # Add the documentation index to git
            git add .aicheck/docs/documentation_index.md
        else
            echo -e "${YELLOW}Documents not added to index. You can add them later with './ai docs add'.${NC}"
            echo -e "${YELLOW}Remember: Undocumented files may be difficult to find in the future.${NC}"
            echo -e "${GREEN}All documentation has been backed up to ${BLUE}${DOCS_BACKUP_DIR}${NC}"
        fi
    else
        echo -e "${GREEN}All documentation files are properly indexed.${NC}"
        echo -e "${GREEN}All documentation has been backed up to ${BLUE}${DOCS_BACKUP_DIR}${NC}"
    fi
}

# Check for command line arguments
if [ "$1" = "--scan-all" ]; then
    scan_all_documentation
else
    # Run the detection as part of the pre-commit hook
    detect_documentation
fi 