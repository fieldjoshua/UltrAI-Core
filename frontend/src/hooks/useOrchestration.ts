import { useState, useCallback } from 'react';
import { processWithFeatherOrchestration } from '../api/orchestrator';

export type OrchestrationStatus = 'idle' | 'processing' | 'success' | 'error';

export interface OrchestrationResult {
  ultra_response: string;
  model_responses?: any[];
  metadata?: any;
}

export function useOrchestration() {
  const [status, setStatus] = useState<OrchestrationStatus>('idle');
  const [result, setResult] = useState<OrchestrationResult | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [progress, setProgress] = useState(0);

  const startOrchestration = useCallback(async (params: {
    prompt: string;
    models: string[];
    pattern?: string;
    ultraModel?: string | null;
    outputFormat?: string;
  }) => {
    setStatus('processing');
    setError(null);
    setResult(null);
    setProgress(0);

    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90));
      }, 500);

      const response = await processWithFeatherOrchestration(params);
      
      clearInterval(progressInterval);
      setProgress(100);
      setResult(response);
      setStatus('success');
      
      return response;
    } catch (err) {
      setStatus('error');
      setError(err instanceof Error ? err : new Error('Orchestration failed'));
      throw err;
    }
  }, []);

  const reset = useCallback(() => {
    setStatus('idle');
    setResult(null);
    setError(null);
    setProgress(0);
  }, []);

  const isProcessing = status === 'processing';
  const isSuccess = status === 'success';
  const isError = status === 'error';
  const isIdle = status === 'idle';

  return {
    status,
    result,
    error,
    progress,
    startOrchestration,
    reset,
    isProcessing,
    isSuccess,
    isError,
    isIdle,
  };
}
