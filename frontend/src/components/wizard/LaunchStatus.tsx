import { useEffect, useMemo, useState, useRef } from "react";
import { OutlineIcon } from "@components/icons/OutlineIcons";
import { Zap, Activity, Check } from 'lucide-react';

interface LaunchStatusProps {
  isComplete?: boolean;
  orchestratorResult?: {
    models_used?: string[];
    processing_time?: number;
    pattern_used?: string;
    final_result?: string;
  } | null;
  selectedAddons?: Array<{ label: string }>;
  onViewResults?: () => void;
  onStartNew?: () => void;
  hasError?: boolean;
}

export default function LaunchStatus({
  isComplete = false,
  orchestratorResult,
  selectedAddons = [],
  onViewResults,
  onStartNew,
  hasError = false,
}: LaunchStatusProps) {
  const stages = useMemo(
    () => [
      { key: 'boot', label: 'Initializing AI models', phase: 'initial', subtext: 'Activating GPT-5, Claude 4.1, Gemini 2.5...' },
      { key: 'submit', label: 'Processing your query', phase: 'initial', subtext: 'Optimizing prompts for each model...' },
      { key: 'initial', label: 'Models generating initial responses', phase: 'initial', subtext: 'Parallel processing across all models...' },
      { key: 'distribute', label: 'Cross-model intelligence sharing', phase: 'meta', subtext: 'Sharing insights between models...' },
      { key: 'revise', label: 'Models refining responses', phase: 'meta', subtext: 'Enhancing based on shared knowledge...' },
      { key: 'meta_submit', label: 'Preparing meta-analysis', phase: 'meta', subtext: 'Identifying patterns and consensus...' },
      { key: 'meta_analyze', label: 'Synthesizing insights', phase: 'synthesis', subtext: 'Creating unified intelligence output...' },
      { key: 'write', label: 'Creating Ultra Synthesis™ report', phase: 'synthesis', subtext: 'Formatting final deliverables...' },
    ],
    []
  );

  const [stageIndex, setStageIndex] = useState(0);
  const [completedStages, setCompletedStages] = useState<number[]>([]);
  const [animatingStages, setAnimatingStages] = useState<number[]>([]);

  useEffect(() => {
    if (isComplete) {
      setStageIndex(stages.length - 1);
      return;
    }
    if (hasError) return;
    
    // Dynamic timing based on stage phase
    const getStageDelay = (index: number) => {
      const stage = stages[index];
      if (!stage) return 5000;
      
      // Initial analysis & revision stages: 7s each
      if (stage.phase === 'initial' || stage.phase === 'meta') {
        return 7000;
      }
      // Synthesis stages: 3s each (faster since it's one LLM)
      if (stage.phase === 'synthesis') {
        return 3000;
      }
      return 5000;
    };
    
    let timeoutId: NodeJS.Timeout;
    const advanceStage = () => {
      setStageIndex((currentIndex) => {
        const nextIndex = Math.min(currentIndex + 1, stages.length - 2);
        if (nextIndex !== currentIndex && nextIndex < stages.length - 1) {
          const delay = getStageDelay(nextIndex);
          timeoutId = setTimeout(advanceStage, delay);
        }
        return nextIndex;
      });
    };
    
    // Start with first stage delay
    timeoutId = setTimeout(advanceStage, getStageDelay(0));
    
    return () => clearTimeout(timeoutId);
  }, [isComplete, hasError, stages]);

  useEffect(() => {
    if (isComplete && orchestratorResult) {
      setStageIndex(stages.length - 1);
    }
  }, [isComplete, orchestratorResult, stages.length]);

  // Handle stage completion animation
  useEffect(() => {
    if (current > 0 && !completedStages.includes(current - 1)) {
      // Animate the previous stage dropping down
      setAnimatingStages(prev => [...prev, current - 1]);
      
      // After animation, mark as completed
      setTimeout(() => {
        setCompletedStages(prev => [...prev, current - 1]);
        setAnimatingStages(prev => prev.filter(idx => idx !== current - 1));
      }, 800);
    }
  }, [current, completedStages]);

  const current = Math.max(0, Math.min(stageIndex, stages.length - 1));
  const borderColor = hasError ? 'border-red-500/50' : 'animate-border-hum';
  const glowColor = hasError ? 'from-red-500/10 via-transparent to-red-500/10' : 'from-cyan-500/5 via-transparent to-orange-500/5';

  // Calculate phase progress
  const currentPhase = stages[current]?.phase || 'initial';
  const phaseProgress = {
    initial: current < 3 ? (current + 1) / 3 * 100 : 100,
    meta: current >= 3 && current < 6 ? ((current - 2) / 3 * 100) : current >= 6 ? 100 : 0,
    synthesis: current >= 6 ? ((current - 5) / 2 * 100) : 0
  };

  return (
    <div className={`glass-strong rounded-xl p-6 border-2 ${borderColor} relative overflow-hidden`}>
      <div className={`absolute inset-0 bg-gradient-to-br ${glowColor} pointer-events-none`} />
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Zap className="w-8 h-8 animate-pulse" />
            <div>
              <div className="text-sm font-bold uppercase tracking-wider">Ultra Synthesis™ Processing</div>
              <div className="text-xs text-white/60 mt-0.5">Orchestrating {Array.isArray(orchestratorResult?.models_used) ? orchestratorResult.models_used.length : '3'} AI models</div>
            </div>
          </div>
          {!isComplete && (
            <div className="text-xs text-white/60">
              Est. {(() => {
                let remaining = 0;
                for (let i = current + 1; i < stages.length; i++) {
                  const phase = stages[i]?.phase;
                  if (phase === 'initial' || phase === 'meta') remaining += 7;
                  else if (phase === 'synthesis') remaining += 3;
                  else remaining += 5;
                }
                return Math.max(3, remaining);
              })()}s remaining
            </div>
          )}
        </div>
        
        {/* Phase Progress Indicators */}
        <div className="grid grid-cols-3 gap-2 mb-6">
          <div className="text-center">
            <div className="text-xs font-semibold mb-1">Initial Analysis</div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-cyan-400 transition-all duration-1000" style={{ width: `${phaseProgress.initial}%` }} />
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs font-semibold mb-1">Meta Analysis</div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-purple-400 transition-all duration-1000" style={{ width: `${phaseProgress.meta}%` }} />
            </div>
          </div>
          <div className="text-center">
            <div className="text-xs font-semibold mb-1">Ultra Synthesis</div>
            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-gradient-to-r from-cyan-400 to-purple-400 transition-all duration-1000" style={{ width: `${phaseProgress.synthesis}%` }} />
            </div>
          </div>
        </div>
        <div className="relative" style={{ minHeight: '280px' }}>
          {/* Active stages display */}
          <div className="space-y-3">
            {stages.map((st, i) => {
              const state = i < current ? 'done' : i === current ? 'current' : 'pending';
              const isAnimating = animatingStages.includes(i);
              const isCompleted = completedStages.includes(i);
              
              if (isCompleted && !isAnimating) return null;
              
              return (
                <div
                  key={st.key}
                  className={`transition-all duration-500 ${state === 'pending' ? 'translate-x-8 opacity-50' : ''} ${
                    isAnimating ? 'animate-[dropDown_0.8s_ease-in-out_forwards]' : ''
                  }`}
                  style={{
                    animation: isAnimating ? 'dropDown 0.8s ease-in-out forwards' : undefined
                  }}
                >
                  <div className="flex items-center gap-3 bg-white/5 rounded-lg p-3 border border-white/20">
                    <div className={`${state === 'done' ? 'text-green-400' : state === 'current' ? 'text-cyan-300' : 'text-white/40'}`}>
                      {state === 'done' ? (
                        <Check className="w-6 h-6" />
                      ) : state === 'current' ? (
                        <Activity className="w-6 h-6 animate-pulse" />
                      ) : (
                        <OutlineIcon name={st.key} category="status" className="w-6 h-6" />
                      )}
                    </div>
                    <div className="flex-1">
                      <div className={`text-sm font-semibold ${state === 'current' ? 'text-white' : ''}`}>{st.label}</div>
                      {st.subtext && state === 'current' && (
                        <div className="text-[10px] text-cyan-300/80 mt-0.5">
                          {st.subtext}
                        </div>
                      )}
                    </div>
                    {state === 'current' && (
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-24 bg-white/10 rounded-full overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 rounded-full" 
                               style={{
                                 width: '30%',
                                 animation: 'slideProgress 2s ease-in-out infinite'
                               }}></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
          
          {/* Collection area at bottom */}
          {completedStages.length > 0 && (
            <div className="absolute bottom-0 left-0 right-0 mt-4 p-3 bg-gradient-to-t from-black/40 to-transparent rounded-b-lg">
              <div className="text-[10px] font-semibold text-white/60 mb-2">Completed Stages</div>
              <div className="flex flex-wrap gap-2">
                {completedStages.map((idx) => (
                  <div key={stages[idx].key} className="bg-green-500/20 border border-green-400/50 rounded px-2 py-1 text-[9px] text-green-300 animate-[fadeInUp_0.5s_ease-out]">
                    <Check className="w-3 h-3 inline mr-1" />
                    {stages[idx].label.split(' ').slice(0, 2).join(' ')}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {isComplete && orchestratorResult && (
          <>
            <div className="grid grid-cols-3 gap-3 mt-6 mb-4">
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <OutlineIcon name="Models Used" category="status" className="w-8 h-8 mx-auto mb-1" />
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Models Used</div>
                <div className="text-[14px] font-bold text-green-300 mt-1">
                  {Array.isArray(orchestratorResult.models_used) ? orchestratorResult.models_used.length : '3'}
                </div>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <OutlineIcon name="Processing Time" category="status" className="w-8 h-8 mx-auto mb-1" />
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Processing Time</div>
                <div className="text-[14px] font-bold text-blue-300 mt-1">
                  {typeof orchestratorResult.processing_time === 'number'
                    ? `${Math.floor(orchestratorResult.processing_time / 60)}:${String(Math.floor(orchestratorResult.processing_time % 60)).padStart(2, '0')}`
                    : '5:42'}
                </div>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <OutlineIcon name="Pattern" category="status" className="w-8 h-8 mx-auto mb-1" />
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Pattern</div>
                <div className="text-[14px] font-bold text-purple-300 mt-1">
                  {orchestratorResult.pattern_used || 'Ultra'}
                </div>
              </div>
            </div>

            {selectedAddons.length > 0 && (
              <div className="mb-4 p-4 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg border border-white/20">
                <div className="text-[11px] font-semibold text-white/80 mb-3 flex items-center gap-2"><OutlineIcon name="Enhanced" category="status" className="w-4 h-4" /> Enhanced Analysis Features:</div>
                <div className="grid grid-cols-2 gap-2">
                  {selectedAddons.map((addon, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-[11px] text-white/90">
                      <Check className="w-4 h-4 text-green-400" />
                      <span>{addon.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-2 mt-4">
              <button
                className="w-full px-4 py-3 rounded-lg font-semibold text-white transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] relative group"
                style={{
                  background: 'linear-gradient(135deg, #00ff9f 0%, #00d4ff 100%)',
                  border: '2px solid transparent',
                  backgroundClip: 'padding-box',
                }}
                onClick={onViewResults}
              >
                <span className="relative z-10 flex items-center justify-center gap-2"><OutlineIcon name="Results" category="action" className="w-5 h-5" /> View Full Results</span>
                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-green-400 to-blue-400 opacity-0 group-hover:opacity-50 blur-xl transition-opacity duration-300" />
              </button>

              <button
                className="w-full px-3 py-2 rounded-lg font-medium text-white/70 transition-all duration-300 hover:text-white hover:bg-white/10"
                style={{ border: '1px solid rgba(255,255,255,0.2)' }}
                onClick={onStartNew}
              >
                <span className="flex items-center justify-center gap-2"><OutlineIcon name="Restart" category="action" className="w-5 h-5" /> Start New Analysis</span>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}


