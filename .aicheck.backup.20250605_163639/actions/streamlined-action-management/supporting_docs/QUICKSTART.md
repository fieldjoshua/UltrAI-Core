# 🟣 AICheck Quickstart - The EASIEST Way

## One Command Setup

In your project directory, run:

```bash
curl -sL https://bit.ly/aicheck-quick | bash
```

That's it! You now have AICheck with deployment verification.

## Or Copy-Paste This

```bash
# Create AICheck in current directory
mkdir -p .aicheck && cat > .aicheck/aicheck << 'EOF'
#!/bin/bash
case "$1" in
  new) mkdir -p .aicheck/actions/$2; echo "✅ Created: $2";;
  status) echo "🟣 AICheck Ready";;
  *) echo "Commands: new, status";;
esac
EOF
chmod +x .aicheck/aicheck
alias aicheck='./.aicheck/aicheck'
echo "🟣 AICheck installed! Try: aicheck status"
```

## Even Simpler: Just Use Aliases

Add to your ~/.bashrc or ~/.zshrc:

```bash
# AICheck shortcuts
alias ai-new='mkdir -p .aicheck/actions/$1'
alias ai-status='ls .aicheck/actions 2>/dev/null || echo "No actions yet"'
alias ai-complete='echo "⚠️  Deployment verification required!"'
```

## The Point

Enhanced AICheck prevents marking things "complete" without deployment verification. Even this simple version reminds you!

## Full Version

For the complete system with all features:
- Deployment verification
- Issue tracking  
- Git integration
- YAML configuration

Install from: `.aicheck/actions/streamlined-action-management/supporting_docs/`

But honestly? Start simple. The core idea is:
**No marking complete without verifying deployment!** 🟣