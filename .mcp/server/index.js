#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ReadResourceRequestSchema,
  InitializeRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { execSync } from 'child_process';

class AICheckMCPServer {
  constructor() {
    this.server = new Server(
      {
        name: 'aicheck-mcp-server',
        version: '4.3.0',
      },
      {
        capabilities: {
          resources: {},
          tools: {},
        },
      }
    );
    
    this.setupHandlers();
  }

  setupHandlers() {
    // Add the required initialize handler
    this.server.setRequestHandler(InitializeRequestSchema, async (request) => {
      return {
        protocolVersion: '2024-11-05',
        capabilities: {
          resources: {},
          tools: {},
        },
        serverInfo: {
          name: 'aicheck-mcp-server',
          version: '4.3.0',
        },
      };
    });

    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [
          {
            uri: 'aicheck://rules',
            name: 'AICheck Rules',
            description: 'The rules governing the AICheck system',
            mimeType: 'text/markdown',
          },
          {
            uri: 'aicheck://actions_index',
            name: 'Actions Index',
            description: 'The index of all actions in the project',
            mimeType: 'text/markdown',
          },
          {
            uri: 'aicheck://current_action',
            name: 'Current Action',
            description: 'The currently active action',
            mimeType: 'text/plain',
          },
        ],
      };
    });

    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const { uri } = request.params;
      
      try {
        let content = '';
        
        switch (uri) {
          case 'aicheck://rules':
            if (existsSync('.aicheck/RULES.md')) {
              content = readFileSync('.aicheck/RULES.md', 'utf-8');
            } else {
              content = 'AICheck rules not found';
            }
            break;
            
          case 'aicheck://actions_index':
            if (existsSync('.aicheck/actions_index.md')) {
              content = readFileSync('.aicheck/actions_index.md', 'utf-8');
            } else {
              content = 'Actions index not found';
            }
            break;
            
          case 'aicheck://current_action':
            if (existsSync('.aicheck/current_action')) {
              content = readFileSync('.aicheck/current_action', 'utf-8').trim();
            } else {
              content = 'None';
            }
            break;
            
          default:
            throw new Error(`Unknown resource: ${uri}`);
        }
        
        return {
          contents: [
            {
              uri,
              mimeType: uri.includes('rules') || uri.includes('actions_index') ? 'text/markdown' : 'text/plain',
              text: content,
            },
          ],
        };
      } catch (error) {
        throw new Error(`Failed to read resource ${uri}: ${error.message}`);
      }
    });

    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'aicheck_getCurrentAction',
            description: 'Get the currently active action',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'aicheck_listActions',
            description: 'List all actions in the project',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'aicheck_getActionPlan',
            description: 'Get the plan for a specific action',
            inputSchema: {
              type: 'object',
              properties: {
                actionName: {
                  type: 'string',
                  description: 'The name of the action',
                },
              },
              required: ['actionName'],
            },
          },
          {
            name: 'aicheck_setCurrentAction',
            description: 'Set the currently active action (requires human approval)',
            inputSchema: {
              type: 'object',
              properties: {
                actionName: {
                  type: 'string',
                  description: 'The name of the action to set as current',
                },
              },
              required: ['actionName'],
            },
          },
          {
            name: 'aicheck_logClaudeInteraction',
            description: 'Log a Claude interaction for the current action',
            inputSchema: {
              type: 'object',
              properties: {
                purpose: {
                  type: 'string',
                  description: 'The purpose of the interaction',
                },
                content: {
                  type: 'string',
                  description: 'The content of the interaction',
                },
              },
              required: ['purpose', 'content'],
            },
          },
          {
            name: 'aicheck_contextPollution',
            description: 'Analyze context pollution and suggest cleanup actions',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'aicheck_contextCompact',
            description: 'Automatically compact context and archive old interactions',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'aicheck_checkBoundaries',
            description: 'Check for action boundary violations and scope creep',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'aicheck_analyzeCosts',
            description: 'Analyze usage patterns and cost efficiency',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
          {
            name: 'aicheck_optimizeContext',
            description: 'Auto-optimize context for better performance and cost efficiency',
            inputSchema: {
              type: 'object',
              properties: {},
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;
      
      try {
        switch (name) {
          case 'aicheck_getCurrentAction':
            return await this.getCurrentAction();
            
          case 'aicheck_listActions':
            return await this.listActions();
            
          case 'aicheck_getActionPlan':
            return await this.getActionPlan(args.actionName);
            
          case 'aicheck_setCurrentAction':
            return await this.setCurrentAction(args.actionName);
            
          case 'aicheck_logClaudeInteraction':
            return await this.logClaudeInteraction(args.purpose, args.content);
            
          case 'aicheck_contextPollution':
            return await this.analyzeContextPollution();
            
          case 'aicheck_contextCompact':
            return await this.compactContext();
            
          case 'aicheck_checkBoundaries':
            return await this.checkActionBoundaries();
            
          case 'aicheck_analyzeCosts':
            return await this.analyzeCosts();
            
          case 'aicheck_optimizeContext':
            return await this.optimizeContext();
            
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        return {
          content: [
            {
              type: 'text',
              text: `Error: ${error.message}`,
            },
          ],
        };
      }
    });
  }

  async getCurrentAction() {
    try {
      const current = existsSync('.aicheck/current_action') 
        ? readFileSync('.aicheck/current_action', 'utf-8').trim()
        : 'None';
      
      return {
        content: [
          {
            type: 'text',
            text: current,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to get current action: ${error.message}`);
    }
  }

  async listActions() {
    try {
      const actionsIndex = existsSync('.aicheck/actions_index.md')
        ? readFileSync('.aicheck/actions_index.md', 'utf-8')
        : 'No actions found';
      
      return {
        content: [
          {
            type: 'text',
            text: actionsIndex,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to list actions: ${error.message}`);
    }
  }

  async getActionPlan(actionName) {
    try {
      const dirName = actionName.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
      const planPath = `.aicheck/actions/${dirName}/${dirName}-plan.md`;
      
      if (!existsSync(planPath)) {
        throw new Error(`Action plan not found for ${actionName}`);
      }
      
      const plan = readFileSync(planPath, 'utf-8');
      
      return {
        content: [
          {
            type: 'text',
            text: plan,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to get action plan: ${error.message}`);
    }
  }

  async setCurrentAction(actionName) {
    return {
      content: [
        {
          type: 'text',
          text: `Setting current action to ${actionName} requires human approval. Please run: ./aicheck action set ${actionName}`,
        },
      ],
    };
  }

  async logClaudeInteraction(purpose, content) {
    try {
      const currentAction = existsSync('.aicheck/current_action')
        ? readFileSync('.aicheck/current_action', 'utf-8').trim()
        : null;
      
      if (!currentAction || currentAction === 'None') {
        throw new Error('No current action set');
      }
      
      const dirName = currentAction.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
      const interactionDir = `.aicheck/actions/${dirName}/supporting_docs/claude-interactions`;
      
      if (!existsSync(interactionDir)) {
        mkdirSync(interactionDir, { recursive: true });
      }
      
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `${timestamp}-${purpose.replace(/\s+/g, '-').toLowerCase()}.md`;
      const filepath = join(interactionDir, filename);
      
      const logContent = `# Claude Interaction: ${purpose}

**Date:** ${new Date().toISOString()}
**Purpose:** ${purpose}
**Action:** ${currentAction}

## Content

${content}
`;
      
      writeFileSync(filepath, logContent);
      
      return {
        content: [
          {
            type: 'text',
            text: `Claude interaction logged: ${filepath}`,
          },
        ],
      };
    } catch (error) {
      throw new Error(`Failed to log Claude interaction: ${error.message}`);
    }
  }

  async analyzeContextPollution() {
    try {
      const { execSync } = await import('child_process');
      const result = execSync('./aicheck context pollution', { encoding: 'utf-8' });
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error analyzing context pollution: ${error.message}`,
          },
        ],
      };
    }
  }

  async compactContext() {
    try {
      const { execSync } = await import('child_process');
      const result = execSync('./aicheck context compact', { encoding: 'utf-8' });
      
      return {
        content: [
          {
            type: 'text',
            text: `Context compaction completed: ${result}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error compacting context: ${error.message}`,
          },
        ],
      };
    }
  }

  async checkActionBoundaries() {
    try {
      const { execSync } = await import('child_process');
      const result = execSync('./aicheck context check', { encoding: 'utf-8' });
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error checking boundaries: ${error.message}`,
          },
        ],
      };
    }
  }

  async analyzeCosts() {
    try {
      const { execSync } = await import('child_process');
      const result = execSync('./aicheck context cost', { encoding: 'utf-8' });
      
      return {
        content: [
          {
            type: 'text',
            text: result,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error analyzing costs: ${error.message}`,
          },
        ],
      };
    }
  }

  async optimizeContext() {
    try {
      const { execSync } = await import('child_process');
      const result = execSync('./aicheck context optimize', { encoding: 'utf-8' });
      
      return {
        content: [
          {
            type: 'text',
            text: `Context optimization completed: ${result}`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `Error optimizing context: ${error.message}`,
          },
        ],
      };
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('AICheck MCP server running on stdio');
  }
}

const server = new AICheckMCPServer();
server.run().catch(console.error);
