# Render Environment Group Setup Guide

## Current Issue
Both staging and production are not loading environment variables properly.

## Fix via Render Dashboard

### 1. Check Environment Group Link
Go to each service and verify:
- **ultrai-staging-api** → Settings → Environment → Should show "Linked Environment Group"
- **ultrai-prod-api** → Settings → Environment → Should show "Linked Environment Group"

### 2. Required Variables in Environment Group

#### Backend Variables:
```
ENVIRONMENT=staging  # or 'production' for prod
PORT=10000
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api03-...
GOOGLE_API_KEY=AIzaSy...
HUGGINGFACE_API_KEY=hf_...
```

#### Frontend Build Variables (CRITICAL):
```
VITE_API_URL=https://ultrai-staging-api.onrender.com/api  # or prod URL
VITE_API_MODE=live
VITE_DEMO_MODE=false
```

### 3. Force Rebuild
After linking/updating environment group:
1. Go to each service
2. Click "Manual Deploy"
3. Select "Clear build cache & deploy"

### 4. Verify After Deploy
Check that environment is correct:
```bash
# Should show environment: "staging"
curl -s https://ultrai-staging-api.onrender.com/api/health | jq .environment

# Should show environment: "production"  
curl -s https://ultrai-prod-api.onrender.com/api/health | jq .environment
```

## If Using Separate Environment Groups

Create two groups:
1. **staging-env** - with ENVIRONMENT=staging
2. **production-env** - with ENVIRONMENT=production

Both should have all the API keys and appropriate VITE_API_URL values.