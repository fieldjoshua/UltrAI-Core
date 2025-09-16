import React from 'react';

export type StepDef = {
  id: string;
  label: string;
  color: string; // tailwind color token e.g. 'cyan'
};

export interface ProgressStepperProps {
  steps: StepDef[];
  currentIndex: number;
  completedCount?: number;
}

/**
 * ProgressStepper renders a 5-stop progress bar with color-coded steps.
 */
const ProgressStepper: React.FC<ProgressStepperProps> = ({
  steps,
  currentIndex,
  completedCount = 0,
}) => {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {steps.map((step, i) => {
          const isCompleted = i < completedCount || i < currentIndex;
          const isCurrent = i === currentIndex;
          const baseColor = step.color;
          const circleColor =
            isCompleted || isCurrent ? `bg-${baseColor}-500` : 'bg-muted';
          const textColor =
            isCompleted || isCurrent
              ? `text-${baseColor}-400`
              : 'text-muted-foreground';
          return (
            <div key={step.id} className="flex-1 flex items-center">
              {/* Circle */}
              <div className="flex flex-col items-center">
                <div
                  className={`w-8 h-8 rounded-full border border-border flex items-center justify-center ${circleColor}`}
                >
                  <span className="text-xs text-white">{i + 1}</span>
                </div>
                <div className={`text-xs mt-2 ${textColor}`}>{step.label}</div>
              </div>
              {/* Connector */}
              {i < steps.length - 1 && (
                <div
                  className={`h-1 flex-1 mx-2 rounded ${isCompleted ? `bg-${baseColor}-500` : 'bg-muted'}`}
                />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ProgressStepper;
