# Operational Fix Action Plan

**Date**: 2025-05-28  
**Priority**: CRITICAL  
**Goal**: Make UltraAI system fully operational

## Emergency Actions (Do Immediately)

### 1. Fix Middleware Chain Issue
**Action**: Create emergency-middleware-fix action
```bash
./aicheck action new emergency-middleware-fix
```
**Steps**:
- Diagnose exact middleware causing "No response returned" 
- Remove or fix problematic async streaming middleware
- Test all endpoints work locally
- Deploy and verify in production

### 2. Fix Frontend API Configuration  
**Action**: Update frontend to use correct backend URL
**Steps**:
- Edit frontend/vercel.json to use https://ultrai-core.onrender.com
- Update frontend/.env.production if exists
- Redeploy frontend on Vercel
- Test frontend-backend connectivity

### 3. Re-enable Security Properly
**Action**: Fix CSP instead of disabling it
**Steps**:
- Identify what CSP was blocking
- Configure proper CSP policy that allows required resources
- Re-enable CSP in backend/config_security.py
- Test in production

### 4. Create Deployment Configuration
**Action**: Add render.yaml to project root
**Steps**:
- Create render.yaml based on current Render dashboard settings
- Include all environment variables
- Add health check configuration
- Commit and push to trigger deployment

## High Priority Actions (This Week)

### 5. Enable Demo Orchestrator Access
**Action**: Complete orchestrator-authentication-setup
**Steps**:
- Implement demo mode in authentication
- Add public demo endpoints
- Create demo user with limited permissions
- Deploy and test access

### 6. Fix Critical Security Vulnerabilities
**Action**: Complete security-vulnerability-fix
**Steps**:
- Run npm audit fix in frontend
- Update Python dependencies in backend
- Test all functionality still works
- Deploy updates

### 7. Clean Up App Structure
**Action**: Create app-structure-cleanup action
**Steps**:
- Archive /src directory (old MVP code)
- Consolidate to single app entry point
- Update all imports and references
- Test thoroughly

### 8. Production Validation
**Action**: Complete production-validation-tests
**Steps**:
- Create comprehensive test suite
- Test all endpoints in production
- Verify frontend-backend integration
- Document any issues found

## Implementation Order

1. **Day 1 (Today)**:
   - [ ] Fix middleware issue (2-4 hours)
   - [ ] Fix frontend API URL (30 minutes)
   - [ ] Re-enable security (1-2 hours)
   - [ ] Create render.yaml (1 hour)

2. **Day 2**:
   - [ ] Deploy all fixes
   - [ ] Run production validation tests
   - [ ] Start demo authentication setup

3. **Day 3-5**:
   - [ ] Complete demo access
   - [ ] Fix security vulnerabilities
   - [ ] Clean up app structure
   - [ ] Full system validation

## Success Metrics

- [ ] All API endpoints return proper responses (not 404 or middleware errors)
- [ ] Frontend successfully connects to backend
- [ ] Users can access demo orchestrator features
- [ ] No critical security vulnerabilities
- [ ] Clean, single app entry point
- [ ] All tests pass in production

## Rollback Plan

If fixes cause new issues:
1. Revert to commit f542e98f (last attempted fix)
2. Deploy minimal working version without middleware
3. Add features back incrementally
4. Test each addition thoroughly

## Long-term Improvements

After system is operational:
- Implement proper monitoring and alerting
- Add automated deployment tests
- Create staging environment
- Implement log rotation
- Add performance monitoring
- Create user documentation

## Action Commands

```bash
# Start emergency fix
./aicheck action new emergency-middleware-fix
./aicheck action set emergency-middleware-fix

# Document dependencies
./aicheck dependency add starlette 0.37.2 "Core middleware framework - has streaming issues"
./aicheck dependency add fastapi 0.111.0 "Backend API framework"

# After middleware fix
./aicheck action complete emergency-middleware-fix

# Continue with other fixes...
```

## Notes

- Prioritize getting basic functionality working over perfect implementation
- Test each fix in isolation before combining
- Document all changes for team awareness
- Keep fixes minimal and focused
- Verify each fix in production before moving to next