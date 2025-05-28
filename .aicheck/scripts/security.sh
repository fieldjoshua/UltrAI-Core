#!/bin/bash

# AICheck Security Utilities
# Universal security functions for any AICheck installation

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Security functions
validate_path() {
    local path="$1"
    # Only allow paths inside .aicheck/, no .. or absolute paths
    if [[ "$path" == .aicheck/* ]] && [[ "$path" != *..* ]] && [[ "$path" != /* ]]; then
        return 0
    else
        return 1
    fi
}

check_permissions() {
    local file="$1"
    # Require 600 permissions (owner read/write only)
    if [ ! -e "$file" ]; then
        return 1
    fi
    perms=$(stat -f %Lp "$file" 2>/dev/null || stat -c %a "$file" 2>/dev/null)
    if [ "$perms" = "600" ]; then
        return 0
    else
        return 1
    fi
}

# Secure logging function
log_security_event() {
    local level="$1"
    local message="$2"
    local logfile=".aicheck/security.log"
    
    # Create log file if it doesn't exist, with 600 permissions
    if [ ! -f "$logfile" ]; then
        touch "$logfile"
        chmod 600 "$logfile"
    fi
    
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $message" >> "$logfile"
    chmod 600 "$logfile"
    return 0
}

# Input sanitization
sanitize_input() {
    local input="$1"
    # Remove any potentially dangerous characters, allow alphanumeric, underscore, hyphen, dot
    echo "$input" | sed 's/[^a-zA-Z0-9_\-\.]//g'
}

# Validate action name format
validate_action_name() {
    local name="$1"
    
    # Must be kebab-case (lowercase, hyphens allowed)
    if [[ "$name" =~ ^[a-z][a-z0-9\-]*[a-z0-9]$ ]] || [[ "$name" =~ ^[a-z]$ ]]; then
        return 0
    else
        echo -e "${RED}Error:${NC} Action name must be kebab-case (e.g., 'my-action', 'feature-implementation')"
        log_security_event "WARN" "Invalid action name attempted: $name"
        return 1
    fi
}

# Secure file creation with proper permissions
create_secure_file() {
    local filepath="$1"
    local content="$2"
    
    # Validate path
    if ! validate_path "$filepath"; then
        echo -e "${RED}Error:${NC} Invalid file path: $filepath"
        log_security_event "ERROR" "Invalid path rejected: $filepath"
        return 1
    fi
    
    # Create directory if needed
    mkdir -p "$(dirname "$filepath")"
    
    # Create file with content
    echo "$content" > "$filepath"
    
    # Set secure permissions
    chmod 600 "$filepath"
    
    log_security_event "INFO" "Secure file created: $filepath"
    return 0
}

# Check if AICheck directory structure is secure
validate_aicheck_security() {
    local issues=0
    
    echo -e "${YELLOW}Validating AICheck security...${NC}"
    
    # Check .aicheck directory permissions
    if [ -d ".aicheck" ]; then
        local perms=$(stat -f %Lp ".aicheck" 2>/dev/null || stat -c %a ".aicheck" 2>/dev/null)
        if [ "$perms" != "755" ] && [ "$perms" != "700" ]; then
            echo -e "${RED}Warning:${NC} .aicheck directory has unusual permissions: $perms"
            ((issues++))
        fi
    fi
    
    # Check for sensitive files with wrong permissions
    for file in .aicheck/current_action .aicheck/security.log; do
        if [ -f "$file" ]; then
            if ! check_permissions "$file"; then
                echo -e "${RED}Warning:${NC} $file has incorrect permissions"
                chmod 600 "$file"
                echo -e "${GREEN}Fixed:${NC} $file permissions corrected"
            fi
        fi
    done
    
    # Check for any world-readable sensitive files
    find .aicheck -type f -perm +044 2>/dev/null | while read -r file; do
        if [[ "$file" == *.log ]] || [[ "$file" == *session* ]] || [[ "$file" == *current_action ]]; then
            echo -e "${RED}Warning:${NC} Sensitive file is world-readable: $file"
            ((issues++))
        fi
    done
    
    if [ $issues -eq 0 ]; then
        echo -e "${GREEN}✓${NC} AICheck security validation passed"
        log_security_event "INFO" "Security validation passed"
    else
        echo -e "${YELLOW}!${NC} $issues security issues found and fixed"
        log_security_event "WARN" "$issues security issues found during validation"
    fi
    
    return $issues
}

# Export functions for use in other scripts
export -f validate_path
export -f check_permissions
export -f log_security_event
export -f sanitize_input
export -f validate_action_name
export -f create_secure_file
export -f validate_aicheck_security