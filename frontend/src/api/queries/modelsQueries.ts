import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { getModels, getModelStatus } from '../models';
import type { Model } from '../types';

// Query Keys
export const modelsKeys = {
  all: ['models'] as const,
  list: () => [...modelsKeys.all, 'list'] as const,
  status: (modelId: string) => [...modelsKeys.all, 'status', modelId] as const,
};

// Queries
export function useModels(options?: UseQueryOptions<Model[]>) {
  return useQuery({
    queryKey: modelsKeys.list(),
    queryFn: getModels,
    staleTime: 1000 * 60 * 5, // 5 minutes
    ...options,
  });
}

export function useModelStatus(
  modelId: string,
  options?: UseQueryOptions<{ status: string; details?: any }>
) {
  return useQuery({
    queryKey: modelsKeys.status(modelId),
    queryFn: () => getModelStatus(modelId),
    enabled: !!modelId,
    staleTime: 1000 * 30, // 30 seconds
    ...options,
  });
}