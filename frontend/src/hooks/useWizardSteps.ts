import { useState, useCallback, useEffect } from 'react';

export interface WizardStep {
  title: string;
  color: string;
  type: string;
  narrative?: string;
  options?: any[];
}

export function useWizardSteps(steps: WizardStep[]) {
  const [currentStep, setCurrentStep] = useState(0);
  const [stepHistory, setStepHistory] = useState<number[]>([0]);

  const goToStep = useCallback((step: number) => {
    if (step >= 0 && step < steps.length) {
      setCurrentStep(step);
      setStepHistory(prev => [...prev, step]);
    }
  }, [steps.length]);

  const goBack = useCallback(() => {
    if (stepHistory.length > 1) {
      const newHistory = stepHistory.slice(0, -1);
      setStepHistory(newHistory);
      setCurrentStep(newHistory[newHistory.length - 1]);
    }
  }, [stepHistory]);

  const goNext = useCallback(() => {
    goToStep(Math.min(currentStep + 1, steps.length - 1));
  }, [currentStep, goToStep, steps.length]);

  const goPrevious = useCallback(() => {
    goToStep(Math.max(currentStep - 1, 0));
  }, [currentStep, goToStep]);

  const handleKeyboard = useCallback((e: KeyboardEvent) => {
    // Don't navigate if user is typing in input/textarea
    if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
      return;
    }

    if (e.key === 'ArrowRight') {
      e.preventDefault();
      goNext();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      goPrevious();
    } else if (e.key === 'Enter' && currentStep === 0) {
      e.preventDefault();
      goToStep(1);
    }
  }, [currentStep, goNext, goPrevious, goToStep]);

  const canGoBack = currentStep > 0;
  const canGoNext = currentStep < steps.length - 1;
  const isFirstStep = currentStep === 0;
  const isLastStep = currentStep === steps.length - 1;

  return {
    currentStep,
    goToStep,
    goBack,
    goNext,
    goPrevious,
    handleKeyboard,
    stepHistory,
    canGoBack,
    canGoNext,
    isFirstStep,
    isLastStep,
  };
}
