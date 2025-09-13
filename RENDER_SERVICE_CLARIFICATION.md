# Render Service Clarification

## Current Situation

Based on investigation, you appear to have multiple Render services:

### Active Services:
1. **ultrai-core.onrender.com** 
   - Status: Active (degraded - needs API keys)
   - Environment: production
   - This is your MAIN service

2. **ultrai-prod-api.onrender.com**
   - Status: Active (degraded - needs API keys)
   - Environment: production
   - Appears to be another production instance

3. **ultrai-staging-api.onrender.com**
   - Status: Down (502 error)
   - This might be the "staging" service you mentioned

### Why "Only Staging is Deploying"?

The confusion might be because:

1. **Multiple Services**: You have multiple Render services, and commits to `main` might only trigger deployment to one of them.

2. **Branch Configuration**: The staging service might be configured to deploy from `main`, while production requires manual promotion.

3. **Service Names**: The CSP headers reference both staging and prod APIs, suggesting a multi-environment setup.

## What You Need to Check:

### 1. In Render Dashboard:
- Go to each service (ultrai-core, ultrai-staging-api, ultrai-prod-api)
- Check the "Settings" tab
- Look for "Build & Deploy" section
- See which branch each service is watching

### 2. Typical Setups:
- **Staging**: Watches `main` branch (auto-deploys on push)
- **Production**: Watches `production` branch OR requires manual promotion

### 3. To Fix:

If you want `ultrai-core` to be your main production service:

```bash
# Option 1: Configure ultrai-core to watch main branch
# In Render dashboard for ultrai-core:
# Settings > Build & Deploy > Branch: main

# Option 2: Push to the branch that ultrai-core watches
git push origin main:production  # If it watches production branch
```

## Recommended Action:

1. **Check Render Dashboard** for each service's branch configuration
2. **Decide on deployment strategy**:
   - Single service (ultrai-core) watching main
   - Multiple services (staging/prod) watching different branches
3. **Update service configurations** accordingly

## Current Code Status:
- ✅ Branches reconciled (production → main)
- ✅ Financial services disabled
- ✅ Core services verified
- ❓ Deployment target unclear

Once you clarify which Render service should receive deployments from `main`, we can ensure your changes deploy correctly.