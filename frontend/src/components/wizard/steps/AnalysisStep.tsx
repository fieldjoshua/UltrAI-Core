import React, { useState } from 'react';

interface AnalysisStepProps {
  onNext: (analysisLevel: string) => void;
  onBack?: () => void;
}

const ANALYSIS_OPTIONS = [
  {
    id: 'basic',
    title: 'Basic Analysis',
    description: 'Standard processing with single model response',
    multiplier: '1x',
    recommended: false,
  },
  {
    id: 'enhanced',
    title: 'Enhanced Analysis',
    description: 'Multi-model processing with enhanced reasoning',
    multiplier: '2x',
    recommended: true,
  },
  {
    id: 'comprehensive',
    title: 'Comprehensive Analysis',
    description: 'Full UltrAI orchestration with maximum intelligence',
    multiplier: '3x',
    recommended: false,
  },
];

export function AnalysisStep({ onNext, onBack }: AnalysisStepProps) {
  const [selectedLevel, setSelectedLevel] = useState<string>('enhanced');

  const handleNext = () => {
    onNext(selectedLevel);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleNext();
    }
  };

  return (
    <div className="analysis-step">
      <div className="analysis-content">
        <h2 className="analysis-title">Choose Analysis Level</h2>
        <p className="analysis-description">
          Select the depth of analysis and processing power for your request.
        </p>

        <div className="analysis-options">
          {ANALYSIS_OPTIONS.map(option => (
            <label key={option.id} className="analysis-option">
              <input
                type="radio"
                name="analysisLevel"
                value={option.id}
                checked={selectedLevel === option.id}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="analysis-radio"
              />
              <div className="analysis-option-content">
                <div className="analysis-option-header">
                  <span className="analysis-option-title">{option.title}</span>
                  {option.recommended && (
                    <span className="analysis-recommended-badge">Recommended</span>
                  )}
                </div>
                <p className="analysis-option-description">{option.description}</p>
                <div className="analysis-multiplier">
                  UltrAI Multiplier: <strong>{option.multiplier}</strong>
                </div>
              </div>
            </label>
          ))}
        </div>

        <div className="analysis-actions">
          {onBack && (
            <button className="analysis-back-button" onClick={onBack}>
              Back
            </button>
          )}
          <button
            className="analysis-next-button"
            onClick={handleNext}
            onKeyPress={handleKeyPress}
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}