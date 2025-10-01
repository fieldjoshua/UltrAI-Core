import React, { useState } from 'react';

interface GoalStepProps {
  onNext: (selectedGoals: string[]) => void;
  onBack?: () => void;
}

const GOALS = [
  { id: 'analysis', label: 'Data Analysis', description: 'Analyze datasets and extract insights' },
  { id: 'writing', label: 'Content Writing', description: 'Generate high-quality written content' },
  { id: 'research', label: 'Research', description: 'Conduct in-depth research on topics' },
  { id: 'coding', label: 'Code Review', description: 'Review and improve code quality' },
  { id: 'planning', label: 'Project Planning', description: 'Help plan and organize projects' },
  { id: 'creative', label: 'Creative Work', description: 'Brainstorm and creative assistance' },
];

export function GoalStep({ onNext, onBack }: GoalStepProps) {
  const [selectedGoals, setSelectedGoals] = useState<string[]>([]);

  const handleGoalToggle = (goalId: string) => {
    setSelectedGoals(prev =>
      prev.includes(goalId)
        ? prev.filter(id => id !== goalId)
        : [...prev, goalId]
    );
  };

  const handleNext = () => {
    if (selectedGoals.length > 0) {
      onNext(selectedGoals);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && selectedGoals.length > 0) {
      handleNext();
    }
  };

  return (
    <div className="goal-step">
      <div className="goal-content">
        <h2 className="goal-title">What do you need help with?</h2>
        <p className="goal-description">
          Select all that apply to help us understand your needs better.
        </p>

        <div className="goals-list">
          {GOALS.map(goal => (
            <label key={goal.id} className="goal-item">
              <input
                type="checkbox"
                checked={selectedGoals.includes(goal.id)}
                onChange={() => handleGoalToggle(goal.id)}
                className="goal-checkbox"
              />
              <div className="goal-info">
                <span className="goal-label">{goal.label}</span>
                <span className="goal-description-text">{goal.description}</span>
              </div>
            </label>
          ))}
        </div>

        <div className="goal-actions">
          {onBack && (
            <button className="goal-back-button" onClick={onBack}>
              Back
            </button>
          )}
          <button
            className="goal-next-button"
            onClick={handleNext}
            onKeyPress={handleKeyPress}
            disabled={selectedGoals.length === 0}
          >
            Next ({selectedGoals.length} selected)
          </button>
        </div>
      </div>
    </div>
  );
}