import React, { useState } from 'react';
import { Button } from '../../Button';
import { Checkbox } from '../../Checkbox';

interface Goal {
  id: string;
  label: string;
  description: string;
  icon: string;
}

interface GoalStepProps {
  selectedGoals: string[];
  onGoalsChange: (goals: string[]) => void;
  onNext: () => void;
  onBack: () => void;
}

const GOALS: Goal[] = [
  {
    id: 'analyze',
    label: 'Deep Analysis',
    description: 'Comprehensive analysis with detailed insights',
    icon: '🔍'
  },
  {
    id: 'summarize',
    label: 'Summarization',
    description: 'Condense information into key points',
    icon: '📋'
  },
  {
    id: 'compare',
    label: 'Comparison',
    description: 'Compare multiple items or perspectives',
    icon: '⚖️'
  },
  {
    id: 'generate',
    label: 'Content Generation',
    description: 'Create new content based on requirements',
    icon: '✍️'
  },
  {
    id: 'extract',
    label: 'Data Extraction',
    description: 'Extract specific information from sources',
    icon: '📊'
  },
  {
    id: 'optimize',
    label: 'Optimization',
    description: 'Improve processes or suggest enhancements',
    icon: '🚀'
  }
];

export function GoalStep({ selectedGoals, onGoalsChange, onNext, onBack }: GoalStepProps) {
  const handleGoalToggle = (goalId: string) => {
    const newGoals = selectedGoals.includes(goalId)
      ? selectedGoals.filter(id => id !== goalId)
      : [...selectedGoals, goalId];
    onGoalsChange(newGoals);
  };

  const handleSelectAll = () => {
    onGoalsChange(GOALS.map(goal => goal.id));
  };

  const handleClearAll = () => {
    onGoalsChange([]);
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-cyber-green mb-2">
          What are your goals?
        </h2>
        <p className="text-gray-300">
          Select one or more objectives for your analysis
        </p>
      </div>

      <div className="flex justify-center space-x-4 mb-6">
        <Button
          onClick={handleSelectAll}
          variant="outline"
          size="sm"
          className="text-cyber-blue border-cyber-blue hover:bg-cyber-blue/10"
        >
          Select All
        </Button>
        <Button
          onClick={handleClearAll}
          variant="outline"
          size="sm"
          className="text-gray-400 border-gray-400 hover:bg-gray-400/10"
        >
          Clear All
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl mx-auto">
        {GOALS.map((goal) => (
          <div
            key={goal.id}
            className={`p-4 rounded-lg border-2 transition-all duration-200 cursor-pointer ${
              selectedGoals.includes(goal.id)
                ? 'border-cyber-green bg-cyber-green/10'
                : 'border-gray-600 hover:border-gray-400'
            }`}
            onClick={() => handleGoalToggle(goal.id)}
          >
            <div className="flex items-start space-x-3">
              <Checkbox
                checked={selectedGoals.includes(goal.id)}
                onChange={() => handleGoalToggle(goal.id)}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-2xl">{goal.icon}</span>
                  <h3 className="font-semibold text-white">{goal.label}</h3>
                </div>
                <p className="text-sm text-gray-400">{goal.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedGoals.length > 0 && (
        <div className="text-center text-sm text-gray-400">
          {selectedGoals.length} goal{selectedGoals.length !== 1 ? 's' : ''} selected
        </div>
      )}

      <div className="flex justify-between pt-6">
        <Button
          onClick={onBack}
          variant="outline"
          className="border-gray-400 text-gray-400 hover:bg-gray-400/10"
        >
          Back
        </Button>
        <Button
          onClick={onNext}
          disabled={selectedGoals.length === 0}
          className="bg-cyber-green hover:bg-cyber-green/80 text-black disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue
        </Button>
      </div>
    </div>
  );
}