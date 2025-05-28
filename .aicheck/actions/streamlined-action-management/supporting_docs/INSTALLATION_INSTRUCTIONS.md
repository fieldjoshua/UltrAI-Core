# Enhanced AICheck Installation Instructions

## Quick Install (Recommended)

Run this single command from the project root:

```bash
curl -fsSL https://raw.githubusercontent.com/your-org/your-repo/main/.aicheck/actions/streamlined-action-management/supporting_docs/install.sh | bash
```

## Manual Installation

### Step 1: Download Enhanced AICheck

```bash
# Clone or download the enhanced AICheck files
git clone <your-repo>
cd <your-repo>/.aicheck/actions/streamlined-action-management/supporting_docs/
```

### Step 2: Install Core Script

```bash
# Option A: System-wide installation (recommended)
sudo cp aicheck-enhanced.sh /usr/local/bin/aicheck
sudo chmod +x /usr/local/bin/aicheck

# Option B: User installation
mkdir -p ~/bin
cp aicheck-enhanced.sh ~/bin/aicheck
chmod +x ~/bin/aicheck
# Add ~/bin to PATH in ~/.bashrc or ~/.zshrc:
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
```

### Step 3: Install Supporting Scripts

```bash
# Create AICheck tools directory
mkdir -p ~/.aicheck/tools

# Copy all supporting scripts
cp yaml-utils.sh ~/.aicheck/tools/
cp deployment-verification-framework.sh ~/.aicheck/tools/
cp issue-tracking-system.sh ~/.aicheck/tools/
cp dependency-management-enhanced.sh ~/.aicheck/tools/
cp migration-tools.sh ~/.aicheck/tools/
cp git-hooks.sh ~/.aicheck/tools/

# Make all executable
chmod +x ~/.aicheck/tools/*.sh
```

### Step 4: Install Git Hooks (Optional but Recommended)

```bash
# From your project directory
~/.aicheck/tools/git-hooks.sh install
```

### Step 5: Install Dependencies (Optional)

For better performance, install yq:

```bash
# macOS
brew install yq

# Ubuntu/Debian
sudo snap install yq

# Or download binary
wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/local/bin/yq
chmod +x /usr/local/bin/yq
```

## Verification

Test your installation:

```bash
# Check aicheck is installed
aicheck --version

# Create a test action
aicheck action new test-installation

# Check YAML was created
ls .aicheck/actions/test-installation/action.yaml

# Clean up
rm -rf .aicheck/actions/test-installation
```

## For Existing Projects

### Migrate Existing Actions

After installation, migrate your existing actions:

```bash
# Migrate all actions at once
~/.aicheck/tools/migration-tools.sh migrate-all

# Or migrate individually
~/.aicheck/tools/migration-tools.sh migrate <action-name>
```

### Update Team Workflows

1. **Update CI/CD pipelines** to use deployment verification:
   ```yaml
   # Example GitHub Actions
   - name: Verify deployment
     run: aicheck verify deployment
   ```

2. **Update deployment scripts** to include verification:
   ```bash
   # deploy.sh
   #!/bin/bash
   # ... deployment steps ...
   
   # Verify deployment succeeded
   aicheck verify deployment || exit 1
   ```

3. **Configure deployment tests** in action.yaml files:
   ```yaml
   deployment:
     required: true
     environments:
       production:
         url: ${{ env.PRODUCTION_URL }}
         test_command: "curl -f ${url}/health"
   ```

## Uninstallation

To remove Enhanced AICheck:

```bash
# Remove main script
sudo rm /usr/local/bin/aicheck

# Remove git hooks
./.aicheck/tools/git-hooks.sh uninstall

# Remove tools directory
rm -rf ~/.aicheck/tools

# Rollback migrations (optional - preserves traditional files)
for action in .aicheck/actions/*; do
  ~/.aicheck/tools/migration-tools.sh rollback $(basename "$action")
done
```

## Troubleshooting

### Command Not Found

If `aicheck` command not found:

1. Check installation location:
   ```bash
   which aicheck
   ls -la /usr/local/bin/aicheck
   ```

2. Ensure PATH includes installation directory:
   ```bash
   echo $PATH
   ```

3. Reload shell configuration:
   ```bash
   source ~/.bashrc  # or ~/.zshrc
   ```

### Permission Denied

If you get permission errors:

```bash
# Check file permissions
ls -la /usr/local/bin/aicheck

# Fix permissions
sudo chmod +x /usr/local/bin/aicheck
```

### YAML Parsing Errors

The system works without yq, but installing it improves performance:

```bash
# Test if yq is available
command -v yq >/dev/null 2>&1 && echo "yq installed" || echo "yq not found"
```

## Integration with Existing Tools

### VS Code

Add to `.vscode/settings.json`:

```json
{
  "terminal.integrated.env.linux": {
    "PATH": "/usr/local/bin:${env:PATH}"
  },
  "terminal.integrated.env.osx": {
    "PATH": "/usr/local/bin:${env:PATH}"
  }
}
```

### Shell Aliases

Add helpful aliases to `~/.bashrc` or `~/.zshrc`:

```bash
alias aic='aicheck'
alias aics='aicheck status'
alias aicv='aicheck verify deployment'
alias aici='aicheck issue'
```

## Next Steps

1. Read the [Training Guide](TRAINING_GUIDE.md)
2. Review the [Quick Reference](QUICK_REFERENCE.md)
3. Run the test suite:
   ```bash
   ~/.aicheck/tools/test-enhanced-commands.sh
   ~/.aicheck/tools/test-migration.sh
   ```

## Support

For issues or questions:
- Check [Documentation](ENHANCED_AICHECK_DOCUMENTATION.md)
- Run tests to verify installation
- Review error messages carefully - they include solutions