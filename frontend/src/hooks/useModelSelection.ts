import { useState, useCallback } from 'react';

export type SelectionMode = 'premium' | 'speed' | 'budget' | 'custom';

const PRESETS = {
  premium: ['gpt-4', 'claude-3-opus', 'gemini-1.5-pro'],
  speed: ['gpt-4o-mini', 'claude-3-haiku'],
  budget: ['gpt-3.5-turbo'],
};

export function useModelSelection() {
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [selectionMode, setSelectionMode] = useState<SelectionMode>('premium');

  const selectPreset = useCallback((mode: 'premium' | 'speed' | 'budget') => {
    setSelectionMode(mode);
    setSelectedModels(PRESETS[mode]);
  }, []);

  const toggleModel = useCallback((model: string) => {
    setSelectionMode('custom');
    setSelectedModels(prev => 
      prev.includes(model) 
        ? prev.filter(m => m !== model)
        : [...prev, model]
    );
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedModels([]);
    setSelectionMode('custom');
  }, []);

  const hasMinimumModels = selectedModels.length >= 2;

  return {
    selectedModels,
    selectionMode,
    selectPreset,
    toggleModel,
    clearSelection,
    hasMinimumModels,
  };
}
