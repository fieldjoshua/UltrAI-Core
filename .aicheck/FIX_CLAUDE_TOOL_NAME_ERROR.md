# How to Fix Claude Tool Name Error

## Error Message
```
API Error: 400 {"type":"error","error":{"type":"invalid_request_error","message":"tools.15.custom.name: String should match pattern '^[a-zA-Z0-9_-]{1,64}$'"}}
```

## What This Means
- Tool #15 in your request has an invalid name
- The name contains characters that aren't allowed
- Only letters, numbers, underscores, and hyphens are permitted

## How to Find the Problem

### 1. Check Your Tool Definitions
Look for where you define tools in your code. It might look like:

```python
tools = [
    {
        "name": "my-tool-name",  # This is what needs to be checked
        "description": "...",
        "parameters": {...}
    },
    # ... more tools
]
```

### 2. Common Issues to Look For

**❌ INVALID Names:**
```python
"name": "My Tool Name"          # Spaces not allowed
"name": "my.tool.name"          # Dots not allowed
"name": "my@tool"               # Special characters not allowed
"name": "my tool!"              # Spaces and special chars
"name": "get/data"              # Slashes not allowed
"name": ""                      # Empty name
"name": "this_is_a_really_long_tool_name_that_exceeds_64_characters_limit"  # Too long
```

**✅ VALID Names:**
```python
"name": "my_tool_name"          # Underscores OK
"name": "my-tool-name"          # Hyphens OK
"name": "getTool123"            # Letters and numbers OK
"name": "TOOL_NAME"             # Uppercase OK
"name": "tool-2-use"            # Mix of allowed chars
```

## How to Fix

### Step 1: Find Tool #15
Since the error mentions "tools.15", it's the 16th tool in your array (0-indexed).

```python
# Print out your tools to find the problematic one
for i, tool in enumerate(tools):
    print(f"Tool {i}: {tool.get('name', 'NO NAME')}")
```

### Step 2: Fix the Name
Replace invalid characters:

```python
def fix_tool_name(name):
    """Convert any string to a valid tool name"""
    import re
    # Replace spaces and invalid chars with underscores
    fixed = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    # Ensure it's not empty
    if not fixed:
        fixed = "unnamed_tool"
    # Truncate to 64 chars
    return fixed[:64]

# Example usage
bad_name = "My Tool: Get Data!"
good_name = fix_tool_name(bad_name)  # Returns: "My_Tool__Get_Data_"
```

### Step 3: Common Fixes

```python
# If using spaces
"Get User Data" → "get_user_data" or "get-user-data"

# If using dots
"api.endpoint.call" → "api_endpoint_call"

# If using slashes
"read/write" → "read_write"

# If too long
"very_long_tool_name_that_exceeds_the_maximum_allowed_length_of_64_chars" → "very_long_tool_name_that_exceeds_the_maximum_allowed_length_of"
```

## Quick Debug Script

```python
def validate_claude_tools(tools):
    """Validate all tool names in a list"""
    import re
    pattern = re.compile(r'^[a-zA-Z0-9_-]{1,64}$')
    
    for i, tool in enumerate(tools):
        name = tool.get('name', '')
        if not pattern.match(name):
            print(f"❌ Tool {i}: '{name}' is INVALID")
            print(f"   Suggestion: '{fix_tool_name(name)}'")
        else:
            print(f"✅ Tool {i}: '{name}' is valid")

# Use this to check your tools
validate_claude_tools(your_tools_list)
```

## If Using MCP (Model Context Protocol)

MCP tools might be defined in a config file:
```json
{
  "tools": {
    "My Tool": {  // This name needs fixing
      "description": "..."
    }
  }
}
```

Change to:
```json
{
  "tools": {
    "my_tool": {  // Fixed name
      "description": "..."
    }
  }
}
```

## Prevention

Always validate tool names before sending:
```python
def create_tool(name, description, parameters):
    """Create a tool with validated name"""
    clean_name = fix_tool_name(name)
    return {
        "name": clean_name,
        "description": description,
        "parameters": parameters
    }
```

The error should disappear once you fix tool #15's name to only contain letters, numbers, underscores, or hyphens!