import React from 'react';
import { useModelSelection, SelectionMode } from '../../hooks/useModelSelection';
import { Button } from '../../ui/Button';
import { Badge } from '../../ui/Badge';

interface ModelStepProps {
  selectedModels?: string[];
  selectionMode?: SelectionMode;
  onModelsChange?: (models: string[], mode: SelectionMode) => void;
}

export function ModelStep({
  selectedModels: externalSelectedModels,
  selectionMode: externalSelectionMode,
  onModelsChange
}: ModelStepProps) {
  const modelSelection = useModelSelection();

  // Use external state if provided, otherwise use internal state
  const selectedModels = externalSelectedModels ?? modelSelection.selectedModels;
  const selectionMode = externalSelectionMode ?? modelSelection.selectionMode;

  const handlePresetSelect = (mode: SelectionMode) => {
    modelSelection.selectPreset(mode);
    if (onModelsChange) {
      onModelsChange(modelSelection.selectedModels, mode);
    }
  };

  const handleModelToggle = (model: string) => {
    modelSelection.toggleModel(model);
    if (onModelsChange) {
      onModelsChange(modelSelection.selectedModels, modelSelection.selectionMode);
    }
  };

  const getPresetButtonClass = (mode: SelectionMode) => {
    const isSelected = selectionMode === mode;
    return `px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
      isSelected
        ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-lg'
        : 'bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white'
    }`;
  };

  const getModelButtonClass = (model: string) => {
    const isSelected = selectedModels.includes(model);
    return `px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
      isSelected
        ? 'bg-cyan-400/20 text-cyan-400 border border-cyan-400'
        : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-300'
    }`;
  };

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">Choose Your AI Models</h2>
        <p className="text-gray-300">
          Select from preset combinations or customize your model selection
        </p>
      </div>

      {/* Preset Selection */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-cyan-400">Quick Selection</h3>
        <div className="grid gap-3 md:grid-cols-3">
          <button
            onClick={() => handlePresetSelect('premium')}
            className={getPresetButtonClass('premium')}
          >
            <div className="text-center">
              <div className="text-sm opacity-80">Premium</div>
              <div className="text-xs mt-1">Best Quality</div>
            </div>
          </button>

          <button
            onClick={() => handlePresetSelect('speed')}
            className={getPresetButtonClass('speed')}
          >
            <div className="text-center">
              <div className="text-sm opacity-80">Speed</div>
              <div className="text-xs mt-1">Fast Results</div>
            </div>
          </button>

          <button
            onClick={() => handlePresetSelect('budget')}
            className={getPresetButtonClass('budget')}
          >
            <div className="text-center">
              <div className="text-sm opacity-80">Budget</div>
              <div className="text-xs mt-1">Cost Effective</div>
            </div>
          </button>
        </div>
      </div>

      {/* Manual Selection */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-cyan-400">Manual Selection</h3>
          {selectionMode === 'custom' && (
            <Badge className="bg-purple-500/20 text-purple-400 border-purple-400">
              Custom Mode
            </Badge>
          )}
        </div>

        <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-600">
          <p className="text-sm text-gray-400 mb-4">
            Select individual models for your analysis. Each model brings unique strengths and capabilities.
          </p>

          <div className="grid gap-2 md:grid-cols-2 lg:grid-cols-3">
            {modelSelection.availableModels.map(model => (
              <button
                key={model}
                onClick={() => handleModelToggle(model)}
                className={getModelButtonClass(model)}
              >
                <div className="flex items-center justify-between">
                  <span>{model}</span>
                  {selectedModels.includes(model) && (
                    <div className="w-2 h-2 bg-cyan-400 rounded-full"></div>
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Selection Summary */}
      {selectedModels.length > 0 && (
        <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-600">
          <h4 className="text-sm font-semibold text-white mb-3">
            Selected Models ({selectedModels.length})
          </h4>
          <div className="flex flex-wrap gap-2">
            {selectedModels.map(model => (
              <Badge
                key={model}
                className="bg-cyan-400/20 text-cyan-400 border-cyan-400"
              >
                {model}
                <button
                  onClick={() => handleModelToggle(model)}
                  className="ml-2 text-cyan-400 hover:text-cyan-300"
                >
                  ×
                </button>
              </Badge>
            ))}
          </div>

          {selectionMode !== 'custom' && (
            <p className="text-xs text-gray-400 mt-2">
              Using {selectionMode} preset • Click individual models to customize
            </p>
          )}
        </div>
      )}

      {/* Model Information */}
      <div className="bg-blue-900/20 p-4 rounded-lg border border-blue-400/30">
        <h4 className="text-sm font-semibold text-blue-400 mb-2">💡 Model Selection Tips</h4>
        <ul className="text-sm text-gray-300 space-y-1">
          <li>• <strong>Premium:</strong> Best for complex analysis requiring high accuracy</li>
          <li>• <strong>Speed:</strong> Ideal when you need quick results without sacrificing quality</li>
          <li>• <strong>Budget:</strong> Cost-effective option for straightforward tasks</li>
          <li>• <strong>Custom:</strong> Mix and match models based on your specific needs</li>
        </ul>
      </div>
    </div>
  );
}