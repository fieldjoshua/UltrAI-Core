# Git Branch Reconciliation Plan

## Current State
- **Render deploys from**: `main` branch  
- **Current work on**: `production` branch (61 commits ahead)
- **Problem**: Nice UI improvements in production not being deployed

## The Smart Fix

### Step 1: Clean Working Directory
```bash
git stash  # Save local changes
git checkout production
```

### Step 2: Create Clean Branch from Production
Since production has the UI improvements we want:
```bash
git checkout -b unified-main
```

### Step 3: Cherry-pick Critical Fixes from Main
Instead of merging everything (which causes conflicts), we'll cherry-pick only the critical fixes from main:
```bash
# Get critical API/security fixes from main
git cherry-pick 3869035c  # enforce minimum 2 models requirement
git cherry-pick 071f8547  # fallback handling for missing API keys
git cherry-pick 788060a5  # model availability detection
```

### Step 4: Force Update Main
Once we have a clean unified branch:
```bash
git checkout main
git reset --hard unified-main
git push --force-with-lease origin main
```

### Step 5: Clean Up
```bash
git branch -D production  # Delete local production
git push origin --delete production  # Delete remote production
```

## Benefits of This Approach
1. Keeps all the UI improvements from production
2. Adds only the critical fixes from main
3. Avoids messy merge conflicts
4. Creates a single source of truth
5. Render will automatically deploy the updated main

## Alternative: If Force Push is Too Risky
Create a PR instead:
```bash
git checkout unified-main
git push -u origin unified-main
# Create PR from unified-main to main on GitHub
# Review and merge
```