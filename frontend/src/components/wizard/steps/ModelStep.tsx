import React from 'react';
import { useModelSelection } from '../../../hooks/useModelSelection';

interface Model {
  name: string;
  provider: string;
  cost_per_1k_tokens?: number;
}

interface ModelStepProps {
  availableModels: Model[];
  onSelectionChange: (models: string[]) => void;
}

export default function ModelStep({ availableModels, onSelectionChange }: ModelStepProps) {
  const { selectedModels, selectionMode, selectPreset, toggleModel } = useModelSelection();

  React.useEffect(() => {
    onSelectionChange(selectedModels);
  }, [selectedModels, onSelectionChange]);

  const [showManual, setShowManual] = React.useState(false);

  const handlePreset = (mode: 'premium' | 'speed' | 'budget') => {
    selectPreset(mode);
    setShowManual(false);
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Model selection</h2>
      <p className="text-gray-400 mb-8">Which AI models should work on this?</p>
      
      {!showManual ? (
        <div className="space-y-4">
          <button
            onClick={() => handlePreset('premium')}
            className={`w-full p-4 rounded-lg border-2 transition-all ${
              selectionMode === 'premium'
                ? 'border-purple-500 bg-purple-500/20'
                : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🎯</span>
              <div className="flex-1 text-left">
                <div className="font-semibold">Premium</div>
                <div className="text-sm text-gray-400">GPT-4 + Claude Opus, $1-2 per query</div>
              </div>
            </div>
          </button>

          <button
            onClick={() => handlePreset('speed')}
            className={`w-full p-4 rounded-lg border-2 transition-all ${
              selectionMode === 'speed'
                ? 'border-purple-500 bg-purple-500/20'
                : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">⏩</span>
              <div className="flex-1 text-left">
                <div className="font-semibold">Speed</div>
                <div className="text-sm text-gray-400">Quick results, $0.50-1 per query</div>
              </div>
            </div>
          </button>

          <button
            onClick={() => handlePreset('budget')}
            className={`w-full p-4 rounded-lg border-2 transition-all ${
              selectionMode === 'budget'
                ? 'border-purple-500 bg-purple-500/20'
                : 'border-gray-700 hover:border-gray-600'
            }`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">💲</span>
              <div className="flex-1 text-left">
                <div className="font-semibold">Budget Mode</div>
                <div className="text-sm text-gray-400">Fast models, $0.25-0.50 per query</div>
              </div>
            </div>
          </button>

          <button
            onClick={() => setShowManual(true)}
            className="w-full p-4 rounded-lg border-2 border-gray-700 hover:border-gray-600 transition-all"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🛠️</span>
              <div className="flex-1 text-left">
                <div className="font-semibold">Manual: Choose Models</div>
                <div className="text-sm text-gray-400">Choose specific models</div>
              </div>
            </div>
          </button>
        </div>
      ) : (
        <div>
          <button
            onClick={() => setShowManual(false)}
            className="mb-4 text-sm text-purple-400 hover:text-purple-300"
          >
            ← Back to presets
          </button>
          
          <div className="space-y-2">
            <h3 className="font-semibold mb-3">Select Models</h3>
            {availableModels.map((model) => (
              <label
                key={model.name}
                className="flex items-center gap-3 p-3 rounded-lg border border-gray-700 hover:border-gray-600 cursor-pointer"
              >
                <input
                  type="checkbox"
                  checked={selectedModels.includes(model.name)}
                  onChange={() => toggleModel(model.name)}
                  className="w-4 h-4"
                />
                <span className="flex-1">{model.name}</span>
                <span className="text-sm text-gray-500">{model.provider}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      {selectedModels.length > 0 && (
        <div className="mt-6 p-4 bg-gray-800/50 rounded-lg">
          <div className="text-sm text-gray-400 mb-2">Selected models ({selectedModels.length}):</div>
          <div className="text-sm">{selectedModels.join(', ')}</div>
        </div>
      )}
    </div>
  );
}
