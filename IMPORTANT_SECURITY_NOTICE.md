# IMPORTANT: API Key Security

## Immediate Action Required

1. **Go to Render Dashboard** → Account Settings → API Keys
2. **Delete the API key** that starts with `rnd_NfrFXrFH...`
3. **Create a new API key** for future use
4. **Never share API keys in chat messages**

## If You Want to Use Render MCP

To set up the Render MCP server with Claude Code:

1. Create a new Render API key
2. Configure it in Claude Code settings (not in chat)
3. Add the MCP server configuration

## For Now: Manual Configuration

Since the API key has been exposed, please:
1. Continue using the Render Dashboard manually
2. Check your environment group settings
3. Ensure variables are properly linked

## Current Status Check

Run this after securing your API key:
```bash
./scripts/check-deployment.sh staging
./scripts/check-deployment.sh production
```

---
**Remember**: API keys are like passwords - keep them secret!