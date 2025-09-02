import { useEffect, useMemo, useState } from "react";

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
      { key: 'boot', label: 'Initializing AI models', icon: '🚀', phase: 'initial' },
      { key: 'submit', label: 'Processing your query', icon: '📤', phase: 'initial' },
      { key: 'initial', label: 'Models generating initial responses', icon: '🧠', phase: 'initial' },
      { key: 'distribute', label: 'Cross-model intelligence sharing', icon: '🔁', phase: 'meta' },
      { key: 'revise', label: 'Models refining responses', icon: '✍️', phase: 'meta' },
      { key: 'meta_submit', label: 'Preparing meta-analysis', icon: '📑', phase: 'meta' },
      { key: 'meta_analyze', label: 'Synthesizing insights', icon: '🧪', phase: 'synthesis' },
      { key: 'write', label: 'Creating Ultra Synthesis™ report', icon: '📄', phase: 'synthesis' },
    ],
    []
  );

  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    if (isComplete) {
      setStageIndex(stages.length - 1);
      return;
    }
    if (hasError) return;
    // Realistic timing: ~35s per stage for 5-7 minute total
    const intervalMs = 35000;
    const t = setInterval(() => {
      setStageIndex((i) => Math.min(i + 1, stages.length - 2));
    }, intervalMs);
    return () => clearInterval(t);
  }, [isComplete, hasError, stages.length]);

  useEffect(() => {
    if (isComplete && orchestratorResult) {
      setStageIndex(stages.length - 1);
    }
  }, [isComplete, orchestratorResult, stages.length]);

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
            <div className="text-2xl animate-pulse">⚡</div>
            <div>
              <div className="text-sm font-bold uppercase tracking-wider">Ultra Synthesis™ Processing</div>
              <div className="text-xs text-white/60 mt-0.5">Orchestrating {Array.isArray(orchestratorResult?.models_used) ? orchestratorResult.models_used.length : '3'} AI models</div>
            </div>
          </div>
          {!isComplete && (
            <div className="text-xs text-white/60">
              Est. {Math.floor((stages.length - current) * 35 / 60)} min remaining
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
        <ol className="relative border-l border-white/15 pl-4 space-y-3">
          {stages.map((st, i) => {
            const state = i < current ? 'done' : i === current ? 'current' : 'pending';
            return (
              <li key={st.key} className="ml-2">
                <div className="flex items-start gap-2">
                  <span className={`mt-0.5 text-base ${state === 'done' ? 'text-green-400' : state === 'current' ? 'text-cyan-300 animate-pulse' : 'text-white/40'}`}>{st.icon}</span>
                  <div>
                    <div className={`text-sm font-semibold ${state === 'pending' ? 'opacity-50' : ''}`}>{st.label}</div>
                    {state === 'current' && (
                      <div className="mt-1 flex items-center gap-2">
                        <div className="h-1.5 w-36 bg-white/10 rounded overflow-hidden">
                          <div className="h-full bg-gradient-to-r from-cyan-400 to-orange-400 animate-pulse w-1/2"></div>
                        </div>
                        <div className="text-[10px] text-cyan-300 animate-pulse">Processing...</div>
                      </div>
                    )}
                    {state === 'done' && <div className="text-xs text-white/50 mt-0.5">Complete</div>}
                  </div>
                </div>
              </li>
            );
          })}
        </ol>

        {isComplete && orchestratorResult && (
          <>
            <div className="grid grid-cols-3 gap-3 mt-6 mb-4">
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <div className="text-2xl mb-1">🤖</div>
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Models Used</div>
                <div className="text-[14px] font-bold text-green-300 mt-1">
                  {Array.isArray(orchestratorResult.models_used) ? orchestratorResult.models_used.length : '3'}
                </div>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <div className="text-2xl mb-1">⚡</div>
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Processing Time</div>
                <div className="text-[14px] font-bold text-blue-300 mt-1">
                  {typeof orchestratorResult.processing_time === 'number'
                    ? `${Math.floor(orchestratorResult.processing_time / 60)}:${String(Math.floor(orchestratorResult.processing_time % 60)).padStart(2, '0')}`
                    : '5:42'}
                </div>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <div className="text-2xl mb-1">🎯</div>
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">Pattern</div>
                <div className="text-[14px] font-bold text-purple-300 mt-1">
                  {orchestratorResult.pattern_used || 'Ultra'}
                </div>
              </div>
            </div>

            {selectedAddons.length > 0 && (
              <div className="mb-4 p-4 bg-gradient-to-r from-purple-500/10 to-pink-500/10 rounded-lg border border-white/20">
                <div className="text-[11px] font-semibold text-white/80 mb-3">✨ Enhanced Analysis Features:</div>
                <div className="grid grid-cols-2 gap-2">
                  {selectedAddons.map((addon, idx) => (
                    <div key={idx} className="flex items-center gap-2 text-[11px] text-white/90">
                      <span className="text-green-400">✓</span>
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
                <span className="relative z-10">📄 View Full Results</span>
                <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-green-400 to-blue-400 opacity-0 group-hover:opacity-50 blur-xl transition-opacity duration-300" />
              </button>

              <button
                className="w-full px-3 py-2 rounded-lg font-medium text-white/70 transition-all duration-300 hover:text-white hover:bg-white/10"
                style={{ border: '1px solid rgba(255,255,255,0.2)' }}
                onClick={onStartNew}
              >
                🔄 Start New Analysis
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}


