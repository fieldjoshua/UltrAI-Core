import { useState, useCallback } from 'react';

export type ModelType = 'gpt-4' | 'claude-3-opus' | 'gemini-1.5-pro' | 'gpt-4o-mini' | 'claude-3-haiku' | 'gpt-3.5-turbo';

export type SelectionMode = 'single' | 'multiple';

export interface ModelPreset {
  name: string;
  models: ModelType[];
  description: string;
}

export interface UseModelSelectionReturn {
  selectedModels: ModelType[];
  selectionMode: SelectionMode;
  setSelectionMode: (mode: SelectionMode) => void;
  selectPreset: (preset: 'premium' | 'speed' | 'budget') => void;
  toggleModel: (model: ModelType) => void;
  clearSelection: () => void;
  isModelSelected: (model: ModelType) => boolean;
  presets: Record<string, ModelPreset>;
}

const MODEL_PRESETS = {
  premium: {
    name: 'Premium',
    models: ['gpt-4', 'claude-3-opus', 'gemini-1.5-pro'] as ModelType[],
    description: 'Highest quality models for complex analysis'
  },
  speed: {
    name: 'Speed',
    models: ['gpt-4o-mini', 'claude-3-haiku'] as ModelType[],
    description: 'Fast processing with good quality'
  },
  budget: {
    name: 'Budget',
    models: ['gpt-3.5-turbo'] as ModelType[],
    description: 'Cost-effective option for basic tasks'
  }
};

export function useModelSelection(initialMode: SelectionMode = 'multiple'): UseModelSelectionReturn {
  const [selectedModels, setSelectedModels] = useState<ModelType[]>([]);
  const [selectionMode, setSelectionMode] = useState<SelectionMode>(initialMode);

  const selectPreset = useCallback((preset: 'premium' | 'speed' | 'budget') => {
    const presetModels = MODEL_PRESETS[preset].models;
    setSelectedModels(presetModels);

    // If in single mode, ensure only one model is selected
    if (selectionMode === 'single' && presetModels.length > 0) {
      setSelectedModels([presetModels[0]]);
    }
  }, [selectionMode]);

  const toggleModel = useCallback((model: ModelType) => {
    setSelectedModels(prev => {
      const isSelected = prev.includes(model);

      if (selectionMode === 'single') {
        // In single mode, selecting a model replaces the current selection
        return isSelected ? [] : [model];
      } else {
        // In multiple mode, toggle the model
        return isSelected
          ? prev.filter(m => m !== model)
          : [...prev, model];
      }
    });
  }, [selectionMode]);

  const clearSelection = useCallback(() => {
    setSelectedModels([]);
  }, []);

  const isModelSelected = useCallback((model: ModelType) => {
    return selectedModels.includes(model);
  }, [selectedModels]);

  return {
    selectedModels,
    selectionMode,
    setSelectionMode,
    selectPreset,
    toggleModel,
    clearSelection,
    isModelSelected,
    presets: MODEL_PRESETS
  };
}