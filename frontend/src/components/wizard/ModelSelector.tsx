import React from 'react';
import { useModelSelection, SelectionMode } from '../../hooks/useModelSelection';
import { Button } from '../../ui/Button';
import { Badge } from '../../ui/Badge';

interface ModelSelectorProps {
  selectedModels?: string[];
  selectionMode?: SelectionMode;
  onSelectionChange?: (models: string[], mode: SelectionMode) => void;
  showTitle?: boolean;
  compact?: boolean;
}

export function ModelSelector({
  selectedModels: externalSelectedModels,
  selectionMode: externalSelectionMode,
  onSelectionChange,
  showTitle = true,
  compact = false
}: ModelSelectorProps) {
  const modelSelection = useModelSelection();

  // Use external state if provided, otherwise use internal state
  const selectedModels = externalSelectedModels ?? modelSelection.selectedModels;
  const selectionMode = externalSelectionMode ?? modelSelection.selectionMode;

  const handlePresetSelect = (mode: SelectionMode) => {
    modelSelection.selectPreset(mode);
    if (onSelectionChange) {
      onSelectionChange(modelSelection.selectedModels, mode);
    }
  };

  const handleModelToggle = (model: string) => {
    modelSelection.toggleModel(model);
    if (onSelectionChange) {
      onSelectionChange(modelSelection.selectedModels, modelSelection.selectionMode);
    }
  };

  const getPresetButtonClass = (mode: SelectionMode) => {
    const isSelected = selectionMode === mode;
    return `px-3 py-2 rounded-lg font-medium transition-all duration-200 text-sm ${
      isSelected
        ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white'
        : 'bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white'
    }`;
  };

  const getModelButtonClass = (model: string) => {
    const isSelected = selectedModels.includes(model);
    return `px-2 py-1 rounded text-xs font-medium transition-all duration-200 ${
      isSelected
        ? 'bg-cyan-400/20 text-cyan-400 border border-cyan-400'
        : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-300'
    }`;
  };

  return (
    <div className={`space-y-4 ${compact ? 'space-y-3' : 'space-y-4'}`}>
      {showTitle && (
        <div className="text-center space-y-1">
          <h3 className={`${compact ? 'text-lg' : 'text-xl'} font-bold text-white`}>
            AI Model Selection
          </h3>
          {!compact && (
            <p className="text-sm text-gray-400">
              Choose from presets or customize your selection
            </p>
          )}
        </div>
      )}

      {/* Preset Selection */}
      <div className="space-y-3">
        <div className={`grid gap-2 ${compact ? 'grid-cols-3' : 'md:grid-cols-3'}`}>
          <button
            onClick={() => handlePresetSelect('premium')}
            className={getPresetButtonClass('premium')}
            title="Best quality models for complex analysis"
          >
            {compact ? 'Premium' : 'Premium Quality'}
          </button>

          <button
            onClick={() => handlePresetSelect('speed')}
            className={getPresetButtonClass('speed')}
            title="Fast processing with good quality"
          >
            {compact ? 'Speed' : 'Fast Results'}
          </button>

          <button
            onClick={() => handlePresetSelect('budget')}
            className={getPresetButtonClass('budget')}
            title="Cost-effective option for simple tasks"
          >
            {compact ? 'Budget' : 'Cost Effective'}
          </button>
        </div>
      </div>

      {/* Manual Selection Toggle */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => handlePresetSelect('custom')}
          className={`text-sm transition-all duration-200 ${
            selectionMode === 'custom'
              ? 'text-cyan-400 font-medium'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          {compact ? 'Custom' : 'Manual: Choose Models'}
        </button>

        {selectionMode === 'custom' && (
          <Badge className="bg-purple-500/20 text-purple-400 border-purple-400 text-xs">
            Custom Mode
          </Badge>
        )}
      </div>

      {/* Manual Model Selection */}
      {selectionMode === 'custom' && (
        <div className={`bg-gray-800/50 p-3 rounded-lg border border-gray-600 ${compact ? 'p-2' : 'p-3'}`}>
          <div className={`grid gap-2 ${compact ? 'grid-cols-2' : 'md:grid-cols-3'}`}>
            {modelSelection.availableModels.map(model => (
              <button
                key={model}
                onClick={() => handleModelToggle(model)}
                className={getModelButtonClass(model)}
                title={`Click to ${selectedModels.includes(model) ? 'remove' : 'add'} ${model}`}
              >
                {model}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Selection Summary */}
      {selectedModels.length > 0 && (
        <div className={`bg-gray-800/30 p-2 rounded border border-gray-600 ${compact ? 'p-1 text-xs' : 'p-2'}`}>
          <div className="flex items-center justify-between">
            <span className="text-gray-300">
              {selectedModels.length} model{selectedModels.length !== 1 ? 's' : ''} selected
            </span>
            {selectionMode !== 'custom' && (
              <Badge className="bg-cyan-400/20 text-cyan-400 border-cyan-400 text-xs">
                {selectionMode} preset
              </Badge>
            )}
          </div>
        </div>
      )}
    </div>
  );
}