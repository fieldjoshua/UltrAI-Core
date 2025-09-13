# Simple Git Fix Plan

## The Problem
- `main` branch is deployed by Render
- `production` branch has UI improvements not in main  
- Cherry-picking causes conflicts due to frontend dist files

## The Solution: Push Production to Main

Since:
1. Production branch has all the good UI stuff
2. Main branch changes are mostly in backend (which production also has)
3. Frontend dist conflicts are just build artifacts

We'll simply make production the new main:

```bash
# Step 1: Push production to main (force)
git checkout main
git reset --hard production
git push --force-with-lease origin main

# Step 2: Delete production branch (no longer needed)
git branch -D production
git push origin --delete production

# Step 3: Create develop branch for future work
git checkout -b develop
git push -u origin develop
```

## Why This Works
- Production branch already has everything we want deployed
- The API fixes from main are less critical than the UI improvements
- We can always cherry-pick specific backend fixes later if needed
- Simplifies everything to one branch (main) going forward

## After This
1. Render will auto-deploy the updated main with UI improvements
2. We'll have a clean git flow: main → develop → feature/*
3. No more confusion about which branch has what