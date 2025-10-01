import React from 'react';
import { Button } from '../../Button';
import { useModelSelection, type ModelType } from '../../../hooks/useModelSelection';

interface ModelStepProps {
  selectedModels: ModelType[];
  onModelsChange: (models: ModelType[]) => void;
  onNext: () => void;
  onBack: () => void;
}

export function ModelStep({ selectedModels, onModelsChange, onNext, onBack }: ModelStepProps) {
  const {
    selectPreset,
    toggleModel,
    isModelSelected,
    presets,
    setSelectionMode,
    selectionMode
  } = useModelSelection('multiple');

  const handlePresetSelect = (preset: 'premium' | 'speed' | 'budget') => {
    selectPreset(preset);
    const presetModels = presets[preset].models;
    onModelsChange(presetModels);

    // Auto-select single mode for budget preset since it only has one model
    if (preset === 'budget') {
      setSelectionMode('single');
    }
  };

  const handleModelToggle = (model: ModelType) => {
    toggleModel(model);
    const newModels = isModelSelected(model)
      ? selectedModels.filter(m => m !== model)
      : [...selectedModels, model];
    onModelsChange(newModels);
  };

  const handleModeChange = (mode: 'single' | 'multiple') => {
    setSelectionMode(mode);
    // If switching to single mode and multiple models are selected, keep only the first one
    if (mode === 'single' && selectedModels.length > 1) {
      onModelsChange([selectedModels[0]]);
    }
  };

  const MODEL_DETAILS: Record<ModelType, { name: string; description: string; icon: string }> = {
    'gpt-4': { name: 'GPT-4', description: 'Most capable model for complex reasoning', icon: '🧠' },
    'claude-3-opus': { name: 'Claude 3 Opus', description: 'Excellent for analysis and writing', icon: '✍️' },
    'gemini-1.5-pro': { name: 'Gemini 1.5 Pro', description: 'Great for multimodal tasks', icon: '🎯' },
    'gpt-4o-mini': { name: 'GPT-4o Mini', description: 'Fast and efficient for most tasks', icon: '⚡' },
    'claude-3-haiku': { name: 'Claude 3 Haiku', description: 'Quick responses with good quality', icon: '🚀' },
    'gpt-3.5-turbo': { name: 'GPT-3.5 Turbo', description: 'Reliable and cost-effective', icon: '💰' }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-cyber-green mb-2">
          Select AI Models
        </h2>
        <p className="text-gray-300">
          Choose from our curated model presets or customize your selection
        </p>
      </div>

      {/* Selection Mode Toggle */}
      <div className="flex justify-center">
        <div className="bg-gray-800 rounded-lg p-1 flex">
          <button
            onClick={() => handleModeChange('single')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectionMode === 'single'
                ? 'bg-cyber-green text-black'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Single Model
          </button>
          <button
            onClick={() => handleModeChange('multiple')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              selectionMode === 'multiple'
                ? 'bg-cyber-green text-black'
                : 'text-gray-400 hover:text-white'
            }`}
          >
            Multiple Models
          </button>
        </div>
      </div>

      {/* Preset Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {Object.entries(presets).map(([key, preset]) => (
          <div
            key={key}
            className={`p-6 rounded-lg border-2 transition-all duration-200 cursor-pointer ${
              selectedModels.length === preset.models.length &&
              preset.models.every(model => selectedModels.includes(model))
                ? 'border-cyber-green bg-cyber-green/10'
                : 'border-gray-600 hover:border-gray-400 hover:bg-gray-700/30'
            }`}
            onClick={() => handlePresetSelect(key as 'premium' | 'speed' | 'budget')}
          >
            <h3 className="text-lg font-semibold text-white mb-2">{preset.name}</h3>
            <p className="text-gray-300 text-sm mb-3">{preset.description}</p>
            <div className="space-y-1">
              {preset.models.map((model) => (
                <div key={model} className="text-xs text-gray-400 flex items-center space-x-1">
                  <span>{MODEL_DETAILS[model].icon}</span>
                  <span>{MODEL_DETAILS[model].name}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Individual Model Selection */}
      <div className="border-t border-gray-600 pt-6">
        <h3 className="text-lg font-semibold text-white mb-4 text-center">
          Or select individual models
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {Object.entries(MODEL_DETAILS).map(([modelKey, details]) => (
            <div
              key={modelKey}
              className={`p-4 rounded-lg border transition-all duration-200 cursor-pointer ${
                isModelSelected(modelKey as ModelType)
                  ? 'border-cyber-green bg-cyber-green/10'
                  : 'border-gray-600 hover:border-gray-400 hover:bg-gray-700/30'
              }`}
              onClick={() => handleModelToggle(modelKey as ModelType)}
            >
              <div className="flex items-start space-x-3">
                <div className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                  isModelSelected(modelKey as ModelType)
                    ? 'bg-cyber-green border-cyber-green'
                    : 'border-gray-400'
                }`}>
                  {isModelSelected(modelKey as ModelType) && (
                    <div className="w-2 h-2 bg-black rounded-full"></div>
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-lg">{details.icon}</span>
                    <span className="font-medium text-white">{details.name}</span>
                  </div>
                  <p className="text-xs text-gray-400">{details.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedModels.length > 0 && (
        <div className="text-center text-sm text-gray-400">
          {selectedModels.length} model{selectedModels.length !== 1 ? 's' : ''} selected
        </div>
      )}

      <div className="flex justify-between pt-6">
        <Button
          onClick={onBack}
          variant="outline"
          className="border-gray-400 text-gray-400 hover:bg-gray-400/10"
        >
          Back
        </Button>
        <Button
          onClick={onNext}
          disabled={selectedModels.length === 0}
          className="bg-cyber-green hover:bg-cyber-green/80 text-black disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue
        </Button>
      </div>
    </div>
  );
}