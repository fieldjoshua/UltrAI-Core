import React from 'react';

// Assuming Step type and stepInfo are defined elsewhere or passed as props
// For simplicity here, let's redefine them or assume they are imported
type Step =
  | 'INTRO'
  | 'PROMPT'
  | 'DOCUMENTS'
  | 'MODELS'
  | 'ANALYSIS_TYPE'
  | 'OPTIONS'
  | 'PROCESSING'
  | 'RESULTS';

const stepInfo: Record<Step, { title: string; description: string }> = {
  INTRO: { title: 'Welcome', description: '...' }, // Simplified descriptions
  PROMPT: { title: 'Prompt', description: '...' },
  DOCUMENTS: { title: 'Context', description: '...' },
  MODELS: { title: 'Models', description: '...' },
  ANALYSIS_TYPE: { title: 'Method', description: '...' },
  OPTIONS: { title: 'Options', description: '...' },
  PROCESSING: { title: 'Processing', description: '...' },
  RESULTS: { title: 'Results', description: '...' },
};

interface StepIndicatorProps {
  currentStep: Step;
}

// Basic Progress component placeholder (replace with actual UI library component if needed)
const Progress = ({ value }: { value: number }) => (
  <div className="relative w-full bg-gray-800 h-2 rounded-full overflow-hidden">
    <div
      className="absolute top-0 left-0 h-full bg-gradient-to-r from-cyan-500 to-cyan-400 transition-all duration-300"
      style={{ width: `${value}%` }}
    />
  </div>
);

const StepIndicator: React.FC<StepIndicatorProps> = ({ currentStep }) => {
  if (currentStep === 'INTRO') return null;

  const steps: Step[] = [
    'INTRO',
    'PROMPT',
    'DOCUMENTS',
    'MODELS',
    'ANALYSIS_TYPE',
    'OPTIONS',
    'PROCESSING',
    'RESULTS',
  ];
  const stepTitles = [
    'Intro', // Keep consistent for display
    'Prompt',
    'Context',
    'Models',
    'Method',
    'Options',
    'Process',
    'Results',
  ];
  const currentIndex = steps.indexOf(currentStep);
  // Calculate progress based on reaching the *start* of the step, except for Results
  const progressValue =
    currentStep === 'RESULTS'
      ? 100
      : Math.round((currentIndex / (steps.length - 2)) * 100);

  return (
    <div className="mb-8">
      <div className="flex justify-between w-full mb-2">
        {stepTitles.map(
          (title, index) =>
            // Skip INTRO title display
            index > 0 && (
              <div
                key={title}
                className={`text-xs md:text-sm font-medium text-center px-1 ${
                  currentIndex >= index ? 'text-cyan-400' : 'text-gray-500'
                }`}
              >
                {index}. {title}
              </div>
            )
        )}
      </div>
      <Progress value={progressValue} />
    </div>
  );
};

export default StepIndicator;
