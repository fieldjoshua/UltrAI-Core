import React, { RefObject } from 'react';
import { DollarSign, Award } from 'lucide-react';

// Assuming Step type is defined elsewhere
type Step =
  | 'INTRO'
  | 'PROMPT'
  | 'DOCUMENTS'
  | 'MODELS'
  | 'ANALYSIS_TYPE'
  | 'OPTIONS'
  | 'PROCESSING'
  | 'RESULTS';

interface FloatingPriceProps {
  isVisible: boolean;
  position: { top: number; right: number };
  selectedLLMs: string[];
  prices: { [key: string]: number };
  currentStep: Step;
  stepInfo: Record<Step, { title: string; description: string }>; // Assuming stepInfo structure
  floatingPriceRef: RefObject<HTMLDivElement>;
  isOffline: boolean; // Added to potentially adjust display when offline
}

const FloatingPrice: React.FC<FloatingPriceProps> = ({
  isVisible,
  position,
  selectedLLMs,
  prices,
  currentStep,
  stepInfo,
  floatingPriceRef,
  isOffline,
}) => {
  if (!isVisible) return null;

  const totalPrice = selectedLLMs.reduce(
    (total, model) => total + (prices[model] || 0),
    0
  );

  const stepKeys = Object.keys(stepInfo);
  const currentStepIndex = stepKeys.indexOf(currentStep);

  return (
    <div
      ref={floatingPriceRef}
      className="fixed shadow-lg rounded-lg bg-white dark:bg-gray-800 p-4 z-50 border border-gray-200 dark:border-gray-700 transition-all duration-300"
      style={{
        top: `${position.top}px`,
        right: `${position.right}px`,
        opacity: isOffline ? 0.5 : 1,
      }}
    >
      <div className="flex flex-col gap-2">
        <h3 className="font-medium text-sm text-gray-700 dark:text-gray-300 flex items-center">
          <Award className="w-4 h-4 mr-1 text-amber-400" /> Price Estimate
        </h3>
        <div className="flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-cyan-500" />
          <span className="text-lg font-medium text-cyan-500">
            {totalPrice.toFixed(4)}
          </span>
          <span className="text-xs text-gray-400 ml-1">/ 1K tokens</span>
        </div>

        {/* Step completion indicator */}
        {currentStep !== 'INTRO' && (
          <div className="text-xs text-gray-500 dark:text-gray-400 mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
            Step {currentStepIndex + 1} of {stepKeys.length}:{' '}
            {stepInfo[currentStep]?.title || 'Unknown'}
          </div>
        )}
      </div>
    </div>
  );
};

export default FloatingPrice;
