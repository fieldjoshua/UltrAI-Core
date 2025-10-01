import React, { useState } from 'react';

interface AddonsStepProps {
  onNext: (selectedAddons: string[]) => void;
  onBack?: () => void;
}

const ADDONS = [
  {
    id: 'priority',
    label: 'Priority Processing',
    description: 'Move your request to the front of the queue',
    cost: '+50%',
    recommended: false,
  },
  {
    id: 'detailed-report',
    label: 'Detailed Report',
    description: 'Generate comprehensive documentation and analysis',
    cost: '+25%',
    recommended: true,
  },
  {
    id: 'follow-up',
    label: 'Follow-up Questions',
    description: 'Enable interactive follow-up capabilities',
    cost: '+15%',
    recommended: false,
  },
  {
    id: 'export-formats',
    label: 'Multiple Export Formats',
    description: 'Export results in PDF, DOCX, and other formats',
    cost: '+20%',
    recommended: false,
  },
  {
    id: 'real-time-updates',
    label: 'Real-time Updates',
    description: 'Get live progress updates during processing',
    cost: '+10%',
    recommended: false,
  },
  {
    id: 'data-persistence',
    label: 'Data Persistence',
    description: 'Store results for future reference and comparison',
    cost: '+5%',
    recommended: false,
  },
];

export function AddonsStep({ onNext, onBack }: AddonsStepProps) {
  const [selectedAddons, setSelectedAddons] = useState<string[]>([]);

  const handleAddonToggle = (addonId: string) => {
    setSelectedAddons(prev =>
      prev.includes(addonId)
        ? prev.filter(id => id !== addonId)
        : [...prev, addonId]
    );
  };

  const handleNext = () => {
    onNext(selectedAddons);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleNext();
    }
  };

  const getTotalCostIncrease = () => {
    return selectedAddons.length * 10; // Simplified calculation
  };

  return (
    <div className="addons-step">
      <div className="addons-content">
        <h2 className="addons-title">Optional Add-ons</h2>
        <p className="addons-description">
          Enhance your request with additional features and capabilities.
        </p>

        <div className="addons-list">
          {ADDONS.map(addon => (
            <label key={addon.id} className="addon-item">
              <input
                type="checkbox"
                checked={selectedAddons.includes(addon.id)}
                onChange={() => handleAddonToggle(addon.id)}
                className="addon-checkbox"
              />
              <div className="addon-info">
                <div className="addon-header">
                  <span className="addon-label">{addon.label}</span>
                  {addon.recommended && (
                    <span className="addon-recommended-badge">Recommended</span>
                  )}
                </div>
                <p className="addon-description">{addon.description}</p>
                <span className="addon-cost">Cost: {addon.cost}</span>
              </div>
            </label>
          ))}
        </div>

        <div className="addons-summary">
          <div className="addons-summary-text">
            {selectedAddons.length} addon{selectedAddons.length !== 1 ? 's' : ''} selected
            {selectedAddons.length > 0 && (
              <span className="addons-cost-increase">
                (+{getTotalCostIncrease()}% total cost)
              </span>
            )}
          </div>
        </div>

        <div className="addons-actions">
          {onBack && (
            <button className="addons-back-button" onClick={onBack}>
              Back
            </button>
          )}
          <button
            className="addons-next-button"
            onClick={handleNext}
            onKeyPress={handleKeyPress}
          >
            {selectedAddons.length > 0 ? 'Continue with Add-ons' : 'Skip Add-ons'}
          </button>
        </div>
      </div>
    </div>
  );
}