#!/usr/bin/env node
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { exec } from "child_process";
import { promisify } from "util";
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const execAsync = promisify(exec);
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

class AICheckMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: "aicheck-mcp-server",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
    this.setupErrorHandling();
  }

  setupErrorHandling() {
    this.server.onerror = (error) => console.error("[MCP Error]", error);
    process.on("SIGINT", async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  setupToolHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "aicheck_status",
          description: "Get current AICheck status",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "aicheck_action_new",
          description: "Create a new AICheck action",
          inputSchema: {
            type: "object",
            properties: {
              name: {
                type: "string",
                description: "Name of the new action",
              },
            },
            required: ["name"],
          },
        },
        {
          name: "aicheck_action_set",
          description: "Set the current AICheck action",
          inputSchema: {
            type: "object",
            properties: {
              name: {
                type: "string",
                description: "Name of the action to set as current",
              },
            },
            required: ["name"],
          },
        },
        {
          name: "aicheck_action_complete",
          description: "Complete an AICheck action",
          inputSchema: {
            type: "object",
            properties: {
              name: {
                type: "string",
                description: "Name of the action to complete (optional)",
              },
            },
          },
        },
        {
          name: "aicheck_action_list",
          description: "List all AICheck actions",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
        {
          name: "aicheck_dependency_add",
          description: "Add an external dependency",
          inputSchema: {
            type: "object",
            properties: {
              name: {
                type: "string",
                description: "Dependency name",
              },
              version: {
                type: "string", 
                description: "Dependency version",
              },
              justification: {
                type: "string",
                description: "Justification for adding the dependency",
              },
              action: {
                type: "string",
                description: "Action name (optional)",
              },
            },
            required: ["name", "version", "justification"],
          },
        },
        {
          name: "aicheck_dependency_internal",
          description: "Add an internal dependency between actions",
          inputSchema: {
            type: "object",
            properties: {
              dep_action: {
                type: "string",
                description: "The action that depends on another",
              },
              target_action: {
                type: "string", 
                description: "The action being depended upon",
              },
              type: {
                type: "string",
                description: "Type of dependency (data, function, service, etc.)",
              },
              description: {
                type: "string",
                description: "Description of the dependency relationship",
              },
            },
            required: ["dep_action", "target_action", "type"],
          },
        },
        {
          name: "aicheck_exec",
          description: "Toggle AICheck exec mode",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "aicheck_status":
            return await this.runAICheckCommand("status");

          case "aicheck_action_new":
            return await this.runAICheckCommand(`action new ${args.name}`);

          case "aicheck_action_set":
            return await this.runAICheckCommand(`action set ${args.name}`);

          case "aicheck_action_complete":
            const completeCmd = args.name ? `action complete ${args.name}` : "action complete";
            return await this.runAICheckCommand(completeCmd);

          case "aicheck_action_list":
            return await this.runAICheckCommand("action list");

          case "aicheck_dependency_add":
            const addCmd = `dependency add "${args.name}" "${args.version}" "${args.justification}"${args.action ? ` "${args.action}"` : ""}`;
            return await this.runAICheckCommand(addCmd);

          case "aicheck_dependency_internal":
            const internalCmd = `dependency internal "${args.dep_action}" "${args.target_action}" "${args.type}"${args.description ? ` "${args.description}"` : ""}`;
            return await this.runAICheckCommand(internalCmd);

          case "aicheck_exec":
            return await this.runAICheckCommand("exec");

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: "text",
              text: `Error executing AICheck command: ${error.message}`,
            },
          ],
        };
      }
    });
  }

  async runAICheckCommand(command) {
    try {
      const { stdout, stderr } = await execAsync(`./aicheck ${command}`, {
        cwd: projectRoot,
        timeout: 30000,
      });

      return {
        content: [
          {
            type: "text",
            text: stdout || stderr || "Command executed successfully",
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: `AICheck command failed: ${error.message}\\nStderr: ${error.stderr}`,
          },
        ],
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("AICheck MCP server running on stdio");
  }
}

const server = new AICheckMCPServer();
server.run().catch(console.error);