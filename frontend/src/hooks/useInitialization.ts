import { useState, useEffect } from 'react';
import apiClient from '../services/api';

export interface InitializationStep {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'loading' | 'success' | 'error';
  error?: string;
  details?: Record<string, any>;
}

export interface InitializationStatus {
  steps: InitializationStep[];
  overall_status: 'initializing' | 'ready' | 'error';
  progress: number;
  message: string;
}

export const useInitialization = () => {
  const [status, setStatus] = useState<InitializationStatus>({
    steps: [],
    overall_status: 'initializing',
    progress: 0,
    message: 'Starting initialization...',
  });

  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    const checkInitialization = async () => {
      try {
        // Check various endpoints to determine initialization status
        const checks = [
          {
            id: 'env',
            name: 'Environment Configuration',
            description: 'Loading environment variables and API keys',
            endpoint: '/test/env-check',
          },
          {
            id: 'models',
            name: 'AI Model Registry',
            description: 'Initializing available LLM models',
            endpoint: '/available-models',
          },
          {
            id: 'health',
            name: 'System Health',
            description: 'Verifying core services',
            endpoint: '/health',
          },
          {
            id: 'cache',
            name: 'Cache Service',
            description: 'Checking cache connectivity',
            endpoint: '/cache/health',
          },
          {
            id: 'orchestrator',
            name: 'Orchestrator Service',
            description: 'Initializing AI orchestration',
            endpoint: '/orchestrator/health',
          },
        ];

        const steps: InitializationStep[] = [];
        let successCount = 0;

        // Run checks in sequence with a small delay for visual effect
        for (const check of checks) {
          // Update to show this step is loading
          setStatus(prev => ({
            ...prev,
            steps: [
              ...steps,
              { ...check, status: 'loading' },
              ...checks.slice(checks.indexOf(check) + 1).map(c => ({
                ...c,
                status: 'pending' as const,
              })),
            ],
            progress: (steps.length / checks.length) * 100,
            message: `Checking ${check.name}...`,
          }));

          try {
            const response = await apiClient.get(check.endpoint);

            // Extract relevant details based on endpoint
            let details: any = {};
            if (check.id === 'env' && response.data.api_keys) {
              const keyCount = response.data.total_keys_found || 0;
              details = { api_keys_found: keyCount };
            } else if (check.id === 'models' && response.data.models) {
              details = {
                total_models: response.data.total_count,
                healthy_models: response.data.healthy_count,
              };
            }

            steps.push({
              ...check,
              status: 'success',
              details,
            });
            successCount++;
          } catch (error: any) {
            steps.push({
              ...check,
              status: 'error',
              error:
                error.response?.data?.message ||
                error.message ||
                'Check failed',
            });
          }

          // Small delay for visual effect
          await new Promise(resolve => setTimeout(resolve, 300));
        }

        // Update final status
        const allSuccess = successCount === checks.length;
        setStatus({
          steps,
          overall_status: allSuccess ? 'ready' : 'error',
          progress: 100,
          message: allSuccess
            ? 'All systems ready!'
            : 'Some services failed to initialize',
        });

        if (allSuccess) {
          setTimeout(() => setIsComplete(true), 1000);
        } else {
          // Retry after 5 seconds if there were errors
          setTimeout(checkInitialization, 5000);
        }
      } catch (error) {
        console.error('Initialization check failed:', error);
        setStatus(prev => ({
          ...prev,
          overall_status: 'error',
          message: 'Failed to check system status',
        }));
      }
    };

    // Start checking immediately
    checkInitialization();

    // Clean up on unmount
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, []);

  return { status, isComplete };
};
