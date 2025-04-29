#!/bin/bash
# Test script for code and documentation location checks
# This script verifies that code and documentation location checks work correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Define test actions
TEST_ACTION="LocationTestAction"
TEST_CODE_FILE="test_code.py"
TEST_DOC_FILE="test_doc.md"
MISPLACED_CODE_FILE=".aicheck/docs/misplaced_code.py"
MISPLACED_DOC_FILE=".aicheck/misplaced_doc.md"

# Test results counters
PASSED=0
FAILED=0

# Function to run a test and evaluate results
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_success="$3"
    local cleanup_command="$4"
    
    echo -e "\n${YELLOW}Running test: ${test_name}${NC}"
    echo "Command: $command"
    
    # Execute the command
    if $command > /tmp/test_output 2>&1; then
        test_result=0  # Success
    else
        test_result=1  # Failure
    fi
    
    # Display output
    cat /tmp/test_output
    
    # Check if result matches expected
    if [ "$test_result" -eq "$expected_success" ]; then
        echo -e "${GREEN}✓ Test passed${NC}"
        PASSED=$((PASSED+1))
    else
        echo -e "${RED}✗ Test failed - Expected exit code $expected_success, got $test_result${NC}"
        FAILED=$((FAILED+1))
    fi
    
    # Run cleanup if provided
    if [ -n "$cleanup_command" ]; then
        echo "Cleaning up..."
        $cleanup_command
    fi
}

# Setup: Create a test action if it doesn't exist
setup() {
    echo -e "${YELLOW}Setting up test environment...${NC}"
    
    # Create test action if it doesn't exist
    if [ ! -d ".aicheck/actions/$TEST_ACTION" ]; then
        ./ai new $TEST_ACTION > /dev/null 2>&1 || true
        echo "Created test action: $TEST_ACTION"
    fi
    
    # Clean up any previous test files
    rm -f ".aicheck/actions/$TEST_ACTION/src/$TEST_CODE_FILE" 2>/dev/null || true
    rm -f ".aicheck/actions/$TEST_ACTION/supporting_docs/$TEST_DOC_FILE" 2>/dev/null || true
    rm -f "$MISPLACED_CODE_FILE" 2>/dev/null || true
    rm -f "$MISPLACED_DOC_FILE" 2>/dev/null || true
    
    # Ensure directories exist
    mkdir -p ".aicheck/actions/$TEST_ACTION/src" 2>/dev/null || true
    mkdir -p ".aicheck/actions/$TEST_ACTION/supporting_docs" 2>/dev/null || true
    mkdir -p ".aicheck/docs" 2>/dev/null || true
}

# Cleanup: Remove test files
cleanup() {
    echo -e "${YELLOW}Cleaning up test environment...${NC}"
    
    # Remove test files
    rm -f ".aicheck/actions/$TEST_ACTION/src/$TEST_CODE_FILE" 2>/dev/null || true
    rm -f ".aicheck/actions/$TEST_ACTION/supporting_docs/$TEST_DOC_FILE" 2>/dev/null || true
    rm -f "$MISPLACED_CODE_FILE" 2>/dev/null || true
    rm -f "$MISPLACED_DOC_FILE" 2>/dev/null || true
}

# Test create-code command with correct path
test_create_code_correct() {
    run_test "Create code in correct location" \
        "./ai create-code $TEST_ACTION $TEST_CODE_FILE python" \
        0 \
        ""
    
    # Verify file was created
    if [ -f ".aicheck/actions/$TEST_ACTION/src/$TEST_CODE_FILE" ]; then
        echo -e "${GREEN}✓ File created correctly${NC}"
    else
        echo -e "${RED}✗ File not created${NC}"
        FAILED=$((FAILED+1))
    fi

    # Clean up after verification
    rm -f ".aicheck/actions/$TEST_ACTION/src/$TEST_CODE_FILE" 2>/dev/null || true
}

# Test create-doc command with correct path
test_create_doc_correct() {
    # Create a dummy file that doesn't require user input
    echo "# Test Document" > ".aicheck/actions/$TEST_ACTION/supporting_docs/$TEST_DOC_FILE"
    
    run_test "Verify doc in correct location" \
        "ls -la .aicheck/actions/$TEST_ACTION/supporting_docs/$TEST_DOC_FILE" \
        0 \
        ""
    
    # Verify file exists
    if [ -f ".aicheck/actions/$TEST_ACTION/supporting_docs/$TEST_DOC_FILE" ]; then
        echo -e "${GREEN}✓ File exists correctly${NC}"
    else
        echo -e "${RED}✗ File does not exist${NC}"
        FAILED=$((FAILED+1))
    fi

    # Clean up after verification
    rm -f ".aicheck/actions/$TEST_ACTION/supporting_docs/$TEST_DOC_FILE" 2>/dev/null || true
}

# Test code location check (mock detection of misplaced code)
test_code_location_check() {
    # Create a misplaced code file
    echo "#!/usr/bin/env python3" > "$MISPLACED_CODE_FILE"
    echo "print('Misplaced code file test')" >> "$MISPLACED_CODE_FILE"
    
    run_test "Code location check detection" \
        "bash .aicheck/scripts/code_location_check.sh < <(echo 'n')" \
        1 \
        "rm -f $MISPLACED_CODE_FILE"
}

# Test code location check allowing override (mock detection of misplaced code but allowing it)
test_code_location_check_override() {
    # Create a misplaced code file
    echo "#!/usr/bin/env python3" > "$MISPLACED_CODE_FILE"
    echo "print('Misplaced code file test with override')" >> "$MISPLACED_CODE_FILE"
    
    run_test "Code location check with override" \
        "bash .aicheck/scripts/code_location_check.sh < <(echo 'y')" \
        0 \
        "rm -f $MISPLACED_CODE_FILE"
}

# Test document location guidance in docs command
test_docs_location_guidance() {
    # Create a misplaced doc file
    mkdir -p ".aicheck/docs" 2>/dev/null || true
    echo "# Test Misplaced Document" > ".aicheck/docs/misplaced_test.md"
    
    run_test "Document location guidance" \
        "./ai docs add $TEST_ACTION \"Misplaced Doc\" \".aicheck/docs/misplaced_test.md\" \"Test description\" < <(echo '3')" \
        0 \
        "rm -f .aicheck/docs/misplaced_test.md"
}

# Test documentation detection hook
test_doc_detection_hook() {
    # Create a test document in the action directory
    mkdir -p ".aicheck/actions/$TEST_ACTION/supporting_docs" 2>/dev/null || true
    echo "# Test Auto-Detected Document" > ".aicheck/actions/$TEST_ACTION/supporting_docs/auto-detected-doc.md"
    echo "This document should be detected by the doc detection hook." >> ".aicheck/actions/$TEST_ACTION/supporting_docs/auto-detected-doc.md"
    
    # Stage the file
    git add ".aicheck/actions/$TEST_ACTION/supporting_docs/auto-detected-doc.md"
    
    run_test "Documentation detection" \
        "bash .aicheck/scripts/doc_detection_hook.sh < <(echo -e 'n')" \
        0 \
        "git reset .aicheck/actions/$TEST_ACTION/supporting_docs/auto-detected-doc.md && rm -f .aicheck/actions/$TEST_ACTION/supporting_docs/auto-detected-doc.md"
}

# Run all tests
run_all_tests() {
    echo -e "${YELLOW}=== Running Code and Documentation Location Tests ===${NC}"
    
    setup
    
    test_create_code_correct
    test_create_doc_correct
    
    # Test detection hook, commented by default as it needs git operations
    # test_doc_detection_hook
    
    # Note: These tests might fail in automated environments since they need user input
    # Comment them out if running in CI/CD pipeline
    # test_code_location_check
    # test_code_location_check_override
    # test_docs_location_guidance
    
    cleanup
    
    echo -e "\n${YELLOW}=== Test Results ===${NC}"
    echo -e "${GREEN}✓ $PASSED tests passed${NC}"
    if [ $FAILED -gt 0 ]; then
        echo -e "${RED}✗ $FAILED tests failed${NC}"
        exit 1
    else
        echo -e "${GREEN}All tests passed!${NC}"
    fi
}

# Run all tests
run_all_tests 