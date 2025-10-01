import React, { useState } from 'react';

interface AddonsStepProps {
  onNext: (addons: string[]) => void;
}

export const AddonsStep: React.FC<AddonsStepProps> = ({ onNext }) => {
  const [addons, setAddons] = useState<string[]>([]);

  const handleAddonChange = (addon: string, checked: boolean) => {
    if (checked) {
      setAddons([...addons, addon]);
    } else {
      setAddons(addons.filter(a => a !== addon));
    }
  };

  const handleNext = () => {
    onNext(addons);
  };

  return (
    <div className="addons-step">
      <h2>Select Add-ons</h2>
      <div className="addons">
        <label>
          <input type="checkbox" onChange={(e) => handleAddonChange('debug', e.target.checked)} />
          Debug Mode
        </label>
        <label>
          <input type="checkbox" onChange={(e) => handleAddonChange('logging', e.target.checked)} />
          Detailed Logging
        </label>
        <label>
          <input type="checkbox" onChange={(e) => handleAddonChange('notifications', e.target.checked)} />
          Email Notifications
        </label>
        <label>
          <input type="checkbox" onChange={(e) => handleAddonChange('export', e.target.checked)} />
          Export Results
        </label>
      </div>
      <button onClick={handleNext}>Next</button>
    </div>
  );
};