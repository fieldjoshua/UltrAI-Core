#!/usr/bin/env node
import { exec } from "child_process";
import { promisify } from "util";

const execAsync = promisify(exec);

async function testMCPServer() {
  try {
    console.log("Testing AICheck MCP server...");
    
    // Test if the server can be started (just check syntax)
    const { stdout, stderr } = await execAsync("node --check server.js", {
      cwd: "/Users/joshuafield/Documents/Ultra/.mcp",
      timeout: 5000,
    });
    
    console.log("✅ Server syntax is valid");
    
    // Test if AICheck is accessible
    const { stdout: aicheckOut } = await execAsync("./aicheck status", {
      cwd: "/Users/joshuafield/Documents/Ultra",
      timeout: 10000,
    });
    
    console.log("✅ AICheck is accessible");
    console.log("AICheck Status:", aicheckOut);
    
    console.log("🎉 AICheck MCP server is ready!");
    
  } catch (error) {
    console.error("❌ Test failed:", error.message);
    process.exit(1);
  }
}

testMCPServer();