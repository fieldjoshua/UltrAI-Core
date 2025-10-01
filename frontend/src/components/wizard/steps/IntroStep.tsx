import React from 'react';

interface IntroStepProps {
  onNext: () => void;
}

export const IntroStep: React.FC<IntroStepProps> = ({ onNext }) => {
  return (
    <div className="intro-step">
      <h1>Welcome to CyberWizard</h1>
      <p>Your journey to advanced AI analysis starts here.</p>
      <button onClick={onNext}>Enter</button>
    </div>
  );
};