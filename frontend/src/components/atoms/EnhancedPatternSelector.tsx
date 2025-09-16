import React, { useState } from 'react';
import { Card } from '../ui/card';
import { ChevronDown, ChevronUp, Info } from 'lucide-react';

export interface PatternConfigOption {
  id: string;
  name: string;
  type: 'boolean' | 'select' | 'range';
  default: any;
  options?: any[];
}

export interface AnalysisPattern {
  id: string;
  name: string;
  description: string;
  useCases: string[];
  configOptions?: PatternConfigOption[];
}

export interface PatternSelectorProps {
  availablePatterns: AnalysisPattern[];
  selectedPattern: string;
  onPatternChange: (patternId: string) => void;
  isLoading: boolean;
  error?: Error;
}

export const EnhancedPatternSelector: React.FC<PatternSelectorProps> = ({
  availablePatterns,
  selectedPattern,
  onPatternChange,
  isLoading,
  error,
}) => {
  const [expandedDetail, setExpandedDetail] = useState<string | null>(null);

  const toggleDetails = (patternId: string) => {
    if (expandedDetail === patternId) {
      setExpandedDetail(null);
    } else {
      setExpandedDetail(patternId);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="animate-pulse">
          <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-32 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
        Error loading analysis patterns: {error.message}
      </div>
    );
  }

  if (availablePatterns.length === 0) {
    return (
      <div className="p-4 bg-gray-50 border border-gray-200 rounded-md text-gray-500">
        No analysis patterns available.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="text-base font-medium mb-2">Select Analysis Pattern</div>
      <p className="text-sm text-gray-600 mb-4">
        Choose how the models should collaborate on your analysis. Each pattern
        represents a different approach to working with multiple AI models.
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {availablePatterns.map(pattern => {
          const isSelected = selectedPattern === pattern.id;
          const isExpanded = expandedDetail === pattern.id;

          return (
            <Card
              key={pattern.id}
              className={`
                overflow-hidden transition-all duration-200
                ${isSelected ? 'ring-2 ring-blue-500' : 'hover:border-gray-300'}
              `}
            >
              {/* Pattern header */}
              <div
                className={`
                  p-4 cursor-pointer
                  ${isSelected ? 'bg-blue-50 border-blue-100' : 'bg-white'}
                `}
                onClick={() => onPatternChange(pattern.id)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex items-center space-x-3">
                    <div className="flex items-center h-5">
                      <input
                        type="radio"
                        checked={isSelected}
                        onChange={() => onPatternChange(pattern.id)}
                        className="h-4 w-4 text-blue-600 border-gray-300 focus:ring-blue-500"
                        aria-labelledby={`pattern-${pattern.id}-label`}
                      />
                    </div>
                    <div className="flex-1">
                      <h3
                        id={`pattern-${pattern.id}-label`}
                        className="text-lg font-medium text-gray-900"
                      >
                        {pattern.name}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        {pattern.description}
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={e => {
                      e.stopPropagation();
                      toggleDetails(pattern.id);
                    }}
                    className="ml-2 text-gray-400 hover:text-gray-500"
                    aria-label={isExpanded ? 'Hide details' : 'Show details'}
                  >
                    {isExpanded ? (
                      <ChevronUp className="h-5 w-5" />
                    ) : (
                      <ChevronDown className="h-5 w-5" />
                    )}
                  </button>
                </div>
              </div>

              {/* Pattern details */}
              {isExpanded && (
                <div className="px-4 py-3 bg-gray-50 border-t border-gray-100">
                  {pattern.useCases.length > 0 && (
                    <div className="mb-3">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">
                        Best used for:
                      </h4>
                      <ul className="space-y-1">
                        {pattern.useCases.map((useCase, index) => (
                          <li
                            key={index}
                            className="text-sm text-gray-600 flex items-start"
                          >
                            <span className="text-blue-500 mr-2">•</span>
                            {useCase}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {pattern.configOptions &&
                    pattern.configOptions.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-700 mb-2">
                          Configuration options:
                        </h4>
                        <div className="space-y-2">
                          {pattern.configOptions.map(option => (
                            <div key={option.id} className="flex items-center">
                              <div className="text-sm text-gray-600">
                                {option.name}:
                              </div>
                              {option.type === 'boolean' && (
                                <label className="inline-flex items-center ml-3">
                                  <input
                                    type="checkbox"
                                    className="rounded text-blue-600"
                                    defaultChecked={option.default}
                                  />
                                </label>
                              )}
                              {option.type === 'select' && option.options && (
                                <select
                                  className="ml-2 text-sm border-gray-300 rounded-md"
                                  defaultValue={option.default}
                                >
                                  {option.options.map((opt, i) => (
                                    <option key={i} value={opt.value || opt}>
                                      {opt.label || opt}
                                    </option>
                                  ))}
                                </select>
                              )}
                              {option.type === 'range' && (
                                <input
                                  type="range"
                                  className="ml-2"
                                  defaultValue={option.default}
                                  min={option.options?.[0] || 0}
                                  max={option.options?.[1] || 100}
                                />
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* Comparison tooltip */}
      <div className="mt-6 text-sm flex items-center text-gray-500">
        <Info className="h-4 w-4 mr-1" />
        <span>
          Not sure which pattern to choose? The "Gut Check Analysis" pattern is
          a good starting point for most analyses.
        </span>
      </div>
    </div>
  );
};

export default EnhancedPatternSelector;
