import React from 'react';
import { Slider } from '../../ui/Slider';

export type AnalysisLevel = 'basic' | 'standard' | 'advanced' | 'comprehensive';

export interface AnalysisConfig {
  level: AnalysisLevel;
  depth: number; // 1-10 scale
  breadth: number; // 1-10 scale
  creativity: number; // 1-10 scale
  enableReasoning: boolean;
  enableMultiPerspective: boolean;
  enablePatternRecognition: boolean;
}

interface AnalysisStepProps {
  config: AnalysisConfig;
  onConfigChange: (config: AnalysisConfig) => void;
}

const ANALYSIS_LEVELS = {
  basic: {
    name: 'Basic',
    description: 'Quick analysis with essential insights',
    depth: 3,
    breadth: 4,
    creativity: 2,
  },
  standard: {
    name: 'Standard',
    description: 'Balanced analysis with good depth and coverage',
    depth: 6,
    breadth: 6,
    creativity: 4,
  },
  advanced: {
    name: 'Advanced',
    description: 'Deep analysis with comprehensive insights',
    depth: 8,
    breadth: 7,
    creativity: 6,
  },
  comprehensive: {
    name: 'Comprehensive',
    description: 'Maximum depth analysis with full intelligence',
    depth: 10,
    breadth: 9,
    creativity: 8,
  },
} as const;

export function AnalysisStep({ config, onConfigChange }: AnalysisStepProps) {
  const handleLevelChange = (level: AnalysisLevel) => {
    const preset = ANALYSIS_LEVELS[level];
    onConfigChange({
      ...config,
      level,
      depth: preset.depth,
      breadth: preset.breadth,
      creativity: preset.creativity,
    });
  };

  const handleSliderChange = (key: keyof AnalysisConfig, value: number) => {
    onConfigChange({
      ...config,
      [key]: value,
    });
  };

  const handleToggleChange = (key: keyof AnalysisConfig) => {
    onConfigChange({
      ...config,
      [key]: !config[key],
    });
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">UltrAI Intelligence Multiplier</h2>
        <p className="text-gray-300">
          Configure the depth and sophistication of your AI analysis
        </p>
      </div>

      {/* Analysis Level Selection */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-cyan-400">Analysis Level</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          {Object.entries(ANALYSIS_LEVELS).map(([key, level]) => (
            <button
              key={key}
              onClick={() => handleLevelChange(key as AnalysisLevel)}
              className={`p-4 rounded-lg border-2 text-left transition-all ${
                config.level === key
                  ? 'border-cyan-400 bg-cyan-400/10 text-white'
                  : 'border-gray-600 bg-gray-800/50 text-gray-300 hover:border-gray-500'
              }`}
            >
              <div className="font-semibold">{level.name}</div>
              <div className="text-sm mt-1 opacity-80">{level.description}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Fine-tuned Controls */}
      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-cyan-400">Fine-tune Analysis</h3>

        <div className="grid gap-6 md:grid-cols-3">
          {/* Depth */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-white">
              Analysis Depth: {config.depth}/10
            </label>
            <Slider
              value={config.depth}
              onChange={(value) => handleSliderChange('depth', value)}
              min={1}
              max={10}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-gray-400">
              How detailed and thorough the analysis should be
            </p>
          </div>

          {/* Breadth */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-white">
              Coverage Breadth: {config.breadth}/10
            </label>
            <Slider
              value={config.breadth}
              onChange={(value) => handleSliderChange('breadth', value)}
              min={1}
              max={10}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-gray-400">
              How many different aspects and perspectives to cover
            </p>
          </div>

          {/* Creativity */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-white">
              Creative Thinking: {config.creativity}/10
            </label>
            <Slider
              value={config.creativity}
              onChange={(value) => handleSliderChange('creativity', value)}
              min={1}
              max={10}
              step={1}
              className="w-full"
            />
            <p className="text-xs text-gray-400">
              How innovative and creative the analysis approach should be
            </p>
          </div>
        </div>
      </div>

      {/* Advanced Features */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-cyan-400">Advanced Features</h3>
        <div className="space-y-3">
          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={config.enableReasoning}
              onChange={() => handleToggleChange('enableReasoning')}
              className="w-4 h-4 text-cyan-400 bg-gray-800 border-gray-600 rounded focus:ring-cyan-400"
            />
            <div>
              <span className="text-white font-medium">Chain-of-Thought Reasoning</span>
              <p className="text-sm text-gray-400">
                Enable step-by-step reasoning for complex problem-solving
              </p>
            </div>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={config.enableMultiPerspective}
              onChange={() => handleToggleChange('enableMultiPerspective')}
              className="w-4 h-4 text-cyan-400 bg-gray-800 border-gray-600 rounded focus:ring-cyan-400"
            />
            <div>
              <span className="text-white font-medium">Multi-Perspective Analysis</span>
              <p className="text-sm text-gray-400">
                Analyze from multiple viewpoints and stakeholder perspectives
              </p>
            </div>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer">
            <input
              type="checkbox"
              checked={config.enablePatternRecognition}
              onChange={() => handleToggleChange('enablePatternRecognition')}
              className="w-4 h-4 text-cyan-400 bg-gray-800 border-gray-600 rounded focus:ring-cyan-400"
            />
            <div>
              <span className="text-white font-medium">Pattern Recognition</span>
              <p className="text-sm text-gray-400">
                Identify patterns, trends, and underlying structures
              </p>
            </div>
          </label>
        </div>
      </div>

      {/* Intelligence Summary */}
      <div className="bg-gradient-to-r from-cyan-500/10 to-purple-500/10 p-6 rounded-lg border border-cyan-400/30">
        <h4 className="text-lg font-semibold text-white mb-3">Intelligence Configuration Summary</h4>
        <div className="grid gap-2 md:grid-cols-2 text-sm">
          <div className="text-gray-300">
            <span className="text-cyan-400">Level:</span> {ANALYSIS_LEVELS[config.level].name}
          </div>
          <div className="text-gray-300">
            <span className="text-cyan-400">Depth:</span> {config.depth}/10
          </div>
          <div className="text-gray-300">
            <span className="text-cyan-400">Breadth:</span> {config.breadth}/10
          </div>
          <div className="text-gray-300">
            <span className="text-cyan-400">Creativity:</span> {config.creativity}/10
          </div>
          <div className="text-gray-300 md:col-span-2">
            <span className="text-cyan-400">Features:</span>{' '}
            {[
              config.enableReasoning && 'Reasoning',
              config.enableMultiPerspective && 'Multi-Perspective',
              config.enablePatternRecognition && 'Pattern Recognition'
            ].filter(Boolean).join(', ') || 'None'}
          </div>
        </div>
      </div>
    </div>
  );
}