#!/bin/bash

# Master test script for AICheck
# This script runs all test suites and generates a comprehensive report

# Exit on error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Create necessary directories
mkdir -p .aicheck/test_reports
mkdir -p .aicheck/sessions
mkdir -p .aicheck/hooks
mkdir -p .aicheck/scripts
mkdir -p .aicheck/actions

# Function to run a test suite and update counts
run_test_suite() {
    local suite_name="$1"
    local script_path="$2"
    
    echo -e "\n${YELLOW}Running $suite_name...${NC}"
    
    if bash "$script_path"; then
        ((PASSED_TESTS++))
        echo -e "${GREEN}✓ $suite_name passed${NC}"
    else
        ((FAILED_TESTS++))
        echo -e "${RED}✗ $suite_name failed${NC}"
    fi
    
    ((TOTAL_TESTS++))
}

# Function to test action management
test_action_management() {
    local test_action="TestAction"
    local test_action2="TestAction2"
    
    echo -e "\n${YELLOW}Testing Action Management...${NC}"
    
    # Test action creation
    if .aicheck/scripts/action.sh create "$test_action"; then
        echo -e "${GREEN}✓ Action creation test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Action creation test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test duplicate action creation (should fail)
    if ! .aicheck/scripts/action.sh create "$test_action"; then
        echo -e "${GREEN}✓ Duplicate action creation test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Duplicate action creation test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test action status
    if .aicheck/scripts/action.sh status "$test_action"; then
        echo -e "${GREEN}✓ Action status test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Action status test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test action switching
    if .aicheck/scripts/action.sh switch "$test_action"; then
        echo -e "${GREEN}✓ Action switching test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Action switching test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test switching to non-existent action (should fail)
    if ! .aicheck/scripts/action.sh switch "NonExistentAction"; then
        echo -e "${GREEN}✓ Non-existent action switch test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Non-existent action switch test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test multiple actions
    if .aicheck/scripts/action.sh create "$test_action2"; then
        echo -e "${GREEN}✓ Multiple action creation test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Multiple action creation test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test switching between multiple actions
    if .aicheck/scripts/action.sh switch "$test_action2" && \
       .aicheck/scripts/action.sh switch "$test_action"; then
        echo -e "${GREEN}✓ Multiple action switching test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Multiple action switching test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Cleanup test actions
    .aicheck/scripts/action.sh delete "$test_action"
    .aicheck/scripts/action.sh delete "$test_action2"
    
    ((TOTAL_TESTS+=7))
}

# Function to test session management
test_session_management() {
    echo -e "\n${YELLOW}Testing Session Management...${NC}"
    
    # Test session creation
    local session_id=$(create_secure_session)
    if [ -n "$session_id" ]; then
        echo -e "${GREEN}✓ Session creation test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Session creation test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test session file permissions
    if [ -f ".aicheck/sessions/${session_id}.session" ]; then
        local perms=$(stat -f %Lp ".aicheck/sessions/${session_id}.session")
        if [ "$perms" -eq 600 ]; then
            echo -e "${GREEN}✓ Session file permissions test passed${NC}"
            ((PASSED_TESTS++))
        else
            echo -e "${RED}✗ Session file permissions test failed${NC}"
            ((FAILED_TESTS++))
        fi
    else
        echo -e "${RED}✗ Session file not found${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Cleanup
    rm -f ".aicheck/sessions/${session_id}.session"
    
    ((TOTAL_TESTS+=2))
}

# Function to test error handling
test_error_handling() {
    echo -e "\n${YELLOW}Testing Error Handling...${NC}"
    
    # Test invalid action name
    if ! .aicheck/scripts/action.sh create "Invalid/Action"; then
        echo -e "${GREEN}✓ Invalid action name test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Invalid action name test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test missing action name
    if ! .aicheck/scripts/action.sh create; then
        echo -e "${GREEN}✓ Missing action name test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Missing action name test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    # Test invalid command
    if ! .aicheck/scripts/action.sh invalid_command; then
        echo -e "${GREEN}✓ Invalid command test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Invalid command test failed${NC}"
        ((FAILED_TESTS++))
    fi
    
    ((TOTAL_TESTS+=3))
}

# Test session start automation

test_session_start_automation() {
    echo -e "\n${YELLOW}Testing Session Start Automation...${NC}"
    # Remove project objective if exists
    rm -f .aicheck/docs/project_objective.md
    # Start session (simulate user input for project objective)
    (echo "Test Project Objective" | .aicheck/scripts/session.sh start_session)
    if [ -f .aicheck/docs/project_objective.md ]; then
        echo -e "${GREEN}✓ Project objective prompt and file creation test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Project objective prompt and file creation test failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Test session end automation

test_session_end_automation() {
    echo -e "\n${YELLOW}Testing Session End Automation...${NC}"
    # Start and end a session to trigger summary creation
    .aicheck/scripts/session.sh start_session > /dev/null
    .aicheck/scripts/session.sh end_session > /dev/null
    # Check for summary context file and symlink
    summary_file=$(ls -t .aicheck/cursor/chat_context_*.md 2>/dev/null | head -n 1)
    symlink_file=.aicheck/cursor/next_chat_context.md
    if [ -f "$summary_file" ] && [ -f "$symlink_file" ]; then
        echo -e "${GREEN}✓ Session summary context file and symlink test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Session summary context file and symlink test failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Test compliance check

test_compliance_check() {
    echo -e "\n${YELLOW}Testing Action Plan Compliance Check...${NC}"
    output=$(bash .aicheck/scripts/common.sh check_action_plan_compliance)
    if echo "$output" | grep -q "[COMPLIANT]"; then
        echo -e "${GREEN}✓ Compliance check test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Compliance check test failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Test prompt generation

test_prompt_generation() {
    echo -e "\n${YELLOW}Testing Prompt Generation...${NC}"
    output=$(bash .aicheck/scripts/common.sh generate_prompt)
    if echo "$output" | grep -q "Purpose:" && echo "$output" | grep -q "Value:" && echo "$output" | grep -q "Next Steps:"; then
        echo -e "${GREEN}✓ Prompt generation test passed${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}✗ Prompt generation test failed${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Run all test suites
echo "Starting AICheck test suite..."
echo "================================"

# Run security tests
run_test_suite "Security Tests" ".aicheck/scripts/test_security.sh"

# Run pre-commit tests
run_test_suite "Pre-commit Tests" ".aicheck/scripts/test_pre_commit.sh"

# Run action management tests
test_action_management

# Run session management tests
test_session_management

# Run error handling tests
test_error_handling

# Run session start automation test
test_session_start_automation

# Run session end automation test
test_session_end_automation

# Run compliance check test
test_compliance_check

# Run prompt generation test
test_prompt_generation

# Generate test report
REPORT_FILE=".aicheck/test_reports/test_report_$(date +%Y%m%d_%H%M%S).txt"
{
    echo "AICheck Test Report"
    echo "==================="
    echo "Date: $(date)"
    echo ""
    echo "Test Summary:"
    echo "-------------"
    echo "Total Tests: $TOTAL_TESTS"
    echo "Passed: $PASSED_TESTS"
    echo "Failed: $FAILED_TESTS"
    echo ""
    echo "Test Suites:"
    echo "- Security Tests"
    echo "- Pre-commit Tests"
    echo "- Action Management Tests"
    echo "- Session Management Tests"
    echo "- Error Handling Tests"
    echo "- Session Start Automation Tests"
    echo "- Session End Automation Tests"
    echo "- Compliance Check Tests"
    echo "- Prompt Generation Tests"
    echo ""
    echo "Detailed Results:"
    echo "----------------"
    echo "Action Management:"
    echo "- Action creation"
    echo "- Duplicate action handling"
    echo "- Action status checking"
    echo "- Action switching"
    echo "- Multiple action management"
    echo ""
    echo "Session Management:"
    echo "- Session creation"
    echo "- Session file permissions"
    echo ""
    echo "Error Handling:"
    echo "- Invalid action names"
    echo "- Missing parameters"
    echo "- Invalid commands"
} > "$REPORT_FILE"

# Print summary
echo -e "\n================================"
echo -e "Test Summary:"
echo -e "${GREEN}Tests passed: $PASSED_TESTS${NC}"
echo -e "${RED}Tests failed: $FAILED_TESTS${NC}"
echo -e "Total tests: $TOTAL_TESTS"
echo -e "\nTest report generated: $REPORT_FILE"

# Exit with status
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "\n${RED}Some tests failed!${NC}"
    exit 1
fi 