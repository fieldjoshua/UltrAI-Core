# Git Workflow for UltrAI

## Branch Strategy

We use a simplified Git Flow with three types of branches:

### 1. **main** (Protected)
- Production-ready code only
- Deploys automatically to Render
- Requires PR review to merge
- Never commit directly

### 2. **develop**
- Integration branch for features
- Always branched from main
- Features merge here first
- Periodically merged to main via PR

### 3. **feature/** branches
- Individual feature development
- Branch from develop
- Merge back to develop via PR
- Delete after merge

## Workflow Commands

### Starting a New Feature
```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-new-feature
```

### Working on a Feature
```bash
# Make changes
git add .
git commit -m "feat: description of changes"
git push -u origin feature/my-new-feature
```

### Creating a Feature PR
```bash
gh pr create --base develop --title "feat: my new feature"
```

### Releasing to Production
```bash
git checkout develop
git pull origin develop
gh pr create --base main --title "release: version X.Y.Z"
```

## Important Rules

1. **Never force push to main** - It's protected
2. **Always create PRs** - Even for small changes
3. **Delete feature branches** - After merging to keep repo clean
4. **Update develop regularly** - Pull from main after releases
5. **Test before merging** - Run tests locally before creating PR

## Deployment

- **Automatic**: Push to main triggers Render deployment
- **Manual**: Use `make deploy` which commits and pushes
- **Verification**: Check https://ultrai-core.onrender.com/ after deploy

## Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `refactor/` - Code improvements
- `docs/` - Documentation updates
- `test/` - Test additions/improvements
- `chore/` - Maintenance tasks

## Example Flow

1. Create feature branch from develop
2. Make changes and commit
3. Push and create PR to develop
4. After review, merge to develop
5. When ready for release, PR from develop to main
6. Render auto-deploys from main

## Emergency Hotfixes

For critical production issues:
```bash
git checkout main
git pull origin main
git checkout -b hotfix/critical-issue
# Fix the issue
git push -u origin hotfix/critical-issue
gh pr create --base main --title "hotfix: critical issue"
```

## Keeping Branches in Sync

After releasing to main:
```bash
git checkout main
git pull origin main
git checkout develop
git merge main
git push origin develop
```