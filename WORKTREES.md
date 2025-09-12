# Git Worktrees for Parallel Development

This project uses Git worktrees to enable parallel development on different features and test suites without constantly switching branches. Each worktree represents an independent, deployable feature.

## Active Worktrees

### Core Development
1. **Main Repository**
   - Path: `/Users/joshuafield/Documents/Ultra`
   - Branch: `chore/config-auth-consolidation`
   - Purpose: Main development and configuration work
   - Status: Active development
   - Owner: Primary development

### Testing Enhancements
2. **Unit Tests Enhancement**
   - Path: `/Users/joshuafield/Documents/Ultra-worktrees/test-unit-enhancement`
   - Branch: `test/unit-enhancement`
   - Purpose: Enhance unit test coverage and quality
   - Status: In progress
   - Focus: Service layer unit tests

3. **Integration Tests Enhancement**
   - Path: `/Users/joshuafield/Documents/Ultra-worktrees/test-integration-enhancement`
   - Branch: `test/integration-enhancement`
   - Purpose: Improve integration testing between services
   - Status: In progress
   - Focus: Service interaction testing

4. **E2E Tests Enhancement**
   - Path: `/Users/joshuafield/Documents/Ultra-worktrees/test-e2e-enhancement`
   - Branch: `test/e2e-enhancement`
   - Purpose: Enhance end-to-end test scenarios
   - Status: In progress
   - Focus: User flow testing

5. **Live & Performance Tests**
   - Path: `/Users/joshuafield/Documents/Ultra-worktrees/test-live-performance`
   - Branch: `test/live-performance`
   - Purpose: Live API testing and performance benchmarking
   - Status: Not created yet
   - Focus: Real provider testing, load testing, performance metrics
   - Ownership: `tests/live/`, performance benchmarks
   - Key Tasks:
     - Implement live provider tests
     - Create performance benchmarks
     - Add load testing scenarios
     - Monitor API response times
     - Test rate limiting behavior

### Feature Development (Planned)
6. **UX/UI Improvements**
   - Path: `/Users/joshuafield/Documents/Ultra-worktrees/ux-ui-improvements`
   - Branch: `feature/ux-ui-improvements`
   - Purpose: Frontend enhancements and theme consolidation
   - Status: Not created yet
   - Ownership: `frontend/src/components/`, `frontend/src/styles/`
   - Key Tasks:
     - Consolidate AnimatedLogo versions (V1, V2, V3)
     - Enhance OrchestratorInterface component
     - Improve theme consistency
     - Mobile responsiveness

7. **Billing & Pricing System**
   - Path: `/Users/joshuafield/Documents/Ultra-worktrees/billing-system`
   - Branch: `feature/billing-pricing`
   - Purpose: Implement billing, budgeting, and pricing features
   - Status: Not created yet
   - Ownership: `app/services/billing_*.py`, `app/services/pricing_*.py`, `app/routes/billing.py`
   - Key Tasks:
     - Implement billing_service.py
     - Create budget_service.py
     - Develop pricing_service.py
     - Usage tracking and analytics

8. **Service Interfaces**
   - Path: `/Users/joshuafield/Documents/Ultra-worktrees/service-interfaces`
   - Branch: `feature/service-interfaces`
   - Purpose: Create service abstractions and interfaces
   - Status: Not created yet
   - Ownership: `app/services/interfaces/`
   - Key Tasks:
     - Define service contracts
     - Create abstract base classes
     - Implement dependency injection

9. **Documentation Updates**
   - Path: `/Users/joshuafield/Documents/Ultra-worktrees/documentation`
   - Branch: `docs/comprehensive-docs`
   - Purpose: Comprehensive documentation updates
   - Status: Not created yet
   - Ownership: `docs/`, `*.md` files
   - Key Tasks:
     - Update TestMatrix.md
     - Create PRICING_INTEGRATION.md
     - Enhance API documentation

10. **CI/CD Pipeline**
    - Path: `/Users/joshuafield/Documents/Ultra-worktrees/ci-cd`
    - Branch: `chore/github-actions`
    - Purpose: GitHub Actions and automation
    - Status: Not created yet
    - Ownership: `.github/workflows/`, `scripts/`
    - Key Tasks:
      - Implement .github/workflows/tests.yml
      - Create test automation scripts
      - Setup deployment pipelines

11. **Recovery System Enhancement**
    - Path: `/Users/joshuafield/Documents/Ultra-worktrees/recovery-system`
    - Branch: `feature/recovery-strategies`
    - Purpose: Enhance error recovery and resilience
    - Status: Not created yet
    - Ownership: `app/services/recovery_*.py`, `app/utils/recovery_*.py`
    - Key Tasks:
      - Enhance recovery_service.py
      - Implement recovery_strategies.py
      - Add circuit breakers

12. **Performance Optimization** (Optional)
    - Path: `/Users/joshuafield/Documents/Ultra-worktrees/performance-optimization`
    - Branch: `feature/performance-optimization`
    - Purpose: Frontend and backend performance improvements
    - Status: Not created yet
    - Key Tasks:
      - Frontend bundle optimization
      - React render optimization
      - Backend response time improvements
      - Caching enhancements

## Working with Worktrees

### Switching Between Worktrees
```bash
# Navigate to unit tests worktree
cd ../Ultra-worktrees/test-unit-enhancement

# Navigate to integration tests worktree
cd ../Ultra-worktrees/test-integration-enhancement

# Navigate to e2e tests worktree
cd ../Ultra-worktrees/test-e2e-enhancement

# Return to main repository
cd /Users/joshuafield/Documents/Ultra
```

### Common Commands
```bash
# List all worktrees
git worktree list

# Remove a worktree (after merging branch)
git worktree remove ../Ultra-worktrees/test-unit-enhancement

# Add a new worktree
git worktree add ../Ultra-worktrees/new-feature -b feature/new-feature

# Add the 4th test worktree
git worktree add ../Ultra-worktrees/test-live-performance -b test/live-performance
```

### Best Practices
1. Each worktree is independent - changes in one don't affect others until merged
2. Run `poetry install` or `make setup` in each worktree after creation
3. Keep worktrees focused on their specific test domain
4. Merge changes back to main branch when enhancements are complete

### Workflow Example
1. Make unit test changes in the unit enhancement worktree
2. Run tests locally: `pytest tests/unit/ -v`
3. Commit changes in that worktree
4. Switch to main repo and merge when ready

## Worktree Status Tracking

### Status Check Script
Create `scripts/check-worktree-status.sh`:
```bash
#!/bin/bash
echo "=== Worktree Status Overview ==="
echo "Generated: $(date)"
echo ""

for worktree in $(git worktree list --porcelain | grep "worktree" | cut -d' ' -f2); do
    echo "📁 $worktree"
    cd "$worktree" 2>/dev/null || continue
    
    branch=$(git branch --show-current)
    echo "  Branch: $branch"
    echo "  Last commit: $(git log -1 --oneline 2>/dev/null || echo 'No commits')"
    
    # Count uncommitted changes
    changes=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    echo "  Uncommitted changes: $changes"
    
    # Check ahead/behind main
    if git rev-parse --verify origin/main >/dev/null 2>&1; then
        ahead_behind=$(git rev-list --left-right --count origin/main...$branch 2>/dev/null || echo "0	0")
        ahead=$(echo $ahead_behind | cut -f2)
        behind=$(echo $ahead_behind | cut -f1)
        echo "  Status: $ahead ahead, $behind behind main"
    fi
    
    # Check for STATUS.md
    if [ -f "STATUS.md" ]; then
        echo "  Feature Status: $(grep -m1 "Status:" STATUS.md | cut -d: -f2- | tr -d ' ')"
    fi
    echo ""
done
```

### Feature Status Template
Each worktree should maintain a `STATUS.md`:
```markdown
# Feature: [Feature Name]
Status: [0-100]% Complete
Ready for Deploy: [Yes/No]
Target Release: [v1.x.x or Date]

## Progress
- [ ] Task 1
- [x] Task 2 (completed)
- [ ] Task 3

## Blockers
- Waiting on [dependency]
- Need review from [team/person]

## Testing
- Unit Tests: [Pass/Fail/Not Started]
- Integration Tests: [Pass/Fail/Not Started]
- E2E Tests: [Pass/Fail/Not Started]

## Dependencies
- Requires: [other worktree features]
- Blocks: [dependent features]

## Deployment Impact
- New APIs: [Yes/No - list them]
- Breaking Changes: [Yes/No - describe]
- Feature Flags: [Required flags]
```

## Deployment Strategy

### Feature-Specific Deployments

1. **Independent Feature Deployment**
   Each worktree can be deployed independently when ready:
   ```bash
   # From feature worktree
   git push origin feature/billing-pricing
   gh pr create --base main --title "Deploy: Billing System"
   ```

2. **Deployment Order & Dependencies**
   ```mermaid
   graph TD
       A[Service Interfaces] --> B[Billing System]
       A --> C[Recovery System]
       B --> D[UX/UI Improvements]
       C --> D
       D --> E[Performance Optimization]
   ```

3. **Feature Flags Configuration**
   ```python
   # app/config.py
   FEATURE_FLAGS = {
       "billing_enabled": os.getenv("ENABLE_BILLING", "false") == "true",
       "new_ui": os.getenv("ENABLE_NEW_UI", "false") == "true",
       "advanced_recovery": os.getenv("ENABLE_RECOVERY", "false") == "true",
       "service_interfaces": os.getenv("ENABLE_INTERFACES", "false") == "true",
   }
   ```

4. **Rollout Strategy**
   - **Phase 1**: Core infrastructure (service interfaces, CI/CD)
   - **Phase 2**: Backend features (billing, recovery)
   - **Phase 3**: Frontend improvements (UI/UX)
   - **Phase 4**: Optimizations (performance, caching)

### Deployment Checklist
Before deploying any worktree feature:
- [ ] All tests pass in worktree
- [ ] Feature flag configured if needed
- [ ] Documentation updated
- [ ] Dependencies deployed first
- [ ] STATUS.md shows "Ready for Deploy: Yes"
- [ ] No breaking changes without coordination
- [ ] Performance impact assessed

## AI Editor Assignment Guidelines

### Recommended Assignments
- **Claude**: UX/UI Improvements, Documentation
- **GPT**: Billing System, Service Interfaces
- **Cursor**: CI/CD Pipeline, Performance Optimization
- **Other AI**: Recovery System, Testing Enhancements
- **Specialized**: Live & Performance Tests (requires real API keys)

### Handoff Protocol
1. Complete current task and commit
2. Update STATUS.md with progress
3. Push changes to origin
4. Document any blockers or decisions
5. Specify next steps clearly

### Cross-Worktree Communication
- Use mock interfaces when dependent features aren't deployed
- Document API contracts in shared `docs/api/` directory
- Regular sync meetings (daily standups) to coordinate
- Check other worktrees' STATUS.md before starting work