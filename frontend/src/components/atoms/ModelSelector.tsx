import React, { useState, useMemo } from 'react';
import { Label } from '../ui/label';
import { Checkbox } from '../ui/checkbox';
import { Card } from '../ui/card';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';

export interface Model {
  id: string;
  name: string;
  provider: string;
  description?: string;
  capabilities?: string[];
  isAvailable: boolean;
}

export interface ModelSelectorProps {
  availableModels: Model[];
  selectedModels: string[];
  onSelectionChange: (modelIds: string[]) => void;
  isLoading: boolean;
  error?: Error;
  maxSelections?: number;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({
  availableModels,
  selectedModels,
  onSelectionChange,
  isLoading,
  error,
  maxSelections = 5,
}) => {
  // Group models by provider
  const groupedModels = useMemo(() => {
    const groups: Record<string, Model[]> = {};

    availableModels.forEach(model => {
      if (!groups[model.provider]) {
        groups[model.provider] = [];
      }
      groups[model.provider].push(model);
    });

    return groups;
  }, [availableModels]);

  // State for expanded/collapsed provider sections
  const [expanded, setExpanded] = useState<Record<string, boolean>>(() => {
    const initial: Record<string, boolean> = {};
    // Default to expanding all provider groups
    Object.keys(groupedModels).forEach(provider => {
      initial[provider] = true;
    });
    return initial;
  });

  // Toggle model selection
  const toggleModel = (modelId: string) => {
    if (selectedModels.includes(modelId)) {
      // Remove model from selection
      onSelectionChange(selectedModels.filter(id => id !== modelId));
    } else {
      // Add model to selection if under max limit
      if (selectedModels.length < maxSelections) {
        onSelectionChange([...selectedModels, modelId]);
      }
    }
  };

  // Toggle provider expansion
  const toggleProvider = (provider: string) => {
    setExpanded(prev => ({
      ...prev,
      [provider]: !prev[provider],
    }));
  };

  // Select all models in a provider group
  const selectAllInProvider = (provider: string) => {
    const modelIds = groupedModels[provider]
      .filter(model => model.isAvailable)
      .map(model => model.id);

    // Only add models up to max selections
    const currentSelected = [...selectedModels];

    // Remove any currently selected models from this provider
    const filteredSelected = currentSelected.filter(
      id => !modelIds.includes(id)
    );

    // Add as many models as we can from this provider
    const availableSlots = maxSelections - filteredSelected.length;
    const modelsToAdd = modelIds.slice(0, availableSlots);

    onSelectionChange([...filteredSelected, ...modelsToAdd]);
  };

  // Clear all selections from a provider
  const clearProvider = (provider: string) => {
    const modelIds = groupedModels[provider].map(model => model.id);
    onSelectionChange(selectedModels.filter(id => !modelIds.includes(id)));
  };

  // Check if all models in a provider are selected
  const isProviderFullySelected = (provider: string) => {
    const availableModelIds = groupedModels[provider]
      .filter(model => model.isAvailable)
      .map(model => model.id);

    return availableModelIds.every(id => selectedModels.includes(id));
  };

  // Count selected models in a provider
  const countSelectedInProvider = (provider: string) => {
    const modelIds = groupedModels[provider].map(model => model.id);
    return selectedModels.filter(id => modelIds.includes(id)).length;
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-24 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
        Error loading models: {error.message}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <Label className="text-base font-medium">Select AI Models</Label>
        <div className="text-sm text-gray-500">
          {selectedModels.length} of {maxSelections} selected
        </div>
      </div>

      {Object.keys(groupedModels).length === 0 ? (
        <div className="p-4 bg-gray-50 border border-gray-200 rounded-md text-gray-500">
          No models available.
        </div>
      ) : (
        <div className="space-y-4">
          {Object.entries(groupedModels).map(([provider, models]) => (
            <div
              key={provider}
              className="border border-gray-200 rounded-md overflow-hidden"
            >
              {/* Provider header */}
              <div
                className="bg-gray-50 p-3 flex justify-between items-center cursor-pointer"
                onClick={() => toggleProvider(provider)}
              >
                <div className="flex items-center">
                  <div className="font-medium">{provider}</div>
                  <div className="ml-2 text-sm text-gray-500">
                    ({countSelectedInProvider(provider)} of{' '}
                    {models.filter(m => m.isAvailable).length} selected)
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="flex space-x-2">
                    <button
                      onClick={e => {
                        e.stopPropagation();
                        selectAllInProvider(provider);
                      }}
                      className="text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded"
                    >
                      Select All
                    </button>
                    <button
                      onClick={e => {
                        e.stopPropagation();
                        clearProvider(provider);
                      }}
                      className="text-xs px-2 py-1 bg-gray-200 hover:bg-gray-300 rounded"
                    >
                      Clear
                    </button>
                  </div>
                  {expanded[provider] ? (
                    <ChevronUp size={18} />
                  ) : (
                    <ChevronDown size={18} />
                  )}
                </div>
              </div>

              {/* Models in this provider */}
              {expanded[provider] && (
                <div className="p-3 space-y-2 bg-white">
                  {models.map(model => (
                    <div
                      key={model.id}
                      className={`
                        flex items-center p-2 rounded-md
                        ${model.isAvailable ? 'cursor-pointer hover:bg-gray-50' : 'opacity-50 cursor-not-allowed'}
                        ${selectedModels.includes(model.id) ? 'bg-blue-50 border border-blue-100' : ''}
                      `}
                      onClick={() => model.isAvailable && toggleModel(model.id)}
                    >
                      <Checkbox
                        checked={selectedModels.includes(model.id)}
                        onCheckedChange={() =>
                          model.isAvailable && toggleModel(model.id)
                        }
                        disabled={
                          !model.isAvailable ||
                          (selectedModels.length >= maxSelections &&
                            !selectedModels.includes(model.id))
                        }
                        className="mr-3"
                      />
                      <div className="flex-grow">
                        <div className="font-medium">{model.name}</div>
                        {model.description && (
                          <div className="text-sm text-gray-500">
                            {model.description}
                          </div>
                        )}
                      </div>

                      {model.capabilities && model.capabilities.length > 0 && (
                        <div className="tooltip-container relative flex items-center">
                          <Info
                            size={16}
                            className="text-gray-400 cursor-help"
                          />
                          <div className="tooltip absolute bottom-full right-0 mb-2 w-64 p-2 bg-gray-800 text-white text-xs rounded shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-opacity z-10">
                            <div className="font-semibold mb-1">
                              Capabilities:
                            </div>
                            <ul className="list-disc pl-4">
                              {model.capabilities.map((capability, idx) => (
                                <li key={idx}>{capability}</li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Selection limit warning */}
      {selectedModels.length >= maxSelections && (
        <div className="text-sm text-amber-600 bg-amber-50 p-2 rounded-md border border-amber-200">
          Maximum model selection limit reached ({maxSelections}).
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
