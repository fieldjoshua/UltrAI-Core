import React from 'react';

interface GoalOption {
  label: string;
  icon: string;
}

interface GoalStepProps {
  options: GoalOption[];
  selectedGoals: string[];
  onToggle: (goal: string) => void;
}

export default function GoalStep({ options, selectedGoals, onToggle }: GoalStepProps) {
  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-6">Select your goals</h2>
      <p className="text-gray-400 mb-8">What are you working on today?</p>
      
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {options.map((option) => {
          const isSelected = selectedGoals.includes(option.label);
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
              <div className="text-sm">{option.label}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
