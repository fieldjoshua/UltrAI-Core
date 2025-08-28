// Type definitions for orchestrator API

export interface OrchestratorOptions {
  selected_models?: string[];
  include_pipeline_details?: boolean;
  include_initial_responses?: boolean;
  [key: string]: any;
}

export interface OrchestratorResponse {
  success: boolean;
  results?: any;
  error?: string;
  ultra_response?: string;
  initial_responses?: any;
  peer_review?: any;
  meta_analysis?: any;
  ultra_synthesis?: any;
}

export interface ProcessWithFeatherOrchestrationParams {
  prompt: string;
  models?: string[] | null;
  pattern?: string;
  ultraModel?: string | null;
  outputFormat?: string;
}

export function processWithFeatherOrchestration(
  params: ProcessWithFeatherOrchestrationParams
): Promise<OrchestratorResponse>;

export function getAvailableModels(): Promise<{
  models: Array<{
    id: string;
    name: string;
    provider: string;
    status: string;
  }>;
  totalCount: number;
}>;

export function checkModelStatus(modelId: string): Promise<{
  available: boolean;
  status: string;
  error?: string;
}>;