import React from 'react';
import { useModelSelection, Preset } from '../../../hooks/useModelSelection';

interface ModelStepProps {
  onNext: (models: string[]) => void;
}

export const ModelStep: React.FC<ModelStepProps> = ({ onNext }) => {
  const { selectedModels, selectionMode, selectPreset, toggleModel } = useModelSelection();

  const handleNext = () => {
    onNext(selectedModels);
  };

  return (
    <div className="model-step">
      <h2>Select Models</h2>
      <div className="preset-buttons">
        <button onClick={() => selectPreset('premium')}>Premium</button>
        <button onClick={() => selectPreset('speed')}>Speed</button>
        <button onClick={() => selectPreset('budget')}>Budget</button>
      </div>
      <div className="model-list">
        {selectionMode && (
          <div>
            <h3>Selected Preset: {selectionMode}</h3>
            <ul>
              {selectedModels.map(model => (
                <li key={model}>
                  <label>
                    <input
                      type="checkbox"
                      checked={true}
                      onChange={() => toggleModel(model)}
                    />
                    {model}
                  </label>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      <button onClick={handleNext}>Next</button>
    </div>
  );
};