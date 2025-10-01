import React from 'react';

interface IntroStepProps {
  onNext: () => void;
}

export function IntroStep({ onNext }: IntroStepProps) {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onNext();
    }
  };

  return (
    <div className="intro-step">
      <div className="intro-content">
        <h1 className="intro-title">Welcome to CyberWizard</h1>
        <p className="intro-description">
          Your intelligent assistant for complex tasks and analysis.
          Let's get started by understanding what you need help with.
        </p>
        <div className="intro-actions">
          <button
            className="intro-enter-button"
            onClick={onNext}
            onKeyPress={handleKeyPress}
            autoFocus
          >
            Enter CyberWizard
          </button>
        </div>
      </div>
    </div>
  );
}