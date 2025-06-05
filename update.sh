  #!/bin/bash
  rm -rf .aicheck.backup.* 2>/dev/null
  curl -sSL
  https://raw.githubusercontent.com/fieldjoshua/AICheck_MCP/main/aicheck >
   aicheck
  chmod +x aicheck
  mkdir -p .mcp/server
  curl -sSL https://raw.githubusercontent.com/fieldjoshua/AICheck_MCP/main
  /.mcp/server/index.js > .mcp/server/index.js
  curl -sSL https://raw.githubusercontent.com/fieldjoshua/AICheck_MCP/main
  /.mcp/server/package.json > .mcp/server/package.json
  cd .mcp/server && npm install
  EOF
