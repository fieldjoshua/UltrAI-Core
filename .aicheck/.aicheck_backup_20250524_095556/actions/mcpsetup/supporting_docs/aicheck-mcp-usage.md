# AICheck MCP Server Usage Guide

The AICheck MCP server has been successfully configured to allow Claude Code to interact with AICheck through the Model Context Protocol.

## Available Tools

### Core AICheck Commands

1. **mcp__aicheck-server__aicheck_status**
   - Get current AICheck status
   - Shows current action, progress, and git status
   - No parameters required

2. **mcp__aicheck-server__aicheck_action_new**
   - Create a new AICheck action
   - Parameters: `name` (string) - Name of the new action

3. **mcp__aicheck-server__aicheck_action_set**
   - Set the current AICheck action
   - Parameters: `name` (string) - Name of the action to set as current

4. **mcp__aicheck-server__aicheck_action_complete**
   - Complete an AICheck action
   - Parameters: `name` (string, optional) - Name of the action to complete

5. **mcp__aicheck-server__aicheck_action_list**
   - List all AICheck actions
   - No parameters required

### Dependency Management

6. **mcp__aicheck-server__aicheck_dependency_add**
   - Add an external dependency
   - Parameters:
     - `name` (string) - Dependency name
     - `version` (string) - Dependency version  
     - `justification` (string) - Justification for adding the dependency
     - `action` (string, optional) - Action name

7. **mcp__aicheck-server__aicheck_dependency_internal**
   - Add an internal dependency between actions
   - Parameters:
     - `dep_action` (string) - The action that depends on another
     - `target_action` (string) - The action being depended upon
     - `type` (string) - Type of dependency (data, function, service, etc.)
     - `description` (string, optional) - Description of the dependency relationship

### System Commands

8. **mcp__aicheck-server__aicheck_exec**
   - Toggle AICheck exec mode
   - No parameters required

## Configuration

The MCP server is configured in Claude Code at:
- Server name: `aicheck-server`
- Command: `node /Users/joshuafield/Documents/Ultra/.mcp/server.js`
- Protocol: stdio

## Usage Examples

### Getting Status
```typescript
// Claude Code can now use:
await mcp__aicheck-server__aicheck_status()
```

### Creating a New Action
```typescript
await mcp__aicheck-server__aicheck_action_new({
  name: "MyNewAction"
})
```

### Adding a Dependency
```typescript
await mcp__aicheck-server__aicheck_dependency_add({
  name: "react",
  version: "^18.0.0",
  justification: "Frontend framework for user interface",
  action: "MyNewAction"
})
```

## Benefits

1. **Integrated Workflow**: Claude Code can now directly interact with AICheck without shell commands
2. **Type Safety**: All AICheck commands are now properly typed and validated
3. **Error Handling**: Better error reporting and handling for AICheck operations
4. **Automation**: Enables automated action management and dependency tracking
5. **Documentation**: All tools are self-documenting with schemas

## Testing

The server has been tested and verified:
- ✅ Server syntax is valid
- ✅ AICheck is accessible
- ✅ All tools are properly configured
- ✅ MCP integration is working

## File Structure

```
.mcp/
├── package.json       # MCP server dependencies
├── server.js          # Main MCP server implementation
└── test-server.js     # Testing script
```

The AICheck MCP server bridges the gap between Claude Code's MCP capabilities and AICheck's project management functionality, creating a seamless development experience.