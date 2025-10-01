import React from 'react';
import { Button } from '../../Button';
import { Radio } from '../../Radio';

export type AnalysisMultiplier = '1x' | '2x' | '3x' | '5x';

interface AnalysisStepProps {
  multiplier: AnalysisMultiplier;
  onMultiplierChange: (multiplier: AnalysisMultiplier) => void;
  onNext: () => void;
  onBack: () => void;
}

const MULTIPLIER_OPTIONS = [
  {
    value: '1x' as AnalysisMultiplier,
    label: 'Standard (1x)',
    description: 'Balanced analysis with standard processing',
    details: 'Single model analysis • Standard response time • Cost-effective',
    recommended: false
  },
  {
    value: '2x' as AnalysisMultiplier,
    label: 'Enhanced (2x)',
    description: 'Deeper analysis with enhanced processing',
    details: 'Dual model analysis • Detailed insights • Moderate cost',
    recommended: true
  },
  {
    value: '3x' as AnalysisMultiplier,
    label: 'Advanced (3x)',
    description: 'Comprehensive analysis with advanced features',
    details: 'Triple model analysis • Advanced reasoning • Higher cost',
    recommended: false
  },
  {
    value: '5x' as AnalysisMultiplier,
    label: 'Ultra (5x)',
    description: 'Maximum analysis power and depth',
    details: 'Multi-model orchestration • Maximum insights • Premium cost',
    recommended: false
  }
];

export function AnalysisStep({ multiplier, onMultiplierChange, onNext, onBack }: AnalysisStepProps) {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-cyber-green mb-2">
          Choose Your Analysis Power
        </h2>
        <p className="text-gray-300">
          Select the UltrAI multiplier for your analysis intensity
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {MULTIPLIER_OPTIONS.map((option) => (
          <div
            key={option.value}
            className={`relative p-6 rounded-lg border-2 transition-all duration-200 cursor-pointer group ${
              multiplier === option.value
                ? 'border-cyber-green bg-cyber-green/10'
                : 'border-gray-600 hover:border-gray-400 hover:bg-gray-700/30'
            }`}
            onClick={() => onMultiplierChange(option.value)}
          >
            {option.recommended && (
              <div className="absolute -top-2 -right-2 bg-cyber-green text-black text-xs font-bold px-2 py-1 rounded-full">
                RECOMMENDED
              </div>
            )}

            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <Radio
                  checked={multiplier === option.value}
                  onChange={() => onMultiplierChange(option.value)}
                />
                <h3 className="text-lg font-semibold text-white">{option.label}</h3>
              </div>

              <p className="text-gray-300">{option.description}</p>

              <div className="bg-gray-800/50 rounded p-3 text-sm">
                <div className="text-gray-400 mb-1">Includes:</div>
                <div className="text-gray-200">{option.details}</div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-gray-600">
                <span className="text-cyber-green font-semibold">
                  {option.value} UltrAI Power
                </span>
                <div className="flex space-x-1">
                  {Array.from({ length: parseInt(option.value) }, (_, i) => (
                    <div
                      key={i}
                      className="w-2 h-2 bg-cyber-green rounded-full"
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="bg-blue-900/20 border border-blue-500/30 rounded-lg p-4">
        <h3 className="font-semibold text-blue-400 mb-2">💡 Analysis Power Explained</h3>
        <div className="text-sm text-gray-300 space-y-2">
          <p>
            <strong>Higher multipliers</strong> use multiple AI models working together for more comprehensive analysis,
            but take longer and cost more.
          </p>
          <p>
            <strong>Lower multipliers</strong> use single models for faster, cost-effective results.
          </p>
        </div>
      </div>

      <div className="flex justify-between pt-6">
        <Button
          onClick={onBack}
          variant="outline"
          className="border-gray-400 text-gray-400 hover:bg-gray-400/10"
        >
          Back
        </Button>
        <Button
          onClick={onNext}
          className="bg-cyber-green hover:bg-cyber-green/80 text-black"
        >
          Continue
        </Button>
      </div>
    </div>
  );
}