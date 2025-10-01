import React from 'react';
import { Check, AlertCircle, Loader2 } from 'lucide-react';

export interface LaunchStage {
  key: string;
  label: string;
  phase: 'initial' | 'meta' | 'synthesis';
  subtext?: string;
}

export interface LaunchProgressProps {
  stages: LaunchStage[];
  currentIndex: number;
  currentProgress: number;
  isComplete: boolean;
  hasError: boolean;
  isDemoMode?: boolean;
  isStagingEnv?: boolean;
}

const PHASE_LABELS = {
  initial: 'Initial Generation',
  meta: 'Meta-Analysis',
  synthesis: 'Ultra Synthesis™',
};

export default function LaunchProgress({
  stages,
  currentIndex,
  currentProgress,
  isComplete,
  hasError,
  isDemoMode = false,
  isStagingEnv = false,
}: LaunchProgressProps) {
  const phasePercentages = React.useMemo(() => {
    const phaseCounts = { initial: 0, meta: 0, synthesis: 0 };
    stages.forEach((s) => phaseCounts[s.phase]++);
    const total = stages.length;

    return {
      initial: (phaseCounts.initial / total) * 100,
      meta: (phaseCounts.meta / total) * 100,
      synthesis: (phaseCounts.synthesis / total) * 100,
    };
  }, [stages]);

  const overallProgress = React.useMemo(() => {
    if (isComplete) return 100;
    if (hasError) return currentProgress;
    const baseProgress = (currentIndex / stages.length) * 100;
    const stageContribution = (currentProgress / stages.length);
    return Math.min(baseProgress + stageContribution, 100);
  }, [currentIndex, currentProgress, stages.length, isComplete, hasError]);

  const getStageState = (idx: number): 'done' | 'current' | 'pending' => {
    if (hasError && idx === currentIndex) return 'current';
    if (idx < currentIndex) return 'done';
    if (idx === currentIndex) return 'current';
    return 'pending';
  };

  const getStageIcon = (state: 'done' | 'current' | 'pending') => {
    if (hasError && state === 'current') {
      return <AlertCircle className="w-4 h-4 text-red-500" aria-label="Error" />;
    }
    if (state === 'done') {
      return <Check className="w-4 h-4 text-green-500" aria-label="Complete" />;
    }
    if (state === 'current') {
      return <Loader2 className="w-4 h-4 text-purple-500 animate-spin" aria-label="In progress" />;
    }
    return <div className="w-4 h-4 rounded-full bg-gray-600" aria-hidden="true" />;
  };

  return (
    <div className="space-y-6">
      {/* Environment badges */}
      {(isDemoMode || isStagingEnv) && (
        <div className="flex gap-2">
          {isDemoMode && (
            <span className="px-2 py-1 text-xs font-semibold bg-yellow-500/20 text-yellow-400 rounded border border-yellow-500/30">
              DEMO
            </span>
          )}
          {isStagingEnv && (
            <span className="px-2 py-1 text-xs font-semibold bg-blue-500/20 text-blue-400 rounded border border-blue-500/30">
              STAGING
            </span>
          )}
        </div>
      )}

      {/* Phase bars */}
      <div className="space-y-2" role="status" aria-label={`Overall progress: ${Math.round(overallProgress)}%`}>
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Progress</span>
          <span>{Math.round(overallProgress)}%</span>
        </div>
        
        <div className="flex gap-1 h-2 bg-gray-800 rounded-full overflow-hidden">
          {(['initial', 'meta', 'synthesis'] as const).map((phase) => {
            const phaseStages = stages.filter((s) => s.phase === phase);
            const phaseStartIdx = stages.findIndex((s) => s.phase === phase);
            const phaseEndIdx = phaseStartIdx + phaseStages.length - 1;
            
            let phaseProgress = 0;
            if (currentIndex > phaseEndIdx) {
              phaseProgress = 100;
            } else if (currentIndex >= phaseStartIdx && currentIndex <= phaseEndIdx) {
              const completedInPhase = currentIndex - phaseStartIdx;
              const stageProgressInPhase = currentProgress / phaseStages.length;
              phaseProgress = ((completedInPhase + (stageProgressInPhase / 100)) / phaseStages.length) * 100;
            }

            return (
              <div
                key={phase}
                className="relative h-full transition-all duration-500"
                style={{ width: `${phasePercentages[phase]}%` }}
                aria-label={`${PHASE_LABELS[phase]}: ${Math.round(phaseProgress)}%`}
              >
                <div
                  className={`
                    h-full transition-all duration-500
                    ${phase === 'initial' ? 'bg-blue-500' : ''}
                    ${phase === 'meta' ? 'bg-purple-500' : ''}
                    ${phase === 'synthesis' ? 'bg-pink-500' : ''}
                  `}
                  style={{ width: `${phaseProgress}%` }}
                />
              </div>
            );
          })}
        </div>

        <div className="flex justify-between text-xs text-gray-500">
          {(['initial', 'meta', 'synthesis'] as const).map((phase) => (
            <span key={phase}>{PHASE_LABELS[phase]}</span>
          ))}
        </div>
      </div>

      {/* Stage list */}
      <div className="space-y-3" role="list" aria-label="Processing stages">
        {stages.map((stage, idx) => {
          const state = getStageState(idx);
          const showProgress = state === 'current' && !hasError;

          return (
            <div
              key={stage.key}
              role="listitem"
              aria-label={`${stage.label}: ${state}`}
              className={`
                flex items-start gap-3 p-3 rounded-lg transition-all duration-300
                ${state === 'current' ? 'bg-gray-800/50 border border-purple-500/30' : ''}
                ${state === 'done' ? 'opacity-60' : ''}
                ${state === 'pending' ? 'opacity-40' : ''}
              `}
            >
              {/* Icon */}
              <div className="flex-shrink-0 mt-0.5">{getStageIcon(state)}</div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div
                  className={`
                    text-sm font-medium
                    ${state === 'current' ? 'text-white' : 'text-gray-400'}
                  `}
                >
                  {stage.label}
                </div>
                {stage.subtext && state === 'current' && (
                  <div className="text-xs text-gray-500 mt-1">{stage.subtext}</div>
                )}

                {/* Stage progress bar */}
                {showProgress && (
                  <div className="mt-2 h-1 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-purple-500 transition-all duration-300"
                      style={{ width: `${currentProgress}%` }}
                      aria-hidden="true"
                    />
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Status message */}
      {isComplete && (
        <div className="text-center p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
          <div className="text-green-400 font-semibold">Analysis Complete!</div>
        </div>
      )}

      {hasError && (
        <div className="text-center p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
          <div className="text-red-400 font-semibold">An error occurred during processing</div>
        </div>
      )}
    </div>
  );
}
