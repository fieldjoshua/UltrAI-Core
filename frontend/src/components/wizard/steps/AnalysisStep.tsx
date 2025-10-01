import React from 'react';

interface AnalysisOption {
  label: string;
  icon: string;
  description?: string;
  cost?: number;
}

interface AnalysisStepProps {
  options: AnalysisOption[];
  selectedAnalysis: string[];
  onToggle: (analysis: string) => void;
}

export default function AnalysisStep({ options, selectedAnalysis, onToggle }: AnalysisStepProps) {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Analyses</h2>
      <p className="text-gray-400 mb-8">Choose how we should combine and improve your results.</p>
      
      <div className="space-y-4">
        {options.map((option) => {
          const isSelected = selectedAnalysis.includes(option.label);
          const isComingSoon = option.label.includes('Coming soon');
          
          return (
            <button
              key={option.label}
              onClick={() => !isComingSoon && onToggle(option.label)}
              disabled={isComingSoon}
              className={`w-full p-4 rounded-lg border-2 text-left transition-all ${
                isComingSoon
                  ? 'border-gray-800 bg-gray-900/50 opacity-50 cursor-not-allowed'
                  : isSelected
                  ? 'border-purple-500 bg-purple-500/20'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl">{option.icon}</div>
                <div className="flex-1">
                  <div className="font-semibold mb-1">{option.label}</div>
                  {option.description && (
                    <div className="text-sm text-gray-400">{option.description}</div>
                  )}
                </div>
                {option.cost !== undefined && !isComingSoon && (
                  <div className="text-sm text-gray-500">+${option.cost.toFixed(2)}</div>
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
