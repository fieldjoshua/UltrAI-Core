/**
 * LLMSelector Component
 *
 * A reusable component for selecting LLM models for analysis. This component
 * allows users to select multiple models and designate one as the "Ultra" model
 * for final synthesis.
 */

import React from 'react';
import { Label } from '../ui/label';
import { Checkbox } from '../ui/checkbox';
import { Card } from '../ui/card';

export interface LLMModel {
  id: string;
  name: string;
  description?: string;
  cost?: number;
  capabilities?: string[];
  status?: 'available' | 'unavailable' | 'loading';
}

export interface LLMSelectorProps {
  /**
   * List of available LLM models
   */
  models: LLMModel[];

  /**
   * Currently selected model IDs
   */
  selectedModels: string[];

  /**
   * ID of the model selected as "Ultra" model
   */
  ultraModel: string | null;

  /**
   * Whether the selector is currently disabled
   * @default false
   */
  disabled?: boolean;

  /**
   * Whether to show loading states
   * @default false
   */
  isLoading?: boolean;

  /**
   * Callback when model selection changes
   * @param modelId The ID of the model that was toggled
   */
  onModelChange: (modelId: string) => void;

  /**
   * Callback when Ultra model changes
   * @param modelId The ID of the model selected as Ultra
   */
  onUltraChange: (modelId: string) => void;
}

export const LLMSelector: React.FC<LLMSelectorProps> = ({
  models,
  selectedModels,
  ultraModel,
  disabled = false,
  isLoading = false,
  onModelChange,
  onUltraChange,
}) => {
  return (
    <div className="space-y-4">
      <Label className="text-lg">Available AI Models</Label>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {models.map(model => {
          const isSelected = selectedModels.includes(model.id);
          const isUltra = ultraModel === model.id;
          const isModelDisabled =
            disabled || isLoading || model.status === 'unavailable';

          return (
            <Card
              key={model.id}
              className={`
                p-4 cursor-pointer transition-all
                ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : ''
                }
                ${isUltra ? 'ring-2 ring-purple-500' : ''}
                ${isModelDisabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
              onClick={() => !isModelDisabled && onModelChange(model.id)}
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <Checkbox
                    checked={isSelected}
                    onCheckedChange={() =>
                      !isModelDisabled && onModelChange(model.id)
                    }
                    disabled={isModelDisabled}
                    className="data-[state=checked]:bg-blue-600"
                    aria-label={`Select model ${model.name}`}
                  />
                  <div>
                    <span className="font-medium text-gray-800 dark:text-gray-200">
                      {model.name}
                    </span>
                    {model.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {model.description}
                      </p>
                    )}
                  </div>
                </div>
                {model.cost !== undefined && (
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    ${model.cost.toFixed(4)} / 1K tokens
                  </div>
                )}
              </div>
              {isSelected && (
                <div className="mt-2 flex justify-end">
                  <button
                    onClick={e => {
                      e.stopPropagation();
                      onUltraChange(model.id);
                    }}
                    disabled={isModelDisabled}
                    className={`
                      text-sm px-2 py-1 rounded
                      ${
                        isUltra
                          ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300'
                          : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                      }
                    `}
                  >
                    {isUltra ? 'Ultra Model' : 'Set as Ultra'}
                  </button>
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
};
