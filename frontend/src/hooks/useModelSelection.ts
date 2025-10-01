import { useState } from 'react';

export type Model = string;

export type Preset = 'premium' | 'speed' | 'budget';

export const presets: Record<Preset, Model[]> = {
  premium: ['gpt-4', 'claude-3-opus', 'gemini-1.5-pro'],
  speed: ['gpt-4o-mini', 'claude-3-haiku'],
  budget: ['gpt-3.5-turbo'],
};

export const useModelSelection = () => {
  const [selectedModels, setSelectedModels] = useState<Model[]>([]);
  const [selectionMode, setSelectionMode] = useState<Preset | null>(null);

  const selectPreset = (preset: Preset) => {
    setSelectedModels(presets[preset]);
    setSelectionMode(preset);
  };

  const toggleModel = (model: Model) => {
    setSelectedModels(prev =>
      prev.includes(model) ? prev.filter(m => m !== model) : [...prev, model]
    );
  };

  return {
    selectedModels,
    selectionMode,
    selectPreset,
    toggleModel,
  };
};