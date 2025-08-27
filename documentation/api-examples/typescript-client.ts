/**
 * UltraAI Core TypeScript/JavaScript API Client Example
 * 
 * This example demonstrates how to use the UltraAI Core API with TypeScript.
 */

interface User {
  id: number;
  email: string;
  username?: string;
  role: string;
  subscription_tier: string;
  account_balance: number;
  is_verified: boolean;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

interface AnalysisOptions {
  temperature?: number;
  max_tokens?: number;
  include_pipeline_details?: boolean;
  save_outputs?: boolean;
}

interface AnalysisResult {
  ultra_synthesis: string;
  metadata: {
    models_used: string[];
    total_tokens: number;
    estimated_cost: number;
    processing_time: number;
  };
  request_id: string;
}

interface Transaction {
  id: number;
  type: 'credit' | 'debit';
  amount: number;
  balance_after: number;
  description: string;
  created_at: string;
}

interface Model {
  id: string;
  name: string;
  provider: string;
  capabilities: string[];
  context_window: number;
  pricing: {
    input_per_1k: number;
    output_per_1k: number;
  };
}

class UltraAIClient {
  private baseUrl: string;
  private token?: string;

  constructor(baseUrl: string = 'https://ultrai-core.onrender.com/api') {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  /**
   * Register a new user account
   */
  async register(
    email: string,
    password: string,
    username?: string,
    fullName?: string
  ): Promise<User> {
    const response = await fetch(`${this.baseUrl}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password,
        username,
        full_name: fullName,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Registration failed');
    }

    return response.json();
  }

  /**
   * Login and store the access token
   */
  async login(emailOrUsername: string, password: string): Promise<User> {
    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email_or_username: emailOrUsername,
        password,
      }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Login failed');
    }

    const data: TokenResponse = await response.json();
    this.token = data.access_token;
    return data.user;
  }

  /**
   * Set the access token manually (e.g., from localStorage)
   */
  setToken(token: string): void {
    this.token = token;
  }

  /**
   * Get the current access token
   */
  getToken(): string | undefined {
    return this.token;
  }

  /**
   * Make an authenticated request
   */
  private async authenticatedFetch(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    if (!this.token) {
      throw new Error('Not authenticated. Please login first.');
    }

    return fetch(url, {
      ...options,
      headers: {
        ...options.headers,
        Authorization: `Bearer ${this.token}`,
        'Content-Type': 'application/json',
      },
    });
  }

  /**
   * Analyze a query using multiple LLMs
   */
  async analyze(
    query: string,
    models: string[] = ['gpt-4o', 'claude-3-5-sonnet-20241022'],
    options: AnalysisOptions = {}
  ): Promise<AnalysisResult> {
    const response = await this.authenticatedFetch(
      `${this.baseUrl}/orchestrator/analyze`,
      {
        method: 'POST',
        body: JSON.stringify({
          query,
          selected_models: models,
          options,
        }),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Analysis failed');
    }

    return response.json();
  }

  /**
   * Get current user information
   */
  async getCurrentUser(): Promise<User> {
    const response = await this.authenticatedFetch(`${this.baseUrl}/auth/me`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get user info');
    }

    return response.json();
  }

  /**
   * Get account balance
   */
  async getBalance(): Promise<number> {
    const response = await this.authenticatedFetch(`${this.baseUrl}/user/balance`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get balance');
    }

    const data = await response.json();
    return data.balance;
  }

  /**
   * Get transaction history
   */
  async getTransactions(
    limit: number = 50,
    offset: number = 0,
    type?: 'credit' | 'debit'
  ): Promise<Transaction[]> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    if (type) params.append('type', type);

    const response = await this.authenticatedFetch(
      `${this.baseUrl}/user/transactions?${params}`
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get transactions');
    }

    const data = await response.json();
    return data.transactions;
  }

  /**
   * Get available models
   */
  async getAvailableModels(): Promise<Model[]> {
    const response = await fetch(`${this.baseUrl}/available-models`);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to get models');
    }

    const data = await response.json();
    return data.models;
  }

  /**
   * Check API health
   */
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl.replace('/api', '')}/health`);

    if (!response.ok) {
      throw new Error('API is unhealthy');
    }

    return response.json();
  }
}

// Example usage
async function main() {
  const client = new UltraAIClient();

  try {
    // Check API health
    console.log('Checking API health...');
    const health = await client.healthCheck();
    console.log('API Status:', health.status);

    // Login (use environment variables for demo)
    const email = process.env.ULTRAI_EMAIL || 'demo@ultrai.app';
    const password = process.env.ULTRAI_PASSWORD || 'demo123';

    console.log(`\nLogging in as ${email}...`);
    const user = await client.login(email, password);
    console.log(`Welcome, ${user.email}!`);
    console.log(`Account balance: $${user.account_balance}`);

    // Get available models
    console.log('\nAvailable models:');
    const models = await client.getAvailableModels();
    for (const model of models) {
      console.log(`  - ${model.name} (${model.id})`);
      console.log(`    Provider: ${model.provider}`);
      console.log(`    Context: ${model.context_window.toLocaleString()} tokens`);
      console.log(
        `    Price: $${model.pricing.input_per_1k}/1k input, ` +
        `$${model.pricing.output_per_1k}/1k output`
      );
    }

    // Analyze a query
    const query = 'Explain the benefits of quantum computing for cryptography';
    console.log(`\nAnalyzing: '${query}'`);
    console.log('Using models: GPT-4o and Claude 3.5 Sonnet');

    const startTime = Date.now();
    const result = await client.analyze(query);
    const elapsed = (Date.now() - startTime) / 1000;

    console.log(`\nAnalysis completed in ${elapsed.toFixed(1)} seconds`);
    console.log(`Cost: $${result.metadata.estimated_cost.toFixed(3)}`);
    console.log(`Tokens used: ${result.metadata.total_tokens.toLocaleString()}`);

    console.log('\n--- Ultra Synthesis™ Result ---');
    const preview = result.ultra_synthesis.substring(0, 500);
    console.log(preview + (result.ultra_synthesis.length > 500 ? '...' : ''));

    // Get recent transactions
    console.log('\n\nRecent transactions:');
    const transactions = await client.getTransactions(5);
    for (const tx of transactions) {
      const sign = tx.type === 'debit' ? '-' : '+';
      console.log(`  ${sign}$${tx.amount.toFixed(3)} - ${tx.description}`);
      console.log(`    Balance after: $${tx.balance_after.toFixed(2)}`);
      console.log(`    Date: ${tx.created_at}`);
    }

    // Check final balance
    const balance = await client.getBalance();
    console.log(`\nCurrent balance: $${balance.toFixed(2)}`);

  } catch (error) {
    console.error('Error:', error);
  }
}

// Run the example
if (require.main === module) {
  main();
}

// Export for use as a module
export { UltraAIClient, User, AnalysisResult, Transaction, Model };