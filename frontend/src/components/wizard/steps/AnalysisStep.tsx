import React, { useState } from 'react';

interface AnalysisStepProps {
  onNext: (multiplier: string) => void;
}

export const AnalysisStep: React.FC<AnalysisStepProps> = ({ onNext }) => {
  const [multiplier, setMultiplier] = useState('standard');

  const handleNext = () => {
    onNext(multiplier);
  };

  return (
    <div className="analysis-step">
      <h2>UltrAI Multiplier</h2>
      <div className="multiplier-options">
        <label>
          <input
            type="radio"
            value="standard"
            checked={multiplier === 'standard'}
            onChange={(e) => setMultiplier(e.target.value)}
          />
          Standard
        </label>
        <label>
          <input
            type="radio"
            value="enhanced"
            checked={multiplier === 'enhanced'}
            onChange={(e) => setMultiplier(e.target.value)}
          />
          Enhanced
        </label>
        <label>
          <input
            type="radio"
            value="maximum"
            checked={multiplier === 'maximum'}
            onChange={(e) => setMultiplier(e.target.value)}
          />
          Maximum
        </label>
      </div>
      <button onClick={handleNext}>Next</button>
    </div>
  );
};