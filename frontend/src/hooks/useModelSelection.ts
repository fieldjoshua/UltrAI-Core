import { useState, useCallback, useMemo } from 'react';

export type SelectionMode = 'premium' | 'speed' | 'budget' | 'custom';

export interface ModelPreset {
  [key: string]: string[];
}

export const MODEL_PRESETS: ModelPreset = {
  premium: ['gpt-4', 'claude-3-opus', 'gemini-1.5-pro'],
  speed: ['gpt-4o-mini', 'claude-3-haiku'],
  budget: ['gpt-3.5-turbo'],
};

export interface UseModelSelectionReturn {
  selectedModels: string[];
  selectionMode: SelectionMode;
  selectPreset: (mode: SelectionMode) => void;
  toggleModel: (model: string) => void;
  clearSelection: () => void;
  isModelSelected: (model: string) => boolean;
  availableModels: string[];
}

export function useModelSelection(): UseModelSelectionReturn {
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectionMode, setSelectionMode] = useState<SelectionMode>('custom');

  const selectPreset = useCallback((mode: SelectionMode) => {
    setSelectedModels(MODEL_PRESETS[mode] || []);
    setSelectionMode(mode);
  }, []);

  const toggleModel = useCallback((model: string) => {
    setSelectedModels(prev => {
      const isSelected = prev.includes(model);
      if (isSelected) {
        // Remove model
        return prev.filter(m => m !== model);
      } else {
        // Add model
        return [...prev, model];
      }
    });
    // Always set to custom mode when manually toggling
    setSelectionMode('custom');
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedModels([]);
    setSelectionMode('custom');
  }, []);

  const isModelSelected = useCallback((model: string) => {
    return selectedModels.includes(model);
  }, [selectedModels]);

  const availableModels = useMemo(() => {
    return Object.values(MODEL_PRESETS).flat();
  }, []);

  return {
    selectedModels,
    selectionMode,
    selectPreset,
    toggleModel,
    clearSelection,
    isModelSelected,
    availableModels,
  };
}