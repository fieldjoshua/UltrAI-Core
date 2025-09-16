// API types for orchestrator and related services

export interface OrchestrationRequest {
  prompt: string;
  models?: string[] | null;
  pattern?: 'gut' | 'comparative' | 'consensus' | 'debate' | 'creative' | 'analytical';
  ultraModel?: string | null;
  outputFormat?: 'plain' | 'markdown' | 'json';
}

export interface OrchestrationResponse {
  status: 'success' | 'error';
  ultra_response?: string;
  models_used?: string[];
  processing_time?: number;
  pattern_used?: string;
  initial_responses?: Record<string, any>;
  meta_analysis?: {
    content: string;
    patterns: string[];
    confidence: number;
  };
  ultra_synthesis?: {
    content: string;
    confidence: number;
    synthesis_method: string;
  };
  correlation_id?: string;
  error?: string;
}

export interface Model {
  id?: string;
  name: string;
  provider: string;
  cost_per_1k_tokens: number;
  is_available?: boolean;
  status?: string;
}

export interface AvailableModelsResponse {
  models: (string | Model)[];
  totalCount?: number;
  providers?: {
    openai: string[];
    anthropic: string[];
    google: string[];
    groq: string[];
  };
  modelInfos?: Record<string, {
    provider: string;
    cost_per_1k_tokens: number;
  }>;
  error?: string;
}

export interface ModelHealthResponse {
  models: Record<string, {
    status: 'healthy' | 'degraded' | 'unhealthy';
    latency_ms: number | null;
    success_rate: number;
    last_check: string;
    error?: string;
  }>;
  overall_health: 'healthy' | 'degraded' | 'unhealthy';
  healthy_models: number;
  total_models: number;
}

export interface OrchestratorStatusResponse {
  status: 'operational' | 'degraded' | 'down';
  version: string;
  uptime_seconds: number;
  total_requests: number;
  success_rate: number;
  average_latency_ms: number;
  active_models: number;
  queue_size: number;
  last_error: string | null;
  models?: {
    available?: string[];
  };
}