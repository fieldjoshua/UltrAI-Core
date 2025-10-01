import React from 'react';
import { useModelSelection, ModelType, SelectionMode } from '../../../hooks/useModelSelection';

interface ModelStepProps {
  onNext: (selectedModels: ModelType[], selectionMode: SelectionMode) => void;
  onBack?: () => void;
}

const MODEL_DISPLAY_NAMES: Record<ModelType, string> = {
  'gpt-4': 'GPT-4',
  'claude-3-opus': 'Claude 3 Opus',
  'gemini-1.5-pro': 'Gemini 1.5 Pro',
  'gpt-4o-mini': 'GPT-4o Mini',
  'claude-3-haiku': 'Claude 3 Haiku',
  'gpt-3.5-turbo': 'GPT-3.5 Turbo',
};

const PRESET_LABELS: Record<SelectionMode, string> = {
  premium: 'Premium',
  speed: 'Speed',
  budget: 'Budget',
  custom: 'Custom',
};

export function ModelStep({ onNext, onBack }: ModelStepProps) {
  const {
    selectedModels,
    selectionMode,
    selectPreset,
    toggleModel,
    isModelSelected,
  } = useModelSelection();

  const handleNext = () => {
    if (selectedModels.length > 0) {
      onNext(selectedModels, selectionMode);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && selectedModels.length > 0) {
      handleNext();
    }
  };

  return (
    <div className="model-step">
      <div className="model-content">
        <h2 className="model-title">Select AI Models</h2>
        <p className="model-description">
          Choose which AI models to use for your request. Each preset offers different capabilities and costs.
        </p>

        {/* Preset Selection */}
        <div className="model-presets">
          <h3 className="model-presets-title">Quick Select</h3>
          <div className="model-preset-buttons">
            {(['premium', 'speed', 'budget'] as SelectionMode[]).map(preset => (
              <button
                key={preset}
                className={`model-preset-button ${selectionMode === preset ? 'active' : ''}`}
                onClick={() => selectPreset(preset)}
              >
                {PRESET_LABELS[preset]}
              </button>
            ))}
          </div>
        </div>

        {/* Model Selection */}
        <div className="model-selection">
          <h3 className="model-selection-title">Available Models</h3>
          <div className="model-list">
            {(Object.keys(MODEL_DISPLAY_NAMES) as ModelType[]).map(model => (
              <label key={model} className="model-item">
                <input
                  type="checkbox"
                  checked={isModelSelected(model)}
                  onChange={() => toggleModel(model)}
                  className="model-checkbox"
                />
                <div className="model-info">
                  <span className="model-name">{MODEL_DISPLAY_NAMES[model]}</span>
                  <span className="model-id">{model}</span>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div className="model-summary">
          <div className="model-summary-text">
            {selectedModels.length} model{selectedModels.length !== 1 ? 's' : ''} selected
            {selectionMode !== 'custom' && ` (${PRESET_LABELS[selectionMode]} preset)`}
          </div>
        </div>

        <div className="model-actions">
          {onBack && (
            <button className="model-back-button" onClick={onBack}>
              Back
            </button>
          )}
          <button
            className="model-next-button"
            onClick={handleNext}
            onKeyPress={handleKeyPress}
            disabled={selectedModels.length === 0}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}