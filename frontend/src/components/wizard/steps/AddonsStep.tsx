import React from 'react';

interface AddonOption {
  label: string;
  icon: string;
  cost?: number;
}

interface AddonsStepProps {
  options: AddonOption[];
  selectedAddons: string[];
  onToggle: (addon: string) => void;
  onSubmit: () => void;
}

export default function AddonsStep({ options, selectedAddons, onToggle, onSubmit }: AddonsStepProps) {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Add-ons & formatting</h2>
      <p className="text-gray-400 mb-8">Add extras like PDF export, citations, or priority processing.</p>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
        {options.map((option) => {
          const isSelected = selectedAddons.includes(option.label);
          return (
            <button
              key={option.label}
              onClick={() => onToggle(option.label)}
              className={`p-4 rounded-lg border-2 transition-all ${
                isSelected
                  ? 'border-purple-500 bg-purple-500/20'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              <div className="text-3xl mb-2">{option.icon}</div>
              <div className="text-sm mb-1">{option.label}</div>
              {option.cost !== undefined && (
                <div className="text-xs text-gray-500">+${option.cost.toFixed(2)}</div>
              )}
            </button>
          );
        })}
      </div>

      <button
        onClick={onSubmit}
        className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold transition-colors"
      >
        Submit Add-ons
      </button>
    </div>
  );
}
