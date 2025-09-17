import { useEffect, useState } from 'react';

interface Substep {
  label: string;
  status: string;
}
interface StatusStep {
  title: string;
  icon?: string;
  narrative?: string;
  substeps?: Substep[];
  animation?:
    | 'fade-in'
    | 'spinner'
    | 'typing-dots'
    | 'flicker'
    | 'gear-spin'
    | 'progress-bar'
    | 'glow-pulse';
  panel?: string;
  tabs?: string[];
}

interface StatusUpdaterProps {
  isComplete?: boolean;
  orchestratorResult?: {
    models_used?: string[];
    processing_time?: number;
    pattern_used?: string;
    final_result?: string;
  };
  selectedAddons?: Array<{ label: string }>;
  onViewResults?: () => void;
  onStartNew?: () => void;
  hasError?: boolean;
  errorStep?: number;
  errorMessage?: {
    detail: string;
    error_details?: {
      providers_present: string[];
      required_providers: string[];
    }
  } | null;
}

export default function StatusUpdater({
  isComplete = false,
  orchestratorResult,
  selectedAddons = [],
  onViewResults,
  onStartNew,
  hasError = false,
  errorStep = 0,
  errorMessage = null,
}: StatusUpdaterProps) {
  const [steps, setSteps] = useState<StatusStep[]>([]);
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    const load = async () => {
      try {
        const r = await fetch('/status_steps.json', { cache: 'no-store' });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const d = await r.json();
        setSteps(d as StatusStep[]);
      } catch (e) {
        console.error('Failed to load status steps', e);
      }
    };
    load();
  }, []);

  useEffect(() => {
    if (steps.length === 0) return;
    // If complete, jump to final step
    if (isComplete) {
      setIdx(steps.length - 1);
      return;
    }
    // If error, stop at the error step
    if (hasError && errorStep > 0) {
      setIdx(Math.min(errorStep, steps.length - 1));
      return;
    }
    const t = setTimeout(
      () => setIdx(i => Math.min(i + 1, steps.length - 1)),
      1500
    );
    return () => clearTimeout(t);
  }, [steps, idx, isComplete, hasError, errorStep]);

  if (steps.length === 0) return null;
  const s = steps[idx];

  const animClass =
    s.animation === 'spinner'
      ? 'animate-spin-slow'
      : s.animation === 'typing-dots'
        ? 'after:content-["…"] after:animate-pulse'
        : s.animation === 'flicker'
          ? 'animate-flicker'
          : s.animation === 'gear-spin'
            ? 'animate-spin'
            : s.animation === 'progress-bar'
              ? 'relative overflow-hidden'
              : s.animation === 'glow-pulse'
                ? 'animate-pulse-neon'
                : 'animate-fade-in';

  const borderColor =
    hasError && idx === errorStep ? 'border-red-500/50' : 'animate-border-hum';
  const glowColor =
    hasError && idx === errorStep
      ? 'from-red-500/10 via-transparent to-red-500/10'
      : 'from-cyan-500/5 via-transparent to-orange-500/5';

  return (
    <div
      className={`glass-strong rounded-xl p-6 border-2 ${borderColor} ${animClass} relative overflow-hidden`}
    >
      {/* Background accent glow */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${glowColor} pointer-events-none`}
      />

      {/* Content centered */}
      <div className="relative z-10 text-center">
        {/* Icon with glow effect */}
        <div className="text-3xl mb-3 inline-block">
          <span className="inline-block animate-bounce-subtle drop-shadow-[0_0_20px_rgba(255,102,0,0.6)]">
            {s.icon}
          </span>
        </div>

        {/* Title with gradient text */}
        <h3 className="text-lg font-bold tracking-wider uppercase bg-gradient-to-r from-cyan-400 to-orange-400 bg-clip-text text-transparent">
          {s.title}
        </h3>

        {/* Narrative with better spacing */}
        {s.narrative && (
          <p className="text-sm opacity-90 mt-3 max-w-md mx-auto leading-relaxed text-white/80">
            {s.narrative}
          </p>
        )}

        {hasError && errorMessage && (
          <div className="mt-4 p-3 bg-red-500/10 rounded-lg border border-red-500/30 text-white/80 text-xs">
            <p className="font-bold mb-1">Service Unavailable</p>
            <p>{errorMessage.detail}</p>
            {errorMessage.error_details && (
              <div className="mt-2 text-left">
                <p><strong>Providers Present:</strong> {errorMessage.error_details.providers_present.join(', ')}</p>
                <p><strong>Providers Required:</strong> {errorMessage.error_details.required_providers.join(', ')}</p>
              </div>
            )}
          </div>
        )}

        {/* Substeps as centered cards */}
        {s.substeps && (
          <div className="mt-4 grid grid-cols-2 gap-2 max-w-sm mx-auto">
            {s.substeps.map(ss => (
              <div
                key={ss.label}
                className="bg-white/5 rounded-lg p-2 border border-white/10"
              >
                <span className="text-xs opacity-70 block">{ss.label}</span>
                <span className="text-sm font-semibold text-cyan-400">
                  {ss.status}
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Enhanced progress bar */}
        {s.animation === 'progress-bar' && (
          <div className="mt-4 max-w-xs mx-auto">
            <div className="h-2 bg-white/10 rounded-full overflow-hidden backdrop-blur-sm">
              <div className="h-full bg-gradient-to-r from-cyan-400 to-orange-400 animate-[progressFill_1.5s_ease-in-out_forwards] shadow-[0_0_10px_rgba(255,102,0,0.5)]"></div>
            </div>
          </div>
        )}

        {/* Tabs as pills */}
        {s.tabs && (
          <div className="mt-4 flex flex-wrap gap-2 justify-center">
            {s.tabs.map(tab => (
              <span
                key={tab}
                className="px-3 py-1.5 text-xs font-medium border rounded-full border-white/20 bg-white/5 hover:bg-white/10 transition-colors"
              >
                {tab}
              </span>
            ))}
          </div>
        )}

        {/* Show completion stats and actions on final step */}
        {isComplete && idx === steps.length - 1 && orchestratorResult && (
          <>
            {/* Processing stats in cards */}
            <div className="grid grid-cols-3 gap-3 mt-6 mb-4">
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <div className="text-2xl mb-1">🤖</div>
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">
                  Models Used
                </div>
                <div className="text-[14px] font-bold text-green-300 mt-1">
                  {Array.isArray(orchestratorResult.models_used)
                    ? orchestratorResult.models_used.length
                    : '3'}
                </div>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <div className="text-2xl mb-1">⚡</div>
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">
                  Processing Time
                </div>
                <div className="text-[14px] font-bold text-blue-300 mt-1">
                  {typeof orchestratorResult.processing_time === 'number'
                    ? orchestratorResult.processing_time.toFixed(2)
                    : '1.32'}
                  s
                </div>
              </div>
              <div className="bg-white/5 rounded-lg p-3 text-center border border-white/10">
                <div className="text-2xl mb-1">🎯</div>
                <div className="text-[10px] font-semibold text-white/60 uppercase tracking-wider">
                  Pattern
                </div>
                <div className="text-[14px] font-bold text-purple-300 mt-1">
                  {orchestratorResult.pattern_used || 'Ultra'}
                </div>
              </div>
            </div>

            {/* Selected add-ons reminder */}
            {selectedAddons.length > 0 && (
              <div className="mb-4 p-3 bg-white/5 rounded-lg border border-white/10">
                <div className="text-[11px] font-semibold text-white/60 mb-2">
                  Selected Add-ons:
                </div>
                <div className="flex flex-wrap gap-2">
                  {selectedAddons.map((addon, idx) => (
                    <span
                      key={idx}
                      className="text-[10px] px-2 py-1 rounded-full bg-pink-500/20 text-pink-300 border border-pink-500/30"
                    >
                      {addon.label}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Action buttons */}
            <div className="space-y-2 mt-4">
              <button
                className="w-full px-4 py-3 rounded-lg font-semibold text-white transition-all duration-300 hover:scale-[1.02] active:scale-[0.98] relative group"
                style={{
                  background:
                    'linear-gradient(135deg, #00ff9f 0%, #00d4ff 100%)',
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
                style={{
                  border: '1px solid rgba(255,255,255,0.2)',
                }}
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
