import { useQuery, useMutation, UseQueryOptions, UseMutationOptions } from '@tanstack/react-query';
import {
  processWithFeatherOrchestration,
  getAvailableModels,
  getModelHealth,
  getOrchestratorStatus,
} from '../orchestrator';
import type {
  OrchestrationRequest,
  OrchestrationResponse,
  AvailableModelsResponse,
  ModelHealthResponse,
  OrchestratorStatusResponse,
} from '../types';

// Query Keys
export const orchestratorKeys = {
  all: ['orchestrator'] as const,
  models: () => [...orchestratorKeys.all, 'models'] as const,
  modelsHealthy: (healthy: boolean) => [...orchestratorKeys.models(), { healthy }] as const,
  health: () => [...orchestratorKeys.all, 'health'] as const,
  status: () => [...orchestratorKeys.all, 'status'] as const,
  orchestration: (id: string) => [...orchestratorKeys.all, 'orchestration', id] as const,
};

// Queries
export function useAvailableModels(
  healthyOnly = false,
  options?: UseQueryOptions<AvailableModelsResponse>
) {
  return useQuery({
    queryKey: orchestratorKeys.modelsHealthy(healthyOnly),
    queryFn: () => getAvailableModels(healthyOnly),
    staleTime: 1000 * 60 * 2, // Consider data fresh for 2 minutes
    ...options,
  });
}

export function useModelHealth(options?: UseQueryOptions<ModelHealthResponse>) {
  return useQuery({
    queryKey: orchestratorKeys.health(),
    queryFn: getModelHealth,
    staleTime: 1000 * 30, // Consider data fresh for 30 seconds
    refetchInterval: 1000 * 60, // Refetch every minute
    ...options,
  });
}

export function useOrchestratorStatus(options?: UseQueryOptions<OrchestratorStatusResponse>) {
  return useQuery({
    queryKey: orchestratorKeys.status(),
    queryFn: getOrchestratorStatus,
    staleTime: 1000 * 30, // Consider data fresh for 30 seconds
    ...options,
  });
}

// Mutations
export function useOrchestration(
  options?: UseMutationOptions<OrchestrationResponse, Error, OrchestrationRequest>
) {
  return useMutation({
    mutationFn: processWithFeatherOrchestration,
    ...options,
  });
}

// Prefetch utilities
export function prefetchModels(queryClient: any, healthyOnly = false) {
  return queryClient.prefetchQuery({
    queryKey: orchestratorKeys.modelsHealthy(healthyOnly),
    queryFn: () => getAvailableModels(healthyOnly),
  });
}

export function prefetchModelHealth(queryClient: any) {
  return queryClient.prefetchQuery({
    queryKey: orchestratorKeys.health(),
    queryFn: getModelHealth,
  });
}