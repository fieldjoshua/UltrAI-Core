/**
 * PatternSelector Component
 *
 * A reusable component for selecting analysis patterns. This component
 * allows users to choose from different analysis patterns that determine
 * how multiple LLMs will collaborate on the analysis.
 */

import React from 'react';
import { Label } from '../ui/label';
import { Card } from '../ui/card';

export interface AnalysisPattern {
  id: string;
  name: string;
  description: string;
  stages: string[];
  recommendedFor?: string[];
}

export interface PatternSelectorProps {
  /**
   * List of available analysis patterns
   */
  patterns: AnalysisPattern[];

  /**
   * Currently selected pattern ID
   */
  selectedPattern: string | null;

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
   * Callback when pattern selection changes
   * @param patternId The ID of the selected pattern
   */
  onPatternChange: (patternId: string) => void;
}

export const PatternSelector: React.FC<PatternSelectorProps> = ({
  patterns,
  selectedPattern,
  disabled = false,
  isLoading = false,
  onPatternChange,
}) => {
  return (
    <div className="space-y-4">
      <Label className="text-lg">Analysis Pattern</Label>
      <p className="text-sm text-gray-500 dark:text-gray-400">
        Choose how the models should collaborate on your analysis. Each pattern
        represents a different approach to intelligence multiplication.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {patterns.map(pattern => {
          const isSelected = selectedPattern === pattern.id;
          const isDisabled = disabled || isLoading;

          return (
            <Card
              key={pattern.id}
              className={`
                p-4 cursor-pointer transition-all
                ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : ''
                }
                ${isDisabled ? 'opacity-50 cursor-not-allowed' : ''}
              `}
              onClick={() => !isDisabled && onPatternChange(pattern.id)}
            >
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <input
                    type="radio"
                    name="pattern"
                    checked={isSelected}
                    onChange={() => !isDisabled && onPatternChange(pattern.id)}
                    disabled={isDisabled}
                    className="h-4 w-4 text-blue-600"
                    aria-label={`Select ${pattern.name} pattern`}
                  />
                  <span className="font-medium text-gray-800 dark:text-gray-200">
                    {pattern.name}
                  </span>
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {pattern.description}
                </p>
                {pattern.recommendedFor &&
                  pattern.recommendedFor.length > 0 && (
                    <div className="mt-2">
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Recommended for:
                      </p>
                      <ul className="mt-1 text-xs text-gray-600 dark:text-gray-300">
                        {pattern.recommendedFor.map(useCase => (
                          <li key={useCase} className="flex items-center gap-1">
                            <span className="h-1 w-1 rounded-full bg-blue-500" />
                            {useCase}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Stages: {pattern.stages.join(' → ')}
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
