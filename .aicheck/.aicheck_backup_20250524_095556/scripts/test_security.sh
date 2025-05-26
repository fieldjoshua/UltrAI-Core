#!/bin/bash
set +e

# Security test script for AICheck
# This script tests all security features and utilities

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create necessary directories
mkdir -p .aicheck/sessions
mkdir -p .aicheck/hooks
mkdir -p .aicheck/scripts
mkdir -p .aicheck/actions

# Source security utilities
source .aicheck/scripts/security_utils.sh

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_exit="$3"

    echo -e "${YELLOW}Running test: $test_name${NC}"

    # Run the test command in a subshell
    ( eval "$test_command" )
    local exit_code=$?
    if [ "$exit_code" -eq "$expected_exit" ]; then
        echo -e "${GREEN}✓ Test passed: $test_name${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ Test failed: $test_name (exit code $exit_code, expected $expected_exit)${NC}"
        ((TESTS_FAILED++))
    fi
}

# Test path validation
test_path_validation() {
    echo -e "\n${YELLOW}Testing path validation...${NC}"

    # Test valid path
    run_test "Valid path" "validate_path .aicheck/scripts" 0

    # Test invalid path
    run_test "Invalid path" "validate_path /etc/passwd" 1

    # Test path traversal attempt
    run_test "Path traversal" "validate_path .aicheck/../../etc/passwd" 1
}

# Test permission checks
test_permission_checks() {
    echo -e "\n${YELLOW}Testing permission checks...${NC}"

    # Create test file
    touch .aicheck/test_file
    chmod 600 .aicheck/test_file

    # Test valid permissions
    run_test "Valid permissions" "check_permissions .aicheck/test_file" 0

    # Test invalid permissions
    chmod 777 .aicheck/test_file
    run_test "Invalid permissions" "check_permissions .aicheck/test_file" 1

    # Cleanup
    rm .aicheck/test_file
}

# Test logging
test_logging() {
    echo -e "\n${YELLOW}Testing security logging...${NC}"

    # Test info logging
    run_test "Info logging" "log_security_event 'INFO' 'Test info message'" 0

    # Test error logging
    run_test "Error logging" "log_security_event 'ERROR' 'Test error message'" 0

    # Verify log file permissions (macOS compatible)
    run_test "Log file permissions" "[ $(stat -f %Lp .aicheck/security.log) -eq 600 ]" 0
}

# Test checksum verification
test_checksum() {
    echo -e "\n${YELLOW}Testing checksum verification...${NC}"

    # Create test file
    echo "test content" > .aicheck/test_file

    # Generate checksum (macOS compatible)
    local checksum=$(shasum -a 256 .aicheck/test_file | cut -d' ' -f1)

    # Test valid checksum
    run_test "Valid checksum" "verify_checksum .aicheck/test_file '$checksum'" 0

    # Test invalid checksum
    run_test "Invalid checksum" "verify_checksum .aicheck/test_file 'invalid'" 1

    # Cleanup
    rm .aicheck/test_file
}

# Test configuration encryption
test_config_encryption() {
    echo -e "\n${YELLOW}Testing configuration encryption...${NC}"

    # Create test files
    echo "test config" > .aicheck/test_config
    openssl rand -hex 32 > .aicheck/test_key

    # Test encryption
    run_test "Config encryption" "encrypt_config .aicheck/test_config .aicheck/test_key" 0

    # Test decryption
    run_test "Config decryption" "decrypt_config .aicheck/test_config .aicheck/test_key" 0

    # Verify file permissions (macOS compatible)
    run_test "Encrypted file permissions" "[ $(stat -f %Lp .aicheck/test_config.enc) -eq 600 ]" 0

    # Cleanup
    rm .aicheck/test_config .aicheck/test_config.enc .aicheck/test_key
}

# Test input sanitization
test_input_sanitization() {
    echo -e "\n${YELLOW}Testing input sanitization...${NC}"

    # Test clean input
    run_test "Clean input" "[ \"$(sanitize_input 'test123')\" = 'test123' ]" 0

    # Test input with special characters
    run_test "Special characters" "[ \"$(sanitize_input 'test!@#$%^&*()')\" = 'test' ]" 0

    # Test input with spaces
    run_test "Spaces" "[ \"$(sanitize_input 'test 123')\" = 'test123' ]" 0
}

# Test session management
test_session_management() {
    echo -e "\n${YELLOW}Testing session management...${NC}"

    # Test session creation
    local session_id=$(create_secure_session)
    run_test "Session creation" "[ -n \"$session_id\" ]" 0

    # Test session file permissions (macOS compatible)
    run_test "Session file permissions" "[ $(stat -f %Lp .aicheck/sessions/${session_id}.session) -eq 600 ]" 0

    # Cleanup
    rm .aicheck/sessions/${session_id}.session
}

# Run all tests
echo "Starting security tests..."
echo "--------------------------------"

test_path_validation
test_permission_checks
test_logging
test_checksum
test_config_encryption
test_input_sanitization
test_session_management

# Print summary
echo -e "\n--------------------------------"
echo -e "Test Summary:"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"
echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
echo -e "Total tests: $((TESTS_PASSED + TESTS_FAILED))"

# Exit with appropriate status
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}All security tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some security tests failed!${NC}"
    exit 1
fi
