#!/bin/bash
# Test suite for enhanced AICheck commands
# Tests new functionality while ensuring backward compatibility

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test environment setup
TEST_DIR="/tmp/aicheck-test-$$"
ORIGINAL_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source the enhanced aicheck script
source "${SCRIPT_DIR}/aicheck-enhanced.sh"

# Test utilities
test_count=0
pass_count=0
fail_count=0

run_test() {
    local test_name="$1"
    local test_function="$2"
    
    ((test_count++))
    echo -e "${BLUE}Running test: ${test_name}${NC}"
    
    if $test_function; then
        ((pass_count++))
        echo -e "${GREEN}✓ PASS: ${test_name}${NC}"
    else
        ((fail_count++))
        echo -e "${RED}✗ FAIL: ${test_name}${NC}"
    fi
    echo ""
}

setup_test_environment() {
    # Create test directory structure
    mkdir -p "$TEST_DIR/.aicheck/actions"
    cd "$TEST_DIR"
    
    # Initialize git repo for git hook tests
    git init --quiet
    
    # Create minimal RULES.md
    cat > "$TEST_DIR/.aicheck/RULES.md" << 'EOF'
# AICheck Rules v3.1
Test rules file
EOF
    
    # Set AICHECK_DIR for tests
    export AICHECK_DIR="$TEST_DIR/.aicheck"
}

cleanup_test_environment() {
    cd "$ORIGINAL_DIR"
    rm -rf "$TEST_DIR"
}

# Test: Create new action with YAML
test_create_action_with_yaml() {
    local action_name="test-action-yaml"
    
    # Create action
    ./aicheck action new "$action_name" >/dev/null 2>&1
    
    # Check traditional files exist
    [[ -f "$AICHECK_DIR/actions/$action_name/status" ]] || return 1
    [[ -f "$AICHECK_DIR/actions/$action_name/$action_name-plan.md" ]] || return 1
    
    # Check YAML file exists
    [[ -f "$AICHECK_DIR/actions/$action_name/action.yaml" ]] || return 1
    
    # Verify YAML content
    grep -q "name: $action_name" "$AICHECK_DIR/actions/$action_name/action.yaml"
}

# Test: Backward compatibility - traditional commands still work
test_backward_compatibility() {
    local action_name="test-traditional"
    
    # Use traditional command
    ./aicheck action new "$action_name" >/dev/null 2>&1
    ./aicheck action set "$action_name" >/dev/null 2>&1
    
    # Check status file
    local status=$(cat "$AICHECK_DIR/current_action")
    [[ "$status" == "$action_name" ]] || return 1
    
    # Traditional complete should still work
    ./aicheck action complete >/dev/null 2>&1
    
    # Verify completion
    local action_status=$(cat "$AICHECK_DIR/actions/$action_name/status")
    [[ "$action_status" == "completed" ]] || return 1
}

# Test: Deployment verification blocks completion
test_deployment_verification_blocking() {
    local action_name="test-deployment-required"
    
    # Create action with deployment requirement
    ./aicheck action new "$action_name" >/dev/null 2>&1
    
    # Manually set deployment required in YAML
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    sed -i.bak 's/required: false/required: true/' "$yaml_file"
    
    # Add test command that fails
    cat >> "$yaml_file" << 'EOF'
  environments:
    production:
      url: https://example.com
      verified: false
      test_command: "false"  # This will always fail
EOF
    
    # Try to complete - should fail
    if ./aicheck action complete "$action_name" 2>/dev/null; then
        return 1  # Should have failed
    fi
    
    # Status should still be pending
    local status=$(cat "$AICHECK_DIR/actions/$action_name/status")
    [[ "$status" != "completed" ]] || return 1
    
    return 0
}

# Test: Issue tracking integration
test_issue_tracking() {
    local action_name="test-issues"
    
    # Create action
    ./aicheck action new "$action_name" >/dev/null 2>&1
    ./aicheck action set "$action_name" >/dev/null 2>&1
    
    # Report an issue
    ./aicheck issue report "Test issue" "critical" >/dev/null 2>&1
    
    # Try to complete - should fail due to critical issue
    if ./aicheck action complete 2>/dev/null; then
        return 1  # Should have failed
    fi
    
    # Update issue status
    ./aicheck issue update "ISS-001" "resolved" >/dev/null 2>&1
    
    # Now completion should work
    ./aicheck action complete >/dev/null 2>&1
    
    local status=$(cat "$AICHECK_DIR/actions/$action_name/status")
    [[ "$status" == "completed" ]] || return 1
}

# Test: Dependency management
test_dependency_management() {
    local action1="test-dep-1"
    local action2="test-dep-2"
    
    # Create two actions
    ./aicheck action new "$action1" >/dev/null 2>&1
    ./aicheck action new "$action2" >/dev/null 2>&1
    
    # Add dependency
    ./aicheck dependency internal "$action2" "$action1" "data" "Test dependency" >/dev/null 2>&1
    
    # Check dependency was recorded
    local yaml_file="$AICHECK_DIR/actions/$action2/action.yaml"
    grep -q "$action1" "$yaml_file" || return 1
    
    # Test circular dependency detection
    if ./aicheck dependency internal "$action1" "$action2" "data" "Circular" 2>/dev/null; then
        return 1  # Should have detected circular dependency
    fi
    
    return 0
}

# Test: YAML sync with traditional files
test_yaml_sync() {
    local action_name="test-sync"
    
    # Create action
    ./aicheck action new "$action_name" >/dev/null 2>&1
    
    # Change status via traditional method
    echo "in_progress" > "$AICHECK_DIR/actions/$action_name/status"
    
    # Sync should update YAML
    ./aicheck sync "$action_name" >/dev/null 2>&1
    
    # Check YAML was updated
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    grep -q "status: in_progress" "$yaml_file" || return 1
}

# Test: Status command shows enhanced info
test_enhanced_status() {
    local action_name="test-status"
    
    # Create action with some data
    ./aicheck action new "$action_name" >/dev/null 2>&1
    ./aicheck action set "$action_name" >/dev/null 2>&1
    
    # Add a dependency
    ./aicheck dependency add "pytest" "7.0.0" "Testing framework" >/dev/null 2>&1
    
    # Get status
    local status_output=$(./aicheck status 2>&1)
    
    # Should show current action
    echo "$status_output" | grep -q "$action_name" || return 1
    
    # Should show dependencies
    echo "$status_output" | grep -q "pytest" || return 1
}

# Test: Git hook integration
test_git_hooks() {
    local action_name="test-git-hooks"
    
    # Install git hooks
    "${SCRIPT_DIR}/git-hooks.sh" install >/dev/null 2>&1
    
    # Create and set action
    ./aicheck action new "$action_name" >/dev/null 2>&1
    ./aicheck action set "$action_name" >/dev/null 2>&1
    
    # Create a test file
    echo "test" > test.txt
    git add test.txt
    
    # Commit should work (no deployment required)
    git commit -m "Test commit" >/dev/null 2>&1 || return 1
    
    # Check commit was recorded in YAML
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    grep -q "Test commit" "$yaml_file" || return 1
}

# Test: List command shows YAML data
test_list_with_yaml() {
    # Create multiple actions
    ./aicheck action new "test-list-1" >/dev/null 2>&1
    ./aicheck action new "test-list-2" >/dev/null 2>&1
    
    # Set one as in progress
    echo "in_progress" > "$AICHECK_DIR/actions/test-list-2/status"
    
    # List should show both
    local list_output=$(./aicheck action list 2>&1)
    
    echo "$list_output" | grep -q "test-list-1" || return 1
    echo "$list_output" | grep -q "test-list-2" || return 1
    echo "$list_output" | grep -q "in_progress" || return 1
}

# Test: Verify deployment command
test_verify_deployment() {
    local action_name="test-verify-deploy"
    
    # Create action
    ./aicheck action new "$action_name" >/dev/null 2>&1
    
    # Add deployment config
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    cat >> "$yaml_file" << 'EOF'
deployment:
  required: true
  environments:
    production:
      url: https://example.com
      verified: false
      test_command: "true"  # This will always pass
EOF
    
    # Run verification
    ./aicheck verify deployment "$action_name" >/dev/null 2>&1
    
    # Check verification was recorded
    grep -q "verified: true" "$yaml_file" || return 1
}

# Main test runner
main() {
    echo -e "${BLUE}AICheck Enhanced Commands Test Suite${NC}"
    echo "====================================="
    echo ""
    
    # Setup
    setup_test_environment
    
    # Run tests
    run_test "Create action with YAML" test_create_action_with_yaml
    run_test "Backward compatibility" test_backward_compatibility
    run_test "Deployment verification blocking" test_deployment_verification_blocking
    run_test "Issue tracking integration" test_issue_tracking
    run_test "Dependency management" test_dependency_management
    run_test "YAML sync functionality" test_yaml_sync
    run_test "Enhanced status command" test_enhanced_status
    run_test "Git hooks integration" test_git_hooks
    run_test "List command with YAML" test_list_with_yaml
    run_test "Verify deployment command" test_verify_deployment
    
    # Cleanup
    cleanup_test_environment
    
    # Summary
    echo "====================================="
    echo -e "${BLUE}Test Summary${NC}"
    echo "Total tests: $test_count"
    echo -e "${GREEN}Passed: $pass_count${NC}"
    echo -e "${RED}Failed: $fail_count${NC}"
    echo ""
    
    if [[ $fail_count -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        return 1
    fi
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi