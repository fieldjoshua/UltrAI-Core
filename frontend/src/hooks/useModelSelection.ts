import { useState, useCallback } from 'react';

export type ModelType = 'gpt-4' | 'claude-3-opus' | 'gemini-1.5-pro' | 'gpt-4o-mini' | 'claude-3-haiku' | 'gpt-3.5-turbo';

export type SelectionMode = 'custom' | 'premium' | 'speed' | 'budget';

export interface ModelSelectionState {
  selectedModels: ModelType[];
  selectionMode: SelectionMode;
}

export interface UseModelSelectionReturn extends ModelSelectionState {
  selectPreset: (preset: SelectionMode) => void;
  toggleModel: (model: ModelType) => void;
  isModelSelected: (model: ModelType) => boolean;
  clearSelection: () => void;
}

const MODEL_PRESETS: Record<SelectionMode, ModelType[]> = {
  premium: ['gpt-4', 'claude-3-opus', 'gemini-1.5-pro'],
  speed: ['gpt-4o-mini', 'claude-3-haiku'],
  budget: ['gpt-3.5-turbo'],
  custom: [],
};

export function useModelSelection(): UseModelSelectionReturn {
  const [selectedModels, setSelectedModels] = useState<ModelType[]>([]);
  const [selectionMode, setSelectionMode] = useState<SelectionMode>('custom');

  const selectPreset = useCallback((preset: SelectionMode) => {
    const models = MODEL_PRESETS[preset];
    setSelectedModels(models);
    setSelectionMode(preset);
  }, []);

  const toggleModel = useCallback((model: ModelType) => {
    setSelectedModels(prev => {
      const isSelected = prev.includes(model);
      let newSelection: ModelType[];

      if (isSelected) {
        // Remove model from selection
        newSelection = prev.filter(m => m !== model);
      } else {
        // Add model to selection
        newSelection = [...prev, model];
      }

      // If selection matches a preset, update mode
      const presetMatch = Object.entries(MODEL_PRESETS).find(([_, models]) =>
        models.length === newSelection.length &&
        models.every(m => newSelection.includes(m))
      );

      if (presetMatch && presetMatch[0] !== 'custom') {
        setSelectionMode(presetMatch[0] as SelectionMode);
      } else {
        setSelectionMode('custom');
      }

      return newSelection;
    });
  }, []);

  const isModelSelected = useCallback((model: ModelType) => {
    return selectedModels.includes(model);
  }, [selectedModels]);

  const clearSelection = useCallback(() => {
    setSelectedModels([]);
    setSelectionMode('custom');
  }, []);

  return {
    selectedModels,
    selectionMode,
    selectPreset,
    toggleModel,
    isModelSelected,
    clearSelection,
  };
}