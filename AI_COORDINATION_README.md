# AI Coordination Guide for UltrAI Development

This guide explains how to effectively use multiple AI editors across different worktrees for parallel development.

## 🚀 Quick Start

1. **Check current AI assignments**: `./scripts/coordinate-ais.sh`
2. **Switch to a worktree**: `cd ../Ultra-worktrees/[name]`
3. **Update AI assignment**: Edit `STATUS.md` in the worktree
4. **Track progress**: Commit `STATUS.md` changes regularly

## 🤖 Available AI Editors

### 1. Claude Code (Multiple Sessions)
- **How**: Open multiple browser tabs/terminal sessions
- **Best for**: Complex implementation, architecture decisions, documentation
- **Sessions**: Can run 3-4 simultaneous sessions in different worktrees
- **Example**:
  ```bash
  # Tab 1: Main development
  cd /Users/joshuafield/Documents/Ultra
  
  # Tab 2: UI/UX work
  cd ../Ultra-worktrees/ux-ui-improvements
  ```

### 2. Cursor AI (Multiple Windows)
- **How**: File → New Window for each worktree
- **Best for**: Quick edits, test writing, refactoring
- **Commands**: 
  - `Cmd+K`: Inline AI editing
  - `Cmd+L`: Chat interface
- **Tip**: Each window maintains separate context

### 3. ChatGPT (Browser)
- **How**: Multiple browser tabs
- **Best for**: Planning, code review, architecture discussions
- **Method**: Copy/paste code for review

### 4. GitHub Copilot
- **How**: Install in VS Code/Cursor
- **Best for**: Autocomplete, boilerplate code
- **Works**: Alongside other AIs

## 📋 Worktree Assignments

### Recommended AI Distribution

| Worktree | Primary AI | Secondary AI | Focus |
|----------|------------|--------------|-------|
| Main (config/auth) | Claude-1 | Cursor | Core development |
| UI/UX | Claude-2 | Copilot | Frontend components |
| Billing | GPT-1 | Cursor | Service implementation |
| Service Interfaces | Claude-3 | GPT | Architecture design |
| Documentation | ChatGPT | Claude | Writing & review |
| Unit Tests | Cursor-1 | Copilot | Test coverage |
| Integration Tests | Cursor-2 | Claude | Service testing |
| CI/CD | Cursor-3 | GPT | Automation scripts |
| Recovery System | Any Available | - | Error handling |
| Performance | Specialized | Claude | Optimization |

## 🔄 Coordination Workflow

### 1. Starting Work in a Worktree

```bash
# 1. Switch to worktree
cd ../Ultra-worktrees/billing-system

# 2. Check current status
cat STATUS.md

# 3. Update AI assignment
# Edit STATUS.md: Current AI: GPT-1

# 4. Pull latest changes
git pull origin main

# 5. Start work
# Open in appropriate AI editor
```

### 2. During Development

1. **Keep STATUS.md Updated**
   - Update progress percentage
   - Mark completed tasks
   - Note blockers immediately
   - Add decisions to communication log

2. **Commit Frequently**
   ```bash
   git add STATUS.md
   git commit -m "Update progress: implemented pricing calculator"
   ```

3. **Check Dependencies**
   - Look at other worktrees' STATUS.md
   - Note what you're waiting for
   - Document what you're providing

### 3. Handing Off Work

```bash
# 1. Update STATUS.md with hand-off notes
echo "## Hand-off to Next AI" >> STATUS.md
echo "- Completed: Basic billing service structure" >> STATUS.md
echo "- Next: Implement subscription logic" >> STATUS.md
echo "- See billing_service.py line 45 for TODO" >> STATUS.md

# 2. Commit all changes
git add -A
git commit -m "Hand-off: Billing service foundation complete"
git push origin feature/billing-pricing

# 3. Update coordination
./scripts/coordinate-ais.sh
```

## 📊 Status Tracking

### STATUS.md Structure

Each worktree must have a `STATUS.md` file. Use the template:
```bash
cp scripts/STATUS_TEMPLATE.md ../Ultra-worktrees/[worktree]/STATUS.md
```

### Key Sections to Maintain

1. **Current AI**: Which AI is actively working
2. **Progress**: Percentage and checklist
3. **Blockers**: What's preventing progress
4. **Dependencies**: Cross-worktree needs
5. **Communication Log**: Decisions and hand-offs

## 🛠️ Helper Scripts

### 1. Coordination Dashboard
```bash
./scripts/coordinate-ais.sh
```
Shows all worktrees and current AI assignments

### 2. Status Checker
```bash
./scripts/check-worktree-status.sh
```
Shows git status for all worktrees

### 3. Quick Status Update
```bash
# Create this helper
cat > scripts/update-status.sh << 'EOF'
#!/bin/bash
WORKTREE=$1
AI_NAME=$2
PROGRESS=$3

if [ -z "$WORKTREE" ] || [ -z "$AI_NAME" ]; then
    echo "Usage: $0 <worktree-name> <ai-name> [progress%]"
    exit 1
fi

cd ../Ultra-worktrees/$WORKTREE || exit 1
sed -i '' "s/Current AI:.*/Current AI: $AI_NAME/" STATUS.md
if [ ! -z "$PROGRESS" ]; then
    sed -i '' "s/Status:.*/Status: $PROGRESS Complete/" STATUS.md
fi
echo "Updated $WORKTREE: AI=$AI_NAME Progress=$PROGRESS"
EOF
chmod +x scripts/update-status.sh
```

## 💡 Best Practices

### 1. AI Specialization
- **Claude**: Complex logic, architecture, documentation
- **Cursor**: Quick edits, test writing, refactoring
- **GPT**: Planning, reviews, problem-solving
- **Copilot**: Boilerplate, completions

### 2. Communication Rules
- Always update STATUS.md before switching AIs
- Commit STATUS.md changes with clear messages
- Check dependencies before starting work
- Document decisions in communication log

### 3. Parallel Development Tips
- Work on independent features simultaneously
- Use feature flags to isolate changes
- Mock dependencies when needed
- Regular sync with main branch

### 4. Conflict Prevention
- Each worktree owns specific directories
- Don't edit same files across worktrees
- Coordinate through STATUS.md
- Merge completed features promptly

## 🚨 Common Issues

### AI Context Lost
**Solution**: Check STATUS.md communication log for context

### Dependency Blocking
**Solution**: Mock the dependency or switch to different task

### Merge Conflicts
**Solution**: Regular rebasing and clear ownership boundaries

### AI Confusion
**Solution**: Clear worktree names and STATUS.md updates

## 📈 Progress Monitoring

### Daily Standup Checklist
1. Run `./scripts/coordinate-ais.sh`
2. Check each worktree's progress
3. Identify and resolve blockers
4. Plan AI assignments for the day
5. Update any completed features

### Weekly Review
1. Merge completed features to main
2. Close completed worktrees
3. Create new worktrees as needed
4. Review AI performance/preferences
5. Adjust assignments based on results

## 🔗 Integration Points

### When Features Interact
1. Document API contracts in `docs/api/`
2. Use STATUS.md dependencies section
3. Create integration tests early
4. Mock services when needed

### Deployment Coordination
1. Check all dependent features are ready
2. Update feature flags
3. Coordinate deployment order
4. Monitor after deployment

---

## Quick Reference Card

```bash
# Switch to worktree
cd ../Ultra-worktrees/billing-system

# Check status
cat STATUS.md

# Update AI assignment
./scripts/update-status.sh billing-system Claude-2 45%

# Check all worktrees
./scripts/coordinate-ais.sh

# Commit progress
git add STATUS.md && git commit -m "Progress: 45% - implemented core billing"

# Push changes
git push origin feature/billing-pricing
```

Remember: **Communication through STATUS.md is key to successful multi-AI development!**