#!/bin/bash

# Security utilities for AICheck
# This script provides security-related functions for AICheck

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

# Checksum verification
verify_checksum() {
    local file="$1"
    local expected_checksum="$2"
    
    # Validate file path
    validate_path "$file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_security_event "ERROR" "File not found: $file"
        return 1
    fi
    
    # Calculate checksum (macOS compatible)
    local actual_checksum=$(shasum -a 256 "$file" | cut -d' ' -f1)
    
    # Compare checksums
    if [ "$actual_checksum" != "$expected_checksum" ]; then
        log_security_event "ERROR" "Checksum mismatch for $file"
        return 1
    fi
    
    log_security_event "INFO" "Checksum verified for $file"
    return 0
}

# Generate checksum
generate_checksum() {
    local file="$1"
    
    # Validate file path
    validate_path "$file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_security_event "ERROR" "File not found: $file"
        return 1
    fi
    
    # Generate and return checksum (macOS compatible)
    shasum -a 256 "$file" | cut -d' ' -f1
}

# Secure configuration handling
encrypt_config() {
    local config_file="$1"
    local key_file="$2"
    
    # Validate paths
    validate_path "$config_file"
    validate_path "$key_file"
    
    # Check if files exist
    if [ ! -f "$config_file" ] || [ ! -f "$key_file" ]; then
        log_security_event "ERROR" "Config or key file not found"
        return 1
    fi
    
    # Encrypt config file
    openssl enc -aes-256-cbc -salt -in "$config_file" -out "${config_file}.enc" -pass file:"$key_file"
    
    # Set secure permissions
    chmod 600 "${config_file}.enc"
    chmod 600 "$key_file"
    
    log_security_event "INFO" "Config file encrypted: $config_file"
}

# Decrypt configuration
decrypt_config() {
    local config_file="$1"
    local key_file="$2"
    
    # Validate paths
    validate_path "$config_file"
    validate_path "$key_file"
    
    # Check if files exist
    if [ ! -f "${config_file}.enc" ] || [ ! -f "$key_file" ]; then
        log_security_event "ERROR" "Encrypted config or key file not found"
        return 1
    fi
    
    # Decrypt config file
    openssl enc -aes-256-cbc -d -in "${config_file}.enc" -out "$config_file" -pass file:"$key_file"
    
    # Set secure permissions
    chmod 600 "$config_file"
    
    log_security_event "INFO" "Config file decrypted: $config_file"
}

# Input sanitization
sanitize_input() {
    local input="$1"
    # Remove any potentially dangerous characters
    echo "$input" | sed 's/[^a-zA-Z0-9_\-\.]//g'
}

# Session management
create_secure_session() {
    local session_id=$(openssl rand -hex 16)
    local session_file=".aicheck/sessions/${session_id}.session"
    
    # Create session directory if it doesn't exist
    mkdir -p "$(dirname "$session_file")"
    
    # Create session file with secure permissions
    touch "$session_file"
    chmod 600 "$session_file"
    
    # Log session creation
    log_security_event "INFO" "Secure session created: $session_id"
    
    echo "$session_id"
}

# Export functions for use in other scripts
export -f validate_path
export -f check_permissions
export -f log_security_event
export -f verify_checksum
export -f generate_checksum
export -f encrypt_config
export -f decrypt_config
export -f sanitize_input
export -f create_secure_session 