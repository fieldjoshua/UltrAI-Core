# Setting Up Render MCP Server in Claude Code

## Step 1: Create Render API Key (You already have: rnd_NfrFXrFHdSs0kU2LfFfaWPkN6lzH)

## Step 2: Configure Claude Code

You need to add this configuration to your Claude Code settings file.

### On macOS/Linux:
Edit: `~/.claude/claude_desktop_config.json`

### On Windows:
Edit: `%APPDATA%\Claude\claude_desktop_config.json`

### Add this configuration:

```json
{
  "mcpServers": {
    "render": {
      "command": "npx",
      "args": [
        "-y",
        "@renderco/mcp-server-render"
      ],
      "env": {
        "RENDER_API_KEY": "rnd_NfrFXrFHdSs0kU2LfFfaWPkN6lzH"
      }
    }
  }
}
```

## Step 3: Restart Claude Code

1. Completely quit Claude Code
2. Start it again
3. The Render MCP server should now be available

## Step 4: Test It

Once configured, you can ask me to:
- List your Render services
- Check environment variables
- Update service configurations
- View logs and metrics

## Alternative: Direct Setup

If the above doesn't work, try:

1. Install the MCP server globally:
```bash
npm install -g @renderco/mcp-server-render
```

2. Then update the config to use the global installation path

## Note

The MCP server will give me access to:
- List and manage services
- Update environment variables
- Check deployment status
- Query databases (read-only)
- View logs and metrics

But I cannot:
- Delete services
- Create free tier services
- Modify billing settings