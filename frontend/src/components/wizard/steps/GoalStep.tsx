import React, { useState } from 'react';

interface GoalStepProps {
  onNext: (goals: string[]) => void;
}

export const GoalStep: React.FC<GoalStepProps> = ({ onNext }) => {
  const [goals, setGoals] = useState<string[]>([]);

  const handleGoalChange = (goal: string, checked: boolean) => {
    if (checked) {
      setGoals([...goals, goal]);
    } else {
      setGoals(goals.filter(g => g !== goal));
    }
  };

  const handleNext = () => {
    onNext(goals);
  };

  return (
    <div className="goal-step">
      <h2>What are your goals?</h2>
      <div className="goals">
        <label>
          <input type="checkbox" onChange={(e) => handleGoalChange('analysis', e.target.checked)} />
          Deep Analysis
        </label>
        <label>
          <input type="checkbox" onChange={(e) => handleGoalChange('speed', e.target.checked)} />
          Fast Response
        </label>
        <label>
          <input type="checkbox" onChange={(e) => handleGoalChange('accuracy', e.target.checked)} />
          High Accuracy
        </label>
        <label>
          <input type="checkbox" onChange={(e) => handleGoalChange('cost', e.target.checked)} />
          Cost Efficiency
        </label>
      </div>
      <button onClick={handleNext}>Next</button>
    </div>
  );
};