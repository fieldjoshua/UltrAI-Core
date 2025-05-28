#!/bin/bash
# Test suite for migration tools
# Validates migration of existing actions to hybrid format

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test environment
TEST_DIR="/tmp/aicheck-migration-test-$$"
ORIGINAL_DIR=$(pwd)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source migration tools
source "${SCRIPT_DIR}/migration-tools.sh"

# Test counters
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
    mkdir -p "$TEST_DIR/.aicheck/actions"
    cd "$TEST_DIR"
    export AICHECK_DIR="$TEST_DIR/.aicheck"
}

cleanup_test_environment() {
    cd "$ORIGINAL_DIR"
    rm -rf "$TEST_DIR"
}

create_traditional_action() {
    local action_name="$1"
    local action_dir="$AICHECK_DIR/actions/$action_name"
    
    mkdir -p "$action_dir/supporting_docs"
    
    # Create traditional files
    echo "pending" > "$action_dir/status"
    echo "$action_name" > "$action_dir/current_action"
    
    # Create plan file
    cat > "$action_dir/$action_name-plan.md" << EOF
# $action_name Plan

## Objective
This is a test action for migration testing. It demonstrates the traditional
action structure that needs to be migrated to the hybrid format.

## Phases

### Phase 1: Planning
- Design the solution
- Create documentation

### Phase 2: Implementation
- Write the code
- Test the implementation

## Success Criteria
- All tests pass
- Documentation complete
EOF
    
    # Create dependencies file
    cat > "$action_dir/dependencies" << EOF
external: pytest==7.0.0 (Testing framework)
external: requests==2.28.0 (HTTP library)
internal: prerequisite-action (data: Provides configuration data)
EOF
    
    # Create todo.md
    cat > "$action_dir/todo.md" << EOF
# Todo List for $action_name

- [ ] Design the solution
- [ ] Write tests
- [ ] Implement features
- [ ] Update documentation
EOF
    
    # Create some supporting docs
    echo "# README" > "$action_dir/supporting_docs/README.md"
    echo "#!/bin/bash" > "$action_dir/supporting_docs/test.sh"
}

# Test: Basic migration
test_basic_migration() {
    local action_name="test-basic-migration"
    
    # Create traditional action
    create_traditional_action "$action_name"
    
    # Run migration
    migrate_action "$action_name" >/dev/null 2>&1
    
    # Check YAML exists
    [[ -f "$AICHECK_DIR/actions/$action_name/action.yaml" ]] || return 1
    
    # Verify basic fields
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    grep -q "name: $action_name" "$yaml_file" || return 1
    grep -q "status: pending" "$yaml_file" || return 1
    grep -q "migrated: true" "$yaml_file" || return 1
}

# Test: Description extraction
test_description_extraction() {
    local action_name="test-desc-extraction"
    
    create_traditional_action "$action_name"
    migrate_action "$action_name" >/dev/null 2>&1
    
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    
    # Check description was extracted
    grep -q "test action for migration testing" "$yaml_file" || return 1
    grep -q "demonstrates the traditional" "$yaml_file" || return 1
}

# Test: Phase extraction
test_phase_extraction() {
    local action_name="test-phase-extraction"
    
    create_traditional_action "$action_name"
    migrate_action "$action_name" >/dev/null 2>&1
    
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    
    # Check phases were extracted
    grep -q "Phase 1: Planning" "$yaml_file" || return 1
    grep -q "Phase 2: Implementation" "$yaml_file" || return 1
}

# Test: Dependency migration
test_dependency_migration() {
    local action_name="test-dep-migration"
    
    create_traditional_action "$action_name"
    migrate_action "$action_name" >/dev/null 2>&1
    
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    
    # Check TODO comments for manual dependency adjustment
    grep -q "pytest" "$yaml_file" || return 1
    grep -q "requests" "$yaml_file" || return 1
    grep -q "prerequisite-action" "$yaml_file" || return 1
}

# Test: Supporting docs cataloging
test_supporting_docs_catalog() {
    local action_name="test-docs-catalog"
    
    create_traditional_action "$action_name"
    migrate_action "$action_name" >/dev/null 2>&1
    
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    
    # Check supporting docs were cataloged
    grep -q "supporting_docs:" "$yaml_file" || return 1
    grep -q "README.md" "$yaml_file" || return 1
    grep -q "test.sh" "$yaml_file" || return 1
}

# Test: Todo reference
test_todo_reference() {
    local action_name="test-todo-ref"
    
    create_traditional_action "$action_name"
    migrate_action "$action_name" >/dev/null 2>&1
    
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    
    # Check todo reference was added
    grep -q "todos:" "$yaml_file" || return 1
    grep -q "source: \"todo.md\"" "$yaml_file" || return 1
    grep -q "TodoRead/TodoWrite" "$yaml_file" || return 1
}

# Test: Validation after migration
test_migration_validation() {
    local action_name="test-validation"
    
    create_traditional_action "$action_name"
    migrate_action "$action_name" >/dev/null 2>&1
    
    # Run validation
    validate_migration "$action_name" >/dev/null 2>&1 || return 1
}

# Test: Skip existing migration
test_skip_existing_migration() {
    local action_name="test-skip-existing"
    
    create_traditional_action "$action_name"
    
    # First migration
    migrate_action "$action_name" >/dev/null 2>&1
    
    # Try to migrate again - should skip
    local output=$(migrate_action "$action_name" 2>&1)
    echo "$output" | grep -q "already exists" || return 1
}

# Test: Rollback functionality
test_rollback() {
    local action_name="test-rollback"
    
    create_traditional_action "$action_name"
    migrate_action "$action_name" >/dev/null 2>&1
    
    # Verify YAML exists
    [[ -f "$AICHECK_DIR/actions/$action_name/action.yaml" ]] || return 1
    
    # Rollback
    rollback_migration "$action_name" >/dev/null 2>&1
    
    # Verify YAML removed
    [[ ! -f "$AICHECK_DIR/actions/$action_name/action.yaml" ]] || return 1
    
    # Traditional files should still exist
    [[ -f "$AICHECK_DIR/actions/$action_name/status" ]] || return 1
}

# Test: Batch migration
test_batch_migration() {
    # Create multiple traditional actions
    for i in {1..3}; do
        create_traditional_action "test-batch-$i"
    done
    
    # Run batch migration
    local output=$(migrate_all_actions 2>&1)
    
    # Check all were migrated
    for i in {1..3}; do
        [[ -f "$AICHECK_DIR/actions/test-batch-$i/action.yaml" ]] || return 1
    done
    
    # Check summary
    echo "$output" | grep -q "3 actions migrated successfully" || return 1
}

# Test: Deployment detection
test_deployment_detection() {
    local action_name="test-deployment-action"
    
    create_traditional_action "$action_name"
    migrate_action "$action_name" >/dev/null 2>&1
    
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    
    # Should detect deployment requirement from name
    grep -q "required: true" "$yaml_file" || return 1
}

# Test: Status preservation
test_status_preservation() {
    local action_name="test-status-preserve"
    
    create_traditional_action "$action_name"
    
    # Change status
    echo "in_progress" > "$AICHECK_DIR/actions/$action_name/status"
    
    migrate_action "$action_name" >/dev/null 2>&1
    
    local yaml_file="$AICHECK_DIR/actions/$action_name/action.yaml"
    
    # Check status was preserved
    grep -q "status: in_progress" "$yaml_file" || return 1
}

# Main test runner
main() {
    echo -e "${BLUE}AICheck Migration Test Suite${NC}"
    echo "============================"
    echo ""
    
    # Setup
    setup_test_environment
    
    # Run tests
    run_test "Basic migration" test_basic_migration
    run_test "Description extraction" test_description_extraction
    run_test "Phase extraction" test_phase_extraction
    run_test "Dependency migration" test_dependency_migration
    run_test "Supporting docs catalog" test_supporting_docs_catalog
    run_test "Todo reference" test_todo_reference
    run_test "Migration validation" test_migration_validation
    run_test "Skip existing migration" test_skip_existing_migration
    run_test "Rollback functionality" test_rollback
    run_test "Batch migration" test_batch_migration
    run_test "Deployment detection" test_deployment_detection
    run_test "Status preservation" test_status_preservation
    
    # Cleanup
    cleanup_test_environment
    
    # Summary
    echo "============================"
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