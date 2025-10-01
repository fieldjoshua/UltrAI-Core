import React from 'react';

export interface StepDefinition {
  title: string;
  type?: string;
}

export interface StepNavigationProps {
  steps: StepDefinition[];
  currentStep: number;
  onStepClick: (index: number) => void;
}

const StepNavigation: React.FC<StepNavigationProps> = ({ steps, currentStep, onStepClick }) => {
  const visibleSteps = steps.slice(1, 6);

  return (
    <nav aria-label="Wizard step navigation" className="flex items-center justify-center gap-2">
      {visibleSteps.map((step, idx) => {
        const actualIndex = idx + 1;
        const isCurrent = actualIndex === currentStep;
        const label = step?.title ? `Go to ${step.title}` : `Go to step ${actualIndex}`;

        return (
          <button
            key={actualIndex}
            type="button"
            aria-label={label}
            aria-current={isCurrent ? 'step' : undefined}
            onClick={() => onStepClick(actualIndex)}
            className={
              `w-9 h-9 rounded-full text-sm font-medium border transition-colors ` +
              (isCurrent
                ? 'bg-white text-black border-white'
                : 'bg-transparent text-white border-white/40 hover:border-white')
            }
          >
            {actualIndex}
          </button>
        );
      })}
    </nav>
  );
};

export default StepNavigation;



