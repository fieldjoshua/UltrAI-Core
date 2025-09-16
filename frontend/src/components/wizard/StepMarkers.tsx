import React from 'react';

interface StepMarkersProps {
  currentStep: number;
  totalSteps: number;
  onStepClick: (step: number) => void;
  disabled?: boolean;
}

export default function StepMarkers({
  currentStep,
  totalSteps,
  onStepClick,
  disabled = false,
}: StepMarkersProps) {
  return (
    <div 
      className="flex items-center justify-center gap-3 mb-8 select-none" 
      role="navigation"
      aria-label="Wizard steps"
    >
      {Array.from({ length: totalSteps }).map((_, idx) => {
        const isActive = idx === currentStep;
        const isPast = idx < currentStep;
        const isFuture = idx > currentStep;
        
        return (
          <button
            key={idx}
            onClick={() => {
              if (!disabled && (isPast || isActive)) {
                onStepClick(idx);
              }
            }}
            disabled={disabled || isFuture}
            className={`
              relative group transition-all duration-300
              ${isActive ? 'scale-110' : 'scale-100'}
            `}
            aria-label={`Go to step ${idx + 1}`}
            aria-current={isActive ? 'step' : undefined}
          >
            {/* Step dot */}
            <div
              className={`
                w-3 h-3 rounded-full transition-all duration-300
                ${isActive 
                  ? 'bg-white shadow-[0_0_12px_rgba(255,255,255,0.8)]' 
                  : isPast 
                    ? 'bg-white/60 hover:bg-white/80' 
                    : 'bg-white/20 cursor-not-allowed'
                }
              `}
            />
            
            {/* Active step glow */}
            {isActive && (
              <div className="absolute inset-0 animate-ping">
                <div className="w-3 h-3 rounded-full bg-white/50" />
              </div>
            )}
            
            {/* Step tooltip */}
            {!disabled && (isPast || isActive) && (
              <div className="
                absolute -top-8 left-1/2 -translate-x-1/2
                opacity-0 group-hover:opacity-100
                transition-opacity duration-200
                pointer-events-none whitespace-nowrap
                px-2 py-1 text-xs rounded
                bg-black/80 text-white
              ">
                Step {idx + 1}
              </div>
            )}
          </button>
        );
      })}
    </div>
  );
}