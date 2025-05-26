export interface AnalysisRequest {
  prompt: string;
  selected_models: string[];
  ultra_model: string;
  pattern: string;
  options?: Record<string, any>;
}

export interface ModelResponse {
  model_id: string;
  model_name: string;
  content: string;
  timestamp: string;
}

export interface AnalysisPerformance {
  total_time_seconds: number;
  model_times: Record<string, number>;
  token_counts: Record<string, number>;
}

export interface AnalysisResponse {
  status: 'success' | 'error';
  analysis_id: string;
  results: {
    model_responses: ModelResponse[];
    ultra_response: ModelResponse;
    performance: AnalysisPerformance;
  };
}

export interface AnalysisProgress {
  stage: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  progress: number;
  message?: string;
}

export interface AnalysisProgressResponse {
  status: 'success' | 'error';
  progress: AnalysisProgress;
}

export interface AnalysisResultsResponse {
  status: 'success' | 'error';
  results: AnalysisResponse['results'];
}
