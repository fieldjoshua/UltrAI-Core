import React from 'react';
import { Label } from '../ui/label'; // Adjust path
import { Checkbox } from '../ui/checkbox'; // Adjust path
import { Button } from '../ui/button'; // Adjust path

interface ModelSelectionStepProps {
  availableModels: string[];
  selectedLLMs: string[];
  ultraLLM: string | null;
  prices: { [key: string]: number };
  isProcessing: boolean;
  isOffline: boolean;
  onLLMChange: (id: string) => void;
  onUltraChange: (id: string) => void;
}

const ModelSelectionStep: React.FC<ModelSelectionStepProps> = ({
  availableModels,
  selectedLLMs,
  ultraLLM,
  prices,
  isProcessing,
  isOffline,
  onLLMChange,
  onUltraChange,
}) => {
  return (
    <div className="space-y-4 fadeIn">
      <div className="border-2 border-cyan-700 rounded-lg p-6 bg-black/50 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-900/20 to-purple-900/20"></div>
        <div className="relative z-10">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 rounded-full bg-cyan-700 flex items-center justify-center mr-3 text-white font-bold">
              3 {/* Adjusted step number for context within this component */}
            </div>
            <h2 className="text-2xl font-bold text-cyan-400">
              Select AI models
            </h2>
          </div>
          <p className="text-cyan-100 mb-4">
            Choose which AI models will analyze your query. Each model brings
            unique strengths and perspectives. Select one as the "Ultra" model
            to synthesize the final result.
          </p>

          <div className="space-y-2">
            <Label className="text-lg text-cyan-200">Available AI Models</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-2">
              {availableModels.map(model => {
                const isSelected = selectedLLMs.includes(model);
                const isUltra = ultraLLM === model;

                return (
                  <div
                    key={model}
                    className={`
                                            border rounded-lg p-4 cursor-pointer transition-all
                                            ${
                                              isSelected
                                                ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                                : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                                            }
                                            ${isUltra ? 'ring-2 ring-purple-500' : ''}
                                        `}
                    onClick={() => onLLMChange(model)}
                  >
                    <div className="flex justify-between items-center">
                      <div className="flex items-center gap-2">
                        <Checkbox
                          checked={isSelected}
                          onCheckedChange={() => onLLMChange(model)}
                          disabled={isProcessing || isOffline}
                          className="data-[state=checked]:bg-blue-600"
                          aria-label={`Select model ${model}`}
                        />
                        <span className="font-medium text-gray-800 dark:text-gray-200">
                          {model.charAt(0).toUpperCase() + model.slice(1)}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500 dark:text-gray-400">
                        ${prices[model]?.toFixed(4)} / 1K tokens
                      </div>
                    </div>

                    <div className="mt-4 flex justify-between items-center">
                      <button
                        onClick={e => {
                          e.stopPropagation(); // Prevent triggering the outer div's onClick
                          onUltraChange(model);
                        }}
                        disabled={!isSelected || isProcessing || isOffline}
                        className={`
                                                    text-xs font-medium px-3 py-1 rounded-full
                                                    ${
                                                      isUltra
                                                        ? 'bg-purple-600 text-white'
                                                        : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-purple-200'
                                                    }
                                                    ${
                                                      !isSelected
                                                        ? 'opacity-50 cursor-not-allowed'
                                                        : ''
                                                    }
                                                `}
                        aria-label={`Set ${model} as Ultra Model`}
                      >
                        {isUltra ? 'Ultra Model ✓' : 'Set as Ultra Model'}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
      {/* PricingDisplay and Navigation Buttons are handled by the parent component */}
    </div>
  );
};

export default ModelSelectionStep;
