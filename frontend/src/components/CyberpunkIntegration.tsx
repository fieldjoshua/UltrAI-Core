import React from 'react';
import CyberpunkTheme from './CyberpunkTheme';
import PromptInput from './PromptInput';
import LLMSelector from './LLMSelector';
import AnalysisPatternSelector from './AnalysisPatternSelector';
import Button from './Button';

interface CyberpunkIntegrationProps {
  onAnalyze?: () => void;
  cost?: number;
  credit?: number;
}

/**
 * Example integration showing how to wrap existing components with the CyberpunkTheme
 */
const CyberpunkIntegration: React.FC<CyberpunkIntegrationProps> = ({
  onAnalyze,
  cost = 0,
  credit = 100
}) => {
  return (
    <CyberpunkTheme
      billboardTitle="ULTRA AI"
      billboardSubtitle="Multiply Your Intelligence"
      cost={cost}
      credit={credit}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
        {/* Prompt Input Section */}
        <div className="cyber-ui-element cyber-ui-prompt">
          <h3 style={{ color: '#ff00de', marginBottom: '1rem' }}>Your Prompt</h3>
          <PromptInput
            value=""
            onChange={() => {}}
            placeholder="Describe what you want to analyze..."
          />
        </div>

        {/* Model Selection Section */}
        <div className="cyber-ui-element cyber-ui-model">
          <h3 style={{ color: '#00ffff', marginBottom: '1rem' }}>AI Models</h3>
          <LLMSelector
            selectedModels={[]}
            onModelToggle={() => {}}
            availableModels={[
              { id: 'gpt-4', name: 'GPT-4', provider: 'OpenAI' },
              { id: 'claude-3', name: 'Claude 3', provider: 'Anthropic' },
              { id: 'llama-2', name: 'Llama 2', provider: 'Meta' }
            ]}
          />
        </div>

        {/* Analysis Pattern Section */}
        <div className="cyber-ui-element cyber-ui-analysis">
          <h3 style={{ color: '#00ff9f', marginBottom: '1rem' }}>Analysis Pattern</h3>
          <AnalysisPatternSelector
            selectedPattern=""
            onPatternSelect={() => {}}
            patterns={[
              { id: 'deep-dive', name: 'Deep Dive', description: 'Thorough analysis' },
              { id: 'compare', name: 'Compare & Contrast', description: 'Multiple perspectives' },
              { id: 'creative', name: 'Creative Synthesis', description: 'Novel insights' }
            ]}
          />
        </div>

        {/* Analyze Button */}
        <div style={{ textAlign: 'center', marginTop: '2rem' }}>
          <button className="cyber-button" onClick={onAnalyze}>
            MULTIPLY INTELLIGENCE
          </button>
        </div>
      </div>
    </CyberpunkTheme>
  );
};

export default CyberpunkIntegration;