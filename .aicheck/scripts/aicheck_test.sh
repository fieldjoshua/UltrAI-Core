#!/bin/bash

# AICheck System Test Suite
# Tests AICheck functionality itself (not project code)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Source required scripts
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/security.sh"
source "$SCRIPT_DIR/action_advanced.sh"

# Function to run a test and update counts
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "\n${YELLOW}Testing: $test_name${NC}"
    
    if eval "$test_command"; then
        echo -e "${GREEN}✓ $test_name passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ $test_name failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS++))
}

# Test security functions
test_security() {
    echo -e "\n${BLUE}Testing Security Functions${NC}"
    
    # Test path validation
    run_test "Valid path validation" "validate_path '.aicheck/test'"
    run_test "Invalid path rejection (absolute)" "! validate_path '/etc/passwd'"
    run_test "Invalid path rejection (traversal)" "! validate_path '.aicheck/../etc/passwd'"
    
    # Test action name validation
    run_test "Valid action name (kebab-case)" "validate_action_name 'my-test-action'"
    run_test "Invalid action name (PascalCase)" "! validate_action_name 'MyTestAction'"
    run_test "Invalid action name (spaces)" "! validate_action_name 'my test action'"
    
    # Test input sanitization
    local sanitized=$(sanitize_input "test-action!@#$%")
    if [[ "$sanitized" == "test-action" ]]; then
        echo -e "${GREEN}✓ Input sanitization passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Input sanitization failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Test action management
test_action_management() {
    echo -e "\n${BLUE}Testing Action Management${NC}"
    
    local test_action="test-action-$(date +%s)"
    local test_action2="test-action2-$(date +%s)"
    
    # Test action creation
    run_test "Action creation" "action_create_advanced '$test_action'"
    
    # Test duplicate action creation (should fail)
    run_test "Duplicate action rejection" "! action_create_advanced '$test_action'"
    
    # Test action status update
    run_test "Status update" "action_update_status '$test_action' 'ActiveAction'"
    
    # Test progress update
    run_test "Progress update" "action_update_progress '$test_action' '50'"
    
    # Test invalid progress (should fail)
    run_test "Invalid progress rejection" "! action_update_progress '$test_action' '150'"
    
    # Test invalid status (should fail)
    run_test "Invalid status rejection" "! action_update_status '$test_action' 'InvalidStatus'"
    
    # Test second action creation
    run_test "Multiple action creation" "action_create_advanced '$test_action2'"
    
    # Test action completion
    run_test "Action completion" "action_complete '$test_action'"
    
    # Verify completed action moved
    if [[ -d ".aicheck/actions/completed/$test_action" ]]; then
        echo -e "${GREEN}✓ Action completion directory move passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Action completion directory move failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    
    # Cleanup
    rm -rf ".aicheck/actions/$test_action2"
    rm -rf ".aicheck/actions/completed/$test_action"
}

# Test file structure validation
test_file_structure() {
    echo -e "\n${BLUE}Testing File Structure${NC}"
    
    # Test directory creation
    local test_action="structure-test-$(date +%s)"
    action_create_advanced "$test_action" > /dev/null
    
    # Check required files exist
    local action_dir=".aicheck/actions/$test_action"
    
    run_test "PLAN.md creation" "[[ -f '$action_dir/PLAN.md' ]]"
    run_test "todo.md creation" "[[ -f '$action_dir/todo.md' ]]"
    run_test "status.txt creation" "[[ -f '$action_dir/status.txt' ]]"
    run_test "progress.txt creation" "[[ -f '$action_dir/progress.txt' ]]"
    run_test "supporting_docs directory" "[[ -d '$action_dir/supporting_docs' ]]"
    
    # Check file permissions
    if check_permissions "$action_dir/status.txt"; then
        echo -e "${GREEN}✓ File permissions test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ File permissions test failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
    
    # Cleanup
    rm -rf "$action_dir"
}

# Test error handling
test_error_handling() {
    echo -e "\n${BLUE}Testing Error Handling${NC}"
    
    # Test missing action name
    run_test "Missing action name error" "! action_create_advanced ''"
    
    # Test invalid action name characters
    run_test "Invalid characters error" "! action_create_advanced 'test/action'"
    
    # Test operations on non-existent action
    run_test "Non-existent action status error" "! action_update_status 'non-existent-action' 'ActiveAction'"
    run_test "Non-existent action progress error" "! action_update_progress 'non-existent-action' '50'"
    run_test "Non-existent action complete error" "! action_complete 'non-existent-action'"
}

# Test system status functionality
test_system_status() {
    echo -e "\n${BLUE}Testing System Status${NC}"
    
    # Create test action for status display
    local test_action="status-test-$(date +%s)"
    action_create_advanced "$test_action" > /dev/null
    action_update_status "$test_action" "ActiveAction" > /dev/null
    action_update_progress "$test_action" "75" > /dev/null
    
    # Test system status display (just check it doesn't error)
    run_test "System status display" "show_system_status > /dev/null"
    
    # Cleanup
    rm -rf ".aicheck/actions/$test_action"
}

# Create test report
generate_test_report() {
    local report_dir=".aicheck/test_reports"
    mkdir -p "$report_dir"
    
    local report_file="$report_dir/aicheck_test_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$report_file" << EOF
AICheck System Test Report
==========================
Date: $(date)

Test Summary:
-------------
Total Tests: $TOTAL_TESTS
Passed: $PASSED_TESTS
Failed: $FAILED_TESTS
Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%

Test Categories:
- Security Functions
- Action Management  
- File Structure
- Error Handling
- System Status

Notes:
- This test suite validates AICheck system functionality
- Does NOT test project-specific code
- Run after AICheck installation or updates
EOF

    echo -e "\n${BLUE}Test report saved:${NC} $report_file"
}

# Main test execution
main() {
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                AICheck System Test Suite                     ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # Ensure required directories exist
    mkdir -p .aicheck/actions .aicheck/actions/completed .aicheck/test_reports
    
    # Run test suites
    test_security
    test_action_management
    test_file_structure
    test_error_handling
    test_system_status
    
    # Generate report
    generate_test_report
    
    # Print summary
    echo -e "\n${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                     Test Summary                             ║${NC}"
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${GREEN}Tests passed: $PASSED_TESTS${NC}"
    echo -e "${RED}Tests failed: $FAILED_TESTS${NC}"
    echo -e "Total tests: $TOTAL_TESTS"
    
    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}✓ All AICheck system tests passed!${NC}"
        exit 0
    else
        echo -e "\n${RED}✗ Some AICheck system tests failed!${NC}"
        exit 1
    fi
}

# Run tests if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi