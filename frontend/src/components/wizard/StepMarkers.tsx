import React from 'react';

interface StepMarkersProps {
  currentStep: number;
  totalSteps: number;
  onStepClick: (step: number) => void;
  disabled?: boolean;
  labels?: string[];
}

export default function StepMarkers({
  currentStep,
  totalSteps,
  onStepClick,
  disabled = false,
  labels = [],
}: StepMarkersProps) {
  const getStepState = (idx: number) => {
    if (idx === currentStep) return 'current';
    if (idx < currentStep) return 'past';
    return 'future';
  };

  const isClickable = (idx: number) => {
    return !disabled && idx <= currentStep;
  };

  return (
    <nav
      className="flex items-center justify-center gap-3 mb-8"
      role="navigation"
      aria-label="Step progress"
    >
      {Array.from({ length: totalSteps }).map((_, idx) => {
        const state = getStepState(idx);
        const clickable = isClickable(idx);
        const label = labels[idx] || `Step ${idx + 1}`;

        return (
          <button
            key={idx}
            type="button"
            onClick={() => clickable && onStepClick(idx)}
            disabled={!clickable}
            aria-label={label}
            aria-current={state === 'current' ? 'step' : undefined}
            aria-disabled={!clickable}
            tabIndex={clickable ? 0 : -1}
            className={`
              relative group transition-all duration-200
              focus:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-gray-900
              ${state === 'current' ? 'scale-110' : 'scale-100'}
              ${clickable ? 'cursor-pointer' : 'cursor-not-allowed'}
            `}
          >
            {/* Step dot */}
            <div
              className={`
                w-3 h-3 rounded-full transition-all duration-200
                ${
                  state === 'current'
                    ? 'bg-purple-500 shadow-[0_0_12px_rgba(168,85,247,0.8)]'
                    : state === 'past'
                    ? 'bg-purple-400 hover:bg-purple-300'
                    : 'bg-gray-600 opacity-50'
                }
              `}
              aria-hidden="true"
            />

            {/* Active step pulse */}
            {state === 'current' && (
              <div className="absolute inset-0 animate-pulse" aria-hidden="true">
                <div className="w-3 h-3 rounded-full bg-purple-400/50" />
              </div>
            )}

            {/* Tooltip */}
            {clickable && (
              <span
                className="
                  absolute -top-8 left-1/2 -translate-x-1/2
                  opacity-0 group-hover:opacity-100 group-focus:opacity-100
                  transition-opacity duration-200
                  pointer-events-none whitespace-nowrap
                  px-2 py-1 text-xs rounded
                  bg-gray-800 text-white border border-gray-700
                  z-10
                "
                role="tooltip"
              >
                {label}
              </span>
            )}
          </button>
        );
      })}
    </nav>
  );
}
