# Render Configuration Tasks for Other AI (Assigned: Claude Code)

## Your Tasks:

### 1. Update Backend Configurations
Remove the frontend build steps from the backend services since we now have separate frontend services.

**In `render-staging.yaml`:**
- Change line 10-11 from:
  ```yaml
  buildCommand: |
    pip install -r requirements-production.txt
    cd frontend && npm ci && npm run build && cd ..
  ```
  To:
  ```yaml
  buildCommand: pip install -r requirements-production.txt
  ```

**In `render-production.yaml`:**
- Change line 9-11 from:
  ```yaml
  buildCommand: |
    pip install -r requirements-production.txt
    cd frontend && npm ci && npm run build && cd ..
  ```
  To:
  ```yaml
  buildCommand: pip install -r requirements-production.txt
  ```

### 2. Create Verification Script
Create the file `scripts/verify-render-config.sh` with the content from the existing script (lines 1-88 from the file we found earlier). Make sure to:
- Create the `scripts` directory first
- Make the script executable with `chmod +x scripts/verify-render-config.sh`

### 3. Handle render.yaml
This file appears to be outdated and doesn't match our current architecture. You should either:
- **Option A**: Delete it entirely (recommended if it's not being used)
- **Option B**: Update it to be a proper development configuration

For Option B, it should be renamed to something like `render-development.yaml` and updated to:
- Use `pip install -r requirements-production.txt` instead of Poetry
- Remove the frontend build steps
- Update service name to something like `ultrai-dev-api`
- Set appropriate development environment variables

## What I've Already Done:
1. ✅ Created 3 frontend service configurations:
   - `render-frontend-staging.yaml` - for staging-ultrai.onrender.com
   - `render-frontend-production.yaml` - for ultrai.com
   - `render-frontend-demo.yaml` - for demo-ultrai.onrender.com

2. ✅ Updated CORS settings in:
   - `render-staging.yaml` - Added frontend URLs
   - `render-production.yaml` - Added all production frontend domains

## Additional Notes:
- The frontend services are now configured as static sites that will be built and deployed separately
- Each frontend service has appropriate environment variables for Vite
- The backend services should no longer build or serve frontend files
- Make sure to test the verification script after creating it